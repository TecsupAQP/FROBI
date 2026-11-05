"""M8 on the real stack: Postgres (frobi_test), Redis (db 15) and the no-AI fallbacks."""

from collections.abc import AsyncIterator
from uuid import UUID

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


def _option(question: dict[str, object], text_: str) -> str:
    """Letter of the option with this text (letters are shuffled per question)."""
    options = question["options"]
    assert isinstance(options, list)
    return str(next(o["id"] for o in options if o["text"] == text_))


async def _adaptation(client: AsyncClient, auth: dict[str, str], fmt: str = "easy_read") -> str:
    response = await client.post(
        f"/api/v1/materials/{SAMPLE_ID}/adaptations", headers=auth, json={"format": fmt}
    )
    return str(response.json()["id"])


async def test_questions_then_a_wrong_and_a_right_answer(client: AsyncClient) -> None:
    auth = await _enter(client)
    adaptation_id = await _adaptation(client, auth, "real_example")

    generated = await client.post(f"/api/v1/adaptations/{adaptation_id}/questions", headers=auth)
    first = generated.json()[0]
    capacitive = _option(first, "Capacitivo")
    inductive = _option(first, "Inductivo")
    wrong = await client.post(
        f"/api/v1/questions/{first['id']}/answers", headers=auth, json={"option": inductive}
    )
    right = await client.post(
        f"/api/v1/questions/{first['id']}/answers", headers=auth, json={"option": capacitive}
    )

    assert generated.status_code == 201, generated.text
    assert len(generated.json()) == 3
    assert all("correct_option" not in q for q in generated.json())
    assert first["statement"] == "¿Qué sensor detecta una botella de plástico?"
    assert wrong.json()["is_correct"] is False
    assert wrong.json()["suggested_format"] == "easy_read"
    assert wrong.json()["correct_option"] == capacitive
    assert wrong.json()["used_help"] is True
    assert right.json()["is_correct"] is True
    assert right.json()["suggested_format"] is None


async def test_transfer_question_is_answered_without_help(client: AsyncClient) -> None:
    auth = await _enter(client)
    adaptation_id = await _adaptation(client, auth)

    question = await client.post(
        f"/api/v1/adaptations/{adaptation_id}/transfer-question", headers=auth
    )
    answer = await client.post(
        f"/api/v1/questions/{question.json()['id']}/answers",
        headers=auth,
        json={"option": _option(question.json(), "Inductivo")},
    )

    assert question.status_code == 201
    assert question.json()["kind"] == "transfer"
    assert answer.json()["used_help"] is False
    assert answer.json()["is_correct"] is True


async def test_my_own_notes_get_fill_in_the_blank_questions(client: AsyncClient) -> None:
    auth = await _enter(client)
    material = await client.post(
        "/api/v1/materials",
        headers=auth,
        json={
            "title": "Notas",
            "kind": "guide",
            "text": "El termopar mide temperatura mediante la unión de dos metales distintos. "
            "Un transmisor convierte la presión del fluido en una corriente eléctrica estable.",
        },
    )
    adaptation = await client.post(
        f"/api/v1/materials/{material.json()['id']}/adaptations",
        headers=auth,
        json={"format": "audio"},
    )

    generated = await client.post(
        f"/api/v1/adaptations/{adaptation.json()['id']}/questions", headers=auth
    )

    assert generated.status_code == 201, generated.text
    assert all("_____" in q["statement"] for q in generated.json())


async def test_privacy_and_errors(client: AsyncClient, test_settings: Settings) -> None:
    ana = await _enter(client, "Ana", class_code="SENSOR1")
    luis = await _enter(client, "Luis")
    adaptation_id = await _adaptation(client, ana)
    questions = (
        await client.post(f"/api/v1/adaptations/{adaptation_id}/questions", headers=ana)
    ).json()

    foreign_generate = await client.post(
        f"/api/v1/adaptations/{adaptation_id}/questions", headers=luis
    )
    foreign_answer = await client.post(
        f"/api/v1/questions/{questions[0]['id']}/answers", headers=luis, json={"option": "a"}
    )
    bad_option = await client.post(
        f"/api/v1/questions/{questions[0]['id']}/answers", headers=ana, json={"option": "z"}
    )
    mine = await client.post(
        f"/api/v1/questions/{questions[0]['id']}/answers", headers=ana, json={"option": "b"}
    )

    assert foreign_generate.status_code == 404
    assert foreign_answer.status_code == 404
    assert bad_option.status_code == 422
    assert bad_option.json()["code"] == "Comprehension.InvalidOption"
    assert mine.status_code == 200
    engine = create_async_engine(test_settings.database_url)
    async with engine.connect() as connection:
        class_ids = (
            await connection.execute(
                text("SELECT class_id FROM answers WHERE question_id = :q"),
                {"q": UUID(questions[0]["id"])},
            )
        ).scalars()
        assert set(class_ids) == {UUID("00000000-0000-4000-8000-0000000000c1")}
    await engine.dispose()
