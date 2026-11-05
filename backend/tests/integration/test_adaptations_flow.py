"""M4/M5 on the real stack: Postgres (frobi_test), Redis (db 15) and the fallback engine."""

from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from fakes.adaptations import ScriptedLlm
from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration

SAMPLE_ID = "00000000-0000-4000-8000-00000000a001"
EXAMPLE_CLASS_ID = UUID("00000000-0000-4000-8000-0000000000c1")


@pytest.fixture
async def app(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[FastAPI]:
    app = create_app(test_settings)
    yield app
    await app.state.redis.aclose()
    await app.state.engine.dispose()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


async def _enter(client: AsyncClient, alias: str, **extra: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions",
        json={"alias": alias, "career": "Mecatrónica", "role": "learner", **extra},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def test_without_a_provider_the_sample_gets_the_prewritten_answer(
    client: AsyncClient,
) -> None:
    auth = await _enter(client, "Ana")

    response = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=auth, json={"format": "real_example"}
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["fallback"] is True
    assert body["content"]["title"] == "Sensores en una línea de envasado de jugo"
    assert body["recipe"]["format"] == "real_example"
    assert body["prompt_text"].startswith("Contexto: Estudio el material «Guía de sensores")
    assert "sin IA" in body["ai_notice"]


async def test_my_own_material_is_adapted_by_rules_and_can_be_seen_again(
    client: AsyncClient,
) -> None:
    ana = await _enter(client, "Ana")
    luis = await _enter(client, "Luis")
    material = await client.post(
        "/api/v1/materials",
        headers=ana,
        json={"title": "Mis notas", "kind": "guide", "text": "## Termopar\nMide temperatura alta."},
    )

    created = await client.post(
        f"/api/v1/materials/{material.json()['id']}/adaptations",
        headers=ana,
        json={"format": "easy_read"},
    )
    again = await client.get(f"/api/v1/adaptations/{created.json()['id']}", headers=ana)
    theirs = await client.get(f"/api/v1/adaptations/{created.json()['id']}", headers=luis)
    luis_adapts_it = await client.post(
        f"/api/v1/materials/{material.json()['id']}/adaptations",
        headers=luis,
        json={"format": "easy_read"},
    )

    assert created.status_code == 201
    assert created.json()["content"]["sections"][0] == {
        "heading": "Termopar",
        "body": "Mide temperatura alta.",
        "items": [],
    }
    assert again.json() == created.json()
    assert theirs.status_code == 404
    assert luis_adapts_it.status_code == 404


async def test_the_active_class_is_stored_on_the_adaptation(
    client: AsyncClient, test_settings: Settings
) -> None:
    in_class = await _enter(client, "Ana", class_code="SENSOR1")
    outside = await _enter(client, "Luis")

    a = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=in_class, json={"format": "audio"}
    )
    b = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=outside, json={"format": "audio"}
    )

    engine = create_async_engine(test_settings.database_url)
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT id, class_id FROM adaptations"))
        rows = dict(result.all())
    await engine.dispose()
    assert rows[UUID(a.json()["id"])] == EXAMPLE_CLASS_ID
    assert rows[UUID(b.json()["id"])] is None


async def test_formats_suggest_according_to_the_wizard(client: AsyncClient) -> None:
    auth = await _enter(client, "Ana")
    before = await client.get("/api/v1/formats", headers=auth)
    await client.post(
        "/api/v1/me/onboarding",
        headers=auth,
        json={"who_uses": "self", "profiles": ["hearing"], "intro": "seen"},
    )
    after = await client.get("/api/v1/formats", headers=auth)

    assert [f["id"] for f in before.json() if f["suggested"]] == []
    assert [f["id"] for f in after.json() if f["suggested"]] == ["visual_map"]


async def test_with_a_provider_answers_are_cached_for_the_same_profile(
    app: FastAPI, client: AsyncClient
) -> None:
    llm = ScriptedLlm()
    app.state.llm = llm
    ana = await _enter(client, "Ana")
    luis = await _enter(client, "Luis")

    first = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=ana, json={"format": "easy_read"}
    )
    second = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=luis, json={"format": "easy_read"}
    )

    assert first.json()["fallback"] is False
    assert first.json()["content"]["title"] == "Versión de la IA"
    assert second.json()["content"] == first.json()["content"]
    assert llm.calls == 1


async def test_a_slow_provider_still_answers_within_the_cap(
    app: FastAPI, client: AsyncClient, test_settings: Settings
) -> None:
    app.state.llm = ScriptedLlm(delay=5)
    app.state.settings = test_settings.model_copy(update={"llm_timeout_seconds": 0.2})
    auth = await _enter(client, "Ana")

    response = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=auth, json={"format": "visual_map"}
    )

    assert response.status_code == 201
    assert response.json()["fallback"] is True
