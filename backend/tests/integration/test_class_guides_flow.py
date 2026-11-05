"""Guías de la clase en el stack real: de estudio (evaluación final) o con tareas, y su avance."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration

GUIA = (
    "## Motores de corriente continua\n"
    "Un motor de corriente continua convierte energía eléctrica en movimiento. "
    "Su velocidad se controla cambiando el voltaje que recibe. "
    "Se usa en juguetes, ventiladores pequeños y robots.\n\n"
    "## Motores de inducción\n"
    "El motor de inducción trifásico es robusto y casi no necesita mantenimiento. "
    "Funciona con corriente alterna y mueve bombas, fajas y compresores en la industria. "
    "Su velocidad depende de la frecuencia de la red eléctrica.\n\n"
    "## Servomotores\n"
    "Un servomotor controla con precisión la posición de su eje. "
    "Tiene un sensor que informa la posición a un controlador. "
    "Se usa en brazos robóticos y en máquinas de control numérico."
)


@pytest.fixture
async def client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


async def _enter(
    client: AsyncClient, alias: str, role: str = "learner", **extra: str
) -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions",
        json={"alias": alias, "career": "Mecatrónica", "role": role, **extra},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def _class(client: AsyncClient, teacher: dict[str, str]) -> tuple[str, str]:
    created = await client.post(
        "/api/v1/classes",
        headers=teacher,
        json={"name": "Máquinas 2026", "subject": "Electricidad"},
    )
    assert created.status_code == 201, created.text
    return created.json()["id"], created.json()["invite_code"]


async def _upload(
    client: AsyncClient,
    teacher: dict[str, str],
    class_id: str,
    title: str,
    mode: str,
    tasks: list[str] | None = None,
) -> dict[str, object]:
    form: dict[str, str | list[str]] = {"title": title, "text": GUIA, "mode": mode}
    if tasks:
        form["tasks"] = tasks
    response = await client.post(
        f"/api/v1/classes/{class_id}/materials", headers=teacher, data=form
    )
    assert response.status_code == 201, response.text
    body: dict[str, object] = response.json()
    return body


async def test_a_guide_with_tasks_tracks_each_student(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe Rosa", role="teacher")
    class_id, code = await _class(client, teacher)
    guide = await _upload(
        client,
        teacher,
        class_id,
        "Motores",
        "tasks",
        ["Explica qué hace un motor", "Da un ejemplo"],
    )
    ana = await _enter(client, "Ana", class_code=code)

    listed = (await client.get(f"/api/v1/classes/{class_id}/materials", headers=ana)).json()
    tasks = listed[0]["tasks"]
    adaptation = await client.post(
        f"/api/v1/materials/{guide['id']}/adaptations", headers=ana, json={"format": "easy_read"}
    )
    attempt = await client.post(
        "/api/v1/help-attempts",
        headers=ana,
        json={"adaptation_id": adaptation.json()["id"], "task_ref": tasks[0]["task_ref"]},
    )
    await client.post(
        f"/api/v1/help-attempts/{attempt.json()['id']}/own-answer",
        headers=ana,
        json={"answer": "Convierte energía eléctrica en movimiento."},
    )
    mine = await client.get(f"/api/v1/classes/{class_id}/guides/my-progress", headers=ana)
    panel = await client.get(f"/api/v1/classes/{class_id}/guides/progress", headers=teacher)

    assert listed[0]["mode"] == "tasks"
    assert [t["statement"] for t in tasks] == ["Explica qué hace un motor", "Da un ejemplo"]
    assert mine.status_code == 200, mine.text
    assert mine.json()[0]["completion"] == 50
    assert mine.json()[0]["done_task_ids"] == [tasks[0]["id"]]
    assert panel.json()[0]["students"] == [
        {"person_id": panel.json()[0]["students"][0]["person_id"], "alias": "Ana", "completion": 50}
    ]


async def test_a_study_guide_is_measured_by_its_final_evaluation(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe Rosa", role="teacher")
    class_id, code = await _class(client, teacher)
    guide = await _upload(client, teacher, class_id, "Motores", "study")
    ana = await _enter(client, "Ana", class_code=code)

    before = await client.get(f"/api/v1/classes/{class_id}/guides/my-progress", headers=ana)
    adaptation = await client.post(
        f"/api/v1/materials/{guide['id']}/adaptations", headers=ana, json={"format": "easy_read"}
    )
    questions = await client.post(
        f"/api/v1/adaptations/{adaptation.json()['id']}/questions", headers=ana
    )
    assert questions.status_code == 201, questions.text
    first = questions.json()[0]
    await client.post(
        f"/api/v1/questions/{first['id']}/answers",
        headers=ana,
        json={"option": first["options"][0]["id"]},
    )
    after = (await client.get(f"/api/v1/classes/{class_id}/guides/my-progress", headers=ana)).json()

    assert before.json()[0] == {
        "material_id": guide["id"],
        "mode": "study",
        "completion": 0,
        "done_task_ids": [],
        "evaluation": None,
    }
    assert after[0]["evaluation"]["total"] == len(questions.json())
    assert after[0]["completion"] == round(
        100 * after[0]["evaluation"]["correct"] / after[0]["evaluation"]["total"]
    )


async def test_the_teacher_changes_the_guide_and_keeps_unchanged_tasks(
    client: AsyncClient,
) -> None:
    teacher = await _enter(client, "Profe Rosa", role="teacher")
    class_id, _ = await _class(client, teacher)
    guide = await _upload(client, teacher, class_id, "Motores", "tasks", ["Tarea A"])
    first_id = guide["tasks"][0]["id"]  # type: ignore[index]

    edited = await client.put(
        f"/api/v1/classes/{class_id}/materials/{guide['id']}/guide",
        headers=teacher,
        json={"mode": "tasks", "tasks": ["Tarea A", "Tarea B"]},
    )
    to_study = await client.put(
        f"/api/v1/classes/{class_id}/materials/{guide['id']}/guide",
        headers=teacher,
        json={"mode": "study", "tasks": []},
    )

    assert edited.status_code == 200, edited.text
    assert [t["statement"] for t in edited.json()["tasks"]] == ["Tarea A", "Tarea B"]
    assert edited.json()["tasks"][0]["id"] == first_id
    assert to_study.json() == {"material_id": guide["id"], "mode": "study", "tasks": []}


async def test_guide_rules_and_permissions(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe Rosa", role="teacher")
    other_teacher = await _enter(client, "Profe Luis", role="teacher")
    class_id, code = await _class(client, teacher)
    guide = await _upload(client, teacher, class_id, "Motores", "study")
    ana = await _enter(client, "Ana", class_code=code)
    outsider = await _enter(client, "Beto")

    no_tasks = await client.put(
        f"/api/v1/classes/{class_id}/materials/{guide['id']}/guide",
        headers=teacher,
        json={"mode": "tasks", "tasks": []},
    )
    by_student = await client.put(
        f"/api/v1/classes/{class_id}/materials/{guide['id']}/guide",
        headers=ana,
        json={"mode": "study", "tasks": []},
    )
    by_other = await client.get(
        f"/api/v1/classes/{class_id}/guides/progress", headers=other_teacher
    )
    outsider_progress = await client.get(
        f"/api/v1/classes/{class_id}/guides/my-progress", headers=outsider
    )

    assert no_tasks.status_code == 422
    assert no_tasks.json()["code"] == "Classrooms.InvalidGuide"
    assert by_student.status_code in (403, 404)
    assert by_other.status_code == 404
    assert outsider_progress.status_code == 404
