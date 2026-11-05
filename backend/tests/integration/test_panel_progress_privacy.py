"""Teacher panel (M12), personal progress (M11) and the privacy rule (RNF16) on the real stack.

RNF16: what a student does outside the class — before joining, after leaving, or in another
class — must never reach the teacher's panel or the student detail.
"""

from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration

SAMPLE = "00000000-0000-4000-8000-00000000a001"


@pytest.fixture
async def client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


async def _enter(client: AsyncClient, alias: str, role: str = "learner") -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions", json={"alias": alias, "career": "Mecatrónica", "role": role}
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def _new_class(client: AsyncClient, teacher: dict[str, str], name: str) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/classes", headers=teacher, json={"name": name, "subject": "Sensores"}
    )
    body: dict[str, Any] = response.json()
    return body


async def _study(client: AsyncClient, auth: dict[str, str], fmt: str, *, wrong: bool) -> None:
    """One adaptation, one help step and one answer (right or wrong)."""
    adaptation = await client.post(
        f"/api/v1/materials/{SAMPLE}/adaptations", headers=auth, json={"format": fmt}
    )
    adaptation_id = adaptation.json()["id"]
    attempt = await client.post(
        "/api/v1/help-attempts",
        headers=auth,
        json={"adaptation_id": adaptation_id, "task_ref": "tarea"},
    )
    await client.post(
        f"/api/v1/help-attempts/{attempt.json()['id']}/steps",
        headers=auth,
        json={"step": "hint_1"},
    )
    question = (
        await client.post(f"/api/v1/adaptations/{adaptation_id}/questions", headers=auth)
    ).json()[0]
    correct = next(o["id"] for o in question["options"] if o["text"] == "Capacitivo")
    option = next(o["id"] for o in question["options"] if o["id"] != correct) if wrong else correct
    await client.post(
        f"/api/v1/questions/{question['id']}/answers", headers=auth, json={"option": option}
    )


async def test_an_empty_class_shows_flagged_sample_data(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe", "teacher")
    classroom = await _new_class(client, teacher, "Vacía")

    panel = await client.get(f"/api/v1/classes/{classroom['id']}/dashboard", headers=teacher)

    assert panel.status_code == 200
    assert panel.json()["sample_data"] is True
    assert all("(ejemplo)" in s["alias"] for s in panel.json()["students"])


async def test_the_panel_only_counts_activity_done_inside_the_class(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe", "teacher")
    classroom = await _new_class(client, teacher, "Privada")
    other = await _new_class(client, teacher, "Otra")
    ana = await _enter(client, "Ana")
    luis = await _enter(client, "Luis")

    # Outside any class: never on the panel.
    await _study(client, ana, "audio", wrong=True)
    # Inside the class.
    await client.post("/api/v1/classes/join", headers=ana, json={"code": classroom["invite_code"]})
    await client.post("/api/v1/classes/join", headers=luis, json={"code": classroom["invite_code"]})
    await _study(client, ana, "easy_read", wrong=False)
    await _study(client, luis, "visual_map", wrong=True)
    # In another class: never on this panel.
    await client.post("/api/v1/classes/join", headers=luis, json={"code": other["invite_code"]})
    await _study(client, luis, "real_example", wrong=True)
    # After leaving: never on the panel.
    await client.delete("/api/v1/me/membership", headers=ana)
    await _study(client, ana, "audio", wrong=True)

    panel = (
        await client.get(f"/api/v1/classes/{classroom['id']}/dashboard", headers=teacher)
    ).json()
    detail_ana = (
        await client.get(
            f"/api/v1/classes/{classroom['id']}/students/{(await _id(client, ana))}",
            headers=teacher,
        )
    ).json()

    assert panel["sample_data"] is False
    assert {f["format"] for f in panel["top_formats"]} == {"easy_read", "visual_map"}
    assert panel["ai_usage"]["help_requests"] == 2
    assert detail_ana["total_answers"] == 1
    assert detail_ana["correct_answers"] == 1
    assert detail_ana["preferred_format"] == "easy_read"
    assert detail_ana["help_by_step"] == [{"step": "hint_1", "count": 1}]


async def _id(client: AsyncClient, auth: dict[str, str]) -> str:
    return str((await client.get("/api/v1/me", headers=auth)).json()["person"]["id"])


async def test_alerts_are_written_as_help(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe", "teacher")
    classroom = await _new_class(client, teacher, "Alertas")
    luis = await _enter(client, "Luis")
    rosa = await _enter(client, "Rosa")
    for student in (luis, rosa):
        await client.post(
            "/api/v1/classes/join", headers=student, json={"code": classroom["invite_code"]}
        )
    for _ in range(3):
        await _study(client, luis, "easy_read", wrong=True)

    panel = (
        await client.get(f"/api/v1/classes/{classroom['id']}/dashboard", headers=teacher)
    ).json()
    rows = {s["alias"]: s for s in panel["students"]}

    assert rows["Luis"]["progress_label"] == "Necesita apoyo"
    assert {a["code"] for a in rows["Luis"]["alerts"]} == {"stuck_on_hint_1", "needs_review"}
    assert rows["Rosa"]["alerts"][0]["text"] == "Todavía no empezó"
    assert panel["most_failed_questions"][0]["fail_rate"] == 1.0


async def test_only_the_teacher_of_the_class_sees_the_panel(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe", "teacher")
    other_teacher = await _enter(client, "Otro", "teacher")
    student = await _enter(client, "Ana")
    classroom = await _new_class(client, teacher, "Mía")

    as_student = await client.get(f"/api/v1/classes/{classroom['id']}/dashboard", headers=student)
    as_other = await client.get(
        f"/api/v1/classes/{classroom['id']}/dashboard", headers=other_teacher
    )

    assert as_student.status_code == 403
    assert as_other.status_code == 404


async def test_progress_includes_everything_the_person_did(client: AsyncClient) -> None:
    ana = await _enter(client, "Ana")
    empty = (await client.get("/api/v1/me/progress", headers=ana)).json()
    await _study(client, ana, "easy_read", wrong=False)
    await _study(client, ana, "easy_read", wrong=False)
    await client.post(
        "/api/v1/prompt-evaluations", headers=ana, json={"text": "explicame sensores"}
    )
    await client.post(
        "/api/v1/prompt-evaluations",
        headers=ana,
        json={"text": "Soy de primer año, explícame los sensores en una tabla para mi examen."},
    )

    progress = (await client.get("/api/v1/me/progress", headers=ana)).json()
    journey = (await client.get("/api/v1/me/journey-summary", headers=ana)).json()

    assert empty["has_data"] is False
    assert empty["message"].startswith("Todavía no hay actividad")
    assert progress["has_data"] is True
    assert progress["formats_used"] == [{"format": "easy_read", "count": 2}]
    assert progress["accuracy_by_format"] == [{"format": "easy_read", "correct": 2, "total": 2}]
    assert len(progress["prompt_scores"]) == 2
    assert progress["message"].startswith("Aciertas más con lectura fácil")
    assert journey["favorite_format"] == "easy_read"
    assert journey["learned_recipe"]["format"] == "easy_read"
    assert journey["best_prompt_score"] >= progress["prompt_scores"][0]["total"]
