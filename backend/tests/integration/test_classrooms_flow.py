"""M12 on the real stack: a teacher's class, invitations, joining by code, one class at a time."""

from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration

DEMO_CLASS = "00000000-0000-4000-8000-0000000000c1"


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


async def test_the_demo_class_exists_from_the_first_run(client: AsyncClient) -> None:
    auth = await _enter(client, "Ana", class_code="sensor1")

    me = await client.get("/api/v1/me", headers=auth)
    detail = await client.get(f"/api/v1/classes/{DEMO_CLASS}", headers=auth)

    assert me.json()["membership"]["class_name"] == "Sensores 2026-II"
    assert detail.json()["invite_code"] == "SENSOR1"


async def test_teacher_creates_invites_and_students_join(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe Rosa", role="teacher")
    created = await client.post(
        "/api/v1/classes",
        headers=teacher,
        json={"name": "Control 2026", "subject": "Automatización", "tasks": ["Informe"]},
    )
    class_id, code = created.json()["id"], created.json()["invite_code"]
    invited = await client.post(
        f"/api/v1/classes/{class_id}/invitations",
        headers=teacher,
        json={"aliases": ["Ana", "Luis"]},
    )

    ana = await _enter(client, "Ana", class_code=code)
    luis = await _enter(client, "Luis")
    joined_later = await client.post("/api/v1/classes/join", headers=luis, json={"code": code})
    members = await client.get(f"/api/v1/classes/{class_id}/members", headers=teacher)
    ana_me = await client.get("/api/v1/me", headers=ana)

    assert created.status_code == 201, created.text
    assert len(code) == 6
    assert [m["status"] for m in invited.json()] == ["invited", "invited"]
    assert joined_later.json() == {
        "class_id": class_id,
        "class_name": "Control 2026",
        "status": "joined",
    }
    assert {(m["alias"], m["status"]) for m in members.json()["members"]} == {
        ("Ana", "joined"),
        ("Luis", "joined"),
    }
    assert ana_me.json()["membership"]["class_id"] == class_id


async def test_permissions(client: AsyncClient) -> None:
    teacher = await _enter(client, "Profe", role="teacher")
    other_teacher = await _enter(client, "Otro profe", role="teacher")
    student = await _enter(client, "Ana")
    created = await client.post(
        "/api/v1/classes", headers=teacher, json={"name": "Mía", "subject": "Física"}
    )
    class_id = created.json()["id"]

    student_creates = await client.post(
        "/api/v1/classes", headers=student, json={"name": "X", "subject": "Y"}
    )
    other_sees_members = await client.get(
        f"/api/v1/classes/{class_id}/members", headers=other_teacher
    )
    outsider_sees_class = await client.get(f"/api/v1/classes/{class_id}", headers=student)
    bad_code = await client.post("/api/v1/classes/join", headers=student, json={"code": "ZZZZZZ"})

    assert student_creates.status_code == 403
    assert student_creates.json()["code"] == "Identity.Forbidden"
    assert other_sees_members.status_code == 404
    assert outsider_sees_class.status_code == 404
    assert bad_code.status_code == 422
    assert bad_code.json()["code"] == "Classrooms.InvalidCode"


async def test_activity_follows_the_class_the_person_is_in(
    client: AsyncClient, test_settings: Settings
) -> None:
    teacher = await _enter(client, "Profe", role="teacher")
    created = await client.post(
        "/api/v1/classes", headers=teacher, json={"name": "Nueva", "subject": "Física"}
    )
    auth = await _enter(client, "Ana", class_code="SENSOR1")
    await client.post(
        "/api/v1/classes/join", headers=auth, json={"code": created.json()["invite_code"]}
    )

    adaptation = await client.post(
        f"/api/v1/materials/{'00000000-0000-4000-8000-00000000a001'}/adaptations",
        headers=auth,
        json={"format": "audio"},
    )

    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(test_settings.database_url)
    async with engine.connect() as connection:
        class_id = await connection.scalar(
            text("SELECT class_id FROM adaptations WHERE id = :id"),
            {"id": adaptation.json()["id"]},
        )
    await engine.dispose()
    assert str(class_id) == created.json()["id"]


async def test_the_database_allows_one_active_class_per_person(db_session: AsyncSession) -> None:
    person = uuid4()
    await db_session.execute(
        text(
            "INSERT INTO persons (id, alias, career, role, configured_by, created_at) "
            "VALUES (:p, 'Ana', 'X', 'learner', 'self', now())"
        ),
        {"p": person},
    )
    insert = text(
        "INSERT INTO memberships (id, class_id, person_id, alias, status, created_at) "
        "VALUES (:id, :c, :p, 'Ana', 'joined', now())"
    )
    await db_session.execute(insert, {"id": uuid4(), "c": DEMO_CLASS, "p": person})

    with pytest.raises(IntegrityError):
        await db_session.execute(insert, {"id": uuid4(), "c": DEMO_CLASS, "p": person})
