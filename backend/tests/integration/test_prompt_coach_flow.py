"""M7 on the real stack: Postgres (frobi_test), Redis (db 15) and the no-AI fallbacks."""

from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration

SAMPLE_ID = "00000000-0000-4000-8000-00000000a001"


@pytest.fixture
async def client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


async def _enter(client: AsyncClient, alias: str = "Ana", **extra: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions",
        json={"alias": alias, "career": "Mecatrónica", "role": "learner", **extra},
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def test_evaluate_a_vague_prompt_then_compare(client: AsyncClient) -> None:
    auth = await _enter(client)

    evaluated = await client.post(
        "/api/v1/prompt-evaluations",
        headers=auth,
        json={"text": "explicame sensores", "material_id": SAMPLE_ID},
    )
    body = evaluated.json()
    compared = await client.post(f"/api/v1/prompt-evaluations/{body['id']}/compare", headers=auth)

    assert evaluated.status_code == 201, evaluated.text
    assert [s["piece"] for s in body["scores"]] == ["context", "level", "format", "goal"]
    assert body["missing_piece"] == "context"
    assert body["autonomy_level"] == 1
    assert body["suggestion"].startswith("Lo que más falta es el contexto.")
    assert "«Guía de sensores industriales»" in body["improved_text"]
    assert compared.status_code == 200
    assert compared.json()["fallback"] is True
    assert compared.json()["original"]["prompt"] == "explicame sensores"
    assert compared.json()["improved"]["output"].startswith("•")


async def test_a_complete_prompt_reaches_autonomy_3(client: AsyncClient) -> None:
    auth = await _enter(client)

    response = await client.post(
        "/api/v1/prompt-evaluations",
        headers=auth,
        json={
            "text": "Soy estudiante de primer año y estoy leyendo la guía de sensores. "
            "Explícame los capacitivos para preparar mi examen, con palabras simples, "
            "en una tabla."
        },
    )

    assert response.json()["missing_piece"] is None
    assert response.json()["autonomy_label"] == "Nivel 3: armas la receta completa"


async def test_evaluations_are_private_and_store_the_class(
    client: AsyncClient, test_settings: Settings
) -> None:
    ana = await _enter(client, "Ana", class_code="SENSOR1")
    luis = await _enter(client, "Luis")
    created = await client.post(
        "/api/v1/prompt-evaluations", headers=ana, json={"text": "dame un resumen"}
    )

    other = await client.post(
        f"/api/v1/prompt-evaluations/{created.json()['id']}/compare", headers=luis
    )
    foreign_material = await client.post(
        "/api/v1/prompt-evaluations",
        headers=luis,
        json={"text": "x", "material_id": str(uuid4())},
    )

    assert other.status_code == 404
    assert foreign_material.status_code == 404
    engine = create_async_engine(test_settings.database_url)
    async with engine.connect() as connection:
        row = (
            await connection.execute(
                text(
                    "SELECT class_id, total, autonomy_level FROM prompt_evaluations WHERE id = :id"
                ),
                {"id": UUID(created.json()["id"])},
            )
        ).one()
    await engine.dispose()
    assert row.class_id == UUID("00000000-0000-4000-8000-0000000000c1")
    assert 0 <= row.total <= 16
    assert row.autonomy_level == 1


async def test_a_blank_prompt_is_422(client: AsyncClient) -> None:
    auth = await _enter(client)

    response = await client.post("/api/v1/prompt-evaluations", headers=auth, json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["code"] == "PromptCoach.EmptyPrompt"
