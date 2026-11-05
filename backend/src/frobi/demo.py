"""Demo seed: two students with activity in the demo class, and sessions to enter as each one.

    uv run python -m frobi.demo            # seed once, then just print fresh sessions
    uv run python -m frobi.demo --reset    # remove the demo students and seed again

Migration 0010 already creates the class «Sensores 2026-II» (code SENSOR1) and its teacher.
This adds class content and two students, «Ana (demo)» and «Luis (demo)», whose activity goes
through the real API, so the teacher panel shows real numbers. That panel is always flagged
``sample_data`` (RNF12). Nobody can create a session for an existing person through the API, so
the script also prints a token for the demo teacher.

Needs Postgres and Redis running and the migrations applied.
"""

import argparse
import asyncio
from dataclasses import dataclass
from uuid import UUID

from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from frobi.main import create_app
from frobi.modules.classrooms.domain import DEMO_CLASS_ID, DEMO_STUDENTS, DEMO_TEACHER_ID
from frobi.modules.identity.infrastructure import RedisSessionStore
from frobi.shared.infrastructure import get_settings

API = "/api/v1"
SAMPLE_GUIDE = "00000000-0000-4000-8000-00000000a001"
CLASS_CONTENT = (
    "Práctica 3 · Sensores de proximidad\n\n"
    "Los sensores inductivos detectan metales sin contacto. Su alcance depende del tamaño de "
    "la bobina y suele ir de 2 a 40 mm.\n\n"
    "Los sensores capacitivos detectan metales y también materiales no metálicos, como agua, "
    "plástico o madera, porque reaccionan al cambio de capacitancia.\n\n"
    "Tarea: elige el sensor adecuado para detectar el nivel de agua en un tanque de plástico y "
    "justifica tu elección con la guía."
)


@dataclass(frozen=True, slots=True)
class DemoPerson:
    alias: str
    token: str


async def _enter(client: AsyncClient, alias: str) -> tuple[UUID, str]:
    response = await client.post(
        f"{API}/sessions",
        json={"alias": alias, "career": "Mecatrónica", "role": "learner", "class_code": "SENSOR1"},
    )
    response.raise_for_status()
    body = response.json()
    return UUID(body["person"]["id"]), body["token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _study(client: AsyncClient, token: str, fmt: str, *, right: bool, hints: int) -> None:
    """Adapt the sample guide, ask for ``hints`` steps of help and answer its first question."""
    auth = _auth(token)
    adaptation = (
        await client.post(
            f"{API}/materials/{SAMPLE_GUIDE}/adaptations", headers=auth, json={"format": fmt}
        )
    ).json()
    attempt = (
        await client.post(
            f"{API}/help-attempts",
            headers=auth,
            json={"adaptation_id": adaptation["id"], "task_ref": "practica-3"},
        )
    ).json()
    for step in ("hint_1", "hint_2", "partial")[:hints]:
        await client.post(
            f"{API}/help-attempts/{attempt['id']}/steps", headers=auth, json={"step": step}
        )
    questions = (
        await client.post(f"{API}/adaptations/{adaptation['id']}/questions", headers=auth)
    ).json()
    question = questions[0]
    correct = next(o["id"] for o in question["options"] if o["text"] == "Capacitivo")
    option = correct if right else next(o["id"] for o in question["options"] if o["id"] != correct)
    await client.post(
        f"{API}/questions/{question['id']}/answers", headers=auth, json={"option": option}
    )


async def _solve_without_ai(client: AsyncClient, token: str) -> None:
    auth = _auth(token)
    adaptation = (
        await client.post(
            f"{API}/materials/{SAMPLE_GUIDE}/adaptations",
            headers=auth,
            json={"format": "easy_read"},
        )
    ).json()
    attempt = (
        await client.post(
            f"{API}/help-attempts",
            headers=auth,
            json={"adaptation_id": adaptation["id"], "task_ref": "practica-3-tanque"},
        )
    ).json()
    await client.post(
        f"{API}/help-attempts/{attempt['id']}/own-answer",
        headers=auth,
        json={
            "answer": "Un sensor capacitivo, porque detecta el agua a través del plástico.",
            "self_check": ["Lo comparé con la guía"],
        },
    )


async def _prompt(client: AsyncClient, token: str, prompt: str) -> None:
    await client.post(
        f"{API}/prompt-evaluations",
        headers=_auth(token),
        json={"text": prompt, "material_id": SAMPLE_GUIDE},
    )


async def _seed(client: AsyncClient, teacher_token: str) -> list[DemoPerson]:
    teacher = _auth(teacher_token)
    upload = await client.post(
        f"{API}/classes/{DEMO_CLASS_ID}/materials",
        headers=teacher,
        data={"title": "Práctica 3 · Sensores de proximidad", "text": CLASS_CONTENT},
    )
    upload.raise_for_status()

    _, ana = await _enter(client, DEMO_STUDENTS["ana"])
    await _prompt(client, ana, "Explícame los sensores")
    await _study(client, ana, "easy_read", right=True, hints=1)
    await _study(client, ana, "easy_read", right=True, hints=0)
    await _solve_without_ai(client, ana)
    await _prompt(
        client,
        ana,
        "Estudio Mecatrónica y tengo que entender la diferencia entre sensores inductivos y "
        "capacitivos de mi guía. Soy principiante: explícamelo en lectura fácil con un ejemplo "
        "de la planta y una tabla corta.",
    )

    _, luis = await _enter(client, DEMO_STUDENTS["luis"])
    for _ in range(3):
        await _study(client, luis, "visual_map", right=False, hints=1)
    await _prompt(client, luis, "Hazme la tarea de sensores")
    return [DemoPerson(DEMO_STUDENTS["ana"], ana), DemoPerson(DEMO_STUDENTS["luis"], luis)]


async def main(reset: bool) -> None:
    app = create_app(get_settings())
    sessions = RedisSessionStore(app.state.redis)
    try:
        async with app.state.session_factory() as db:
            if reset:
                await db.execute(
                    text(
                        "DELETE FROM persons WHERE id IN (SELECT person_id FROM memberships "
                        "WHERE class_id = :c AND person_id IS NOT NULL) AND id <> :t"
                    ),
                    {"c": DEMO_CLASS_ID, "t": DEMO_TEACHER_ID},
                )
                await db.execute(
                    text("DELETE FROM materials WHERE class_id = :c"), {"c": DEMO_CLASS_ID}
                )
                await db.commit()
            rows = (
                await db.execute(
                    text(
                        "SELECT person_id, alias FROM memberships WHERE class_id = :c "
                        "AND status = 'joined' AND person_id IS NOT NULL ORDER BY joined_at"
                    ),
                    {"c": DEMO_CLASS_ID},
                )
            ).all()

        teacher_token = await sessions.create(DEMO_TEACHER_ID)
        if rows:
            students = [DemoPerson(alias, await sessions.create(pid)) for pid, alias in rows]
            print("La clase demo ya tiene estudiantes; solo se crearon sesiones nuevas.")
            print("Para empezar de cero: uv run python -m frobi.demo --reset\n")
        else:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://demo") as client:
                students = await _seed(client, teacher_token)
            print("Clase demo lista: contenido de clase, 2 estudiantes y su actividad.\n")
    finally:
        await app.state.redis.aclose()
        await app.state.engine.dispose()

    print("Clase: Sensores 2026-II · código SENSOR1")
    print(f"Panel: GET {API}/classes/{DEMO_CLASS_ID}/dashboard\n")
    print("Sesiones (Authorization: Bearer <token>, válidas 30 días):")
    print(f"  Docente demo  {teacher_token}")
    for student in students:
        print(f"  {student.alias:<13} {student.token}")
    print(
        f"\nDesde el front (sin copiar tokens): POST {API}/sessions/demo con "
        '{"who": "teacher"}, "ana" o "luis".'
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--reset", action="store_true", help="borra los estudiantes demo y siembra de nuevo"
    )
    asyncio.run(main(parser.parse_args().reset))
