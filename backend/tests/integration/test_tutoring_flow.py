"""M6 on the real stack: the ladder over HTTP, Postgres row locks and the DB safety net."""

import asyncio
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration

SAMPLE_ID = "00000000-0000-4000-8000-00000000a001"
TASK = "¿Qué sensor detecta una botella de plástico?"


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


async def _attempt(client: AsyncClient, auth: dict[str, str]) -> str:
    adaptation = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=auth, json={"format": "easy_read"}
    )
    attempt = await client.post(
        "/api/v1/help-attempts",
        headers=auth,
        json={"adaptation_id": adaptation.json()["id"], "task_ref": TASK},
    )
    assert attempt.status_code == 201, attempt.text
    return str(attempt.json()["id"])


async def _step(client: AsyncClient, auth: dict[str, str], attempt_id: str, step: str):  # type: ignore[no-untyped-def]
    return await client.post(
        f"/api/v1/help-attempts/{attempt_id}/steps", headers=auth, json={"step": step}
    )


async def test_the_full_ladder(client: AsyncClient) -> None:
    auth = await _enter(client)
    attempt_id = await _attempt(client, auth)

    skip = await _step(client, auth, attempt_id, "hint_2")
    locked = await _step(client, auth, attempt_id, "final")
    hint_1 = await _step(client, auth, attempt_id, "hint_1")
    hint_2 = await _step(client, auth, attempt_id, "hint_2")
    sbs = await _step(client, auth, attempt_id, "step_by_step")
    still_locked = await _step(client, auth, attempt_id, "final")
    own = await client.post(
        f"/api/v1/help-attempts/{attempt_id}/own-answer",
        headers=auth,
        json={"answer": "El capacitivo, detecta plásticos", "self_check": ["Releí la guía"]},
    )
    final = await _step(client, auth, attempt_id, "final")
    state = await client.get(f"/api/v1/help-attempts/{attempt_id}", headers=auth)

    assert skip.status_code == 409
    assert skip.json()["code"] == "Tutoring.StepOutOfOrder"
    assert locked.status_code == 409
    assert locked.json()["code"] == "Tutoring.FinalLocked"
    assert hint_1.json()["attempt"]["help_label"] == "Nivel 1, con una pista"
    assert "«Sensores capacitivos»" in hint_1.json()["content"]
    assert hint_1.json()["fallback"] is True
    assert hint_2.json()["attempt"]["next_step"] == "step_by_step"
    assert sbs.json()["attempt"]["next_step"] == "final"
    assert still_locked.json()["code"] == "Tutoring.FinalLocked"
    assert own.status_code == 200
    assert own.json()["matching_passages"]
    assert own.json()["attempt"]["solved_without_ai"] is False
    assert final.status_code == 200
    assert final.json()["attempt"]["max_step"] == "final"
    assert state.json()["help_label"] == "Nivel 4, con la respuesta"


async def test_solved_without_ai_before_any_hint(client: AsyncClient) -> None:
    auth = await _enter(client)
    attempt_id = await _attempt(client, auth)

    own = await client.post(
        f"/api/v1/help-attempts/{attempt_id}/own-answer",
        headers=auth,
        json={"answer": "Un sensor capacitivo, porque detecta plásticos y líquidos"},
    )

    assert own.json()["attempt"]["solved_without_ai"] is True
    assert own.json()["attempt"]["help_level"] == 0
    assert "capacitivos" in own.json()["matching_passages"][0]["text"]


async def test_a_double_click_on_a_step_only_advances_once(client: AsyncClient) -> None:
    auth = await _enter(client)
    attempt_id = await _attempt(client, auth)

    first, second = await asyncio.gather(
        _step(client, auth, attempt_id, "hint_1"), _step(client, auth, attempt_id, "hint_1")
    )

    assert first.status_code == second.status_code == 200
    state = await client.get(f"/api/v1/help-attempts/{attempt_id}", headers=auth)
    assert state.json()["max_step"] == "hint_1"


async def test_attempts_are_private(client: AsyncClient) -> None:
    ana = await _enter(client, "Ana")
    luis = await _enter(client, "Luis")
    attempt_id = await _attempt(client, ana)

    assert (
        await client.get(f"/api/v1/help-attempts/{attempt_id}", headers=luis)
    ).status_code == 404
    assert (await _step(client, luis, attempt_id, "hint_1")).status_code == 404
    unknown = await client.post(
        "/api/v1/help-attempts",
        headers=luis,
        json={"adaptation_id": str(uuid4()), "task_ref": "x"},
    )
    assert unknown.status_code == 404


async def test_the_class_is_stored_on_the_attempt(
    client: AsyncClient, test_settings: Settings
) -> None:
    auth = await _enter(client, class_code="SENSOR1")
    attempt_id = await _attempt(client, auth)

    engine = create_async_engine(test_settings.database_url)
    async with engine.connect() as connection:
        class_id = await connection.scalar(
            text("SELECT class_id FROM help_attempts WHERE id = :id"), {"id": UUID(attempt_id)}
        )
    await engine.dispose()
    assert class_id == UUID("00000000-0000-4000-8000-0000000000c1")


async def test_the_database_refuses_final_without_own_answer(db_session: AsyncSession) -> None:
    person, adaptation = uuid4(), uuid4()
    await db_session.execute(
        text(
            "INSERT INTO persons (id, alias, career, role, configured_by, created_at) "
            "VALUES (:p, 'Ana', 'X', 'learner', 'self', now())"
        ),
        {"p": person},
    )
    await db_session.execute(
        text(
            "INSERT INTO adaptations (id, material_id, person_id, format, content, recipe, "
            "fallback, created_at) VALUES (:a, :m, :p, 'audio', '{}', '{}', true, now())"
        ),
        {"a": adaptation, "m": uuid4(), "p": person},
    )
    with pytest.raises(IntegrityError):
        await db_session.execute(
            text(
                "INSERT INTO help_attempts (id, person_id, adaptation_id, task_ref, max_step, "
                "self_check, solved_without_ai, created_at) "
                "VALUES (:id, :p, :a, 't', 'final', '[]', false, now())"
            ),
            {"id": uuid4(), "p": person, "a": adaptation},
        )
