"""M9 on the real stack: a work from M3 reviewed against the person's guides and the sample."""

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

DEMO_DRAFT = (
    "# Introducción\n"
    "Los sensores inductivos detectan metales sin contacto.\n"
    "Los sensores capacitivos solo detectan metales.\n"
    "# Conclusión\n"
    "Los sensores ópticos son los más baratos del mercado."
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


async def _enter(client: AsyncClient, alias: str = "Ana") -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions", json={"alias": alias, "career": "Mecatrónica", "role": "learner"}
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def _paste(client: AsyncClient, auth: dict[str, str], kind: str, body: str) -> str:
    response = await client.post(
        "/api/v1/materials", headers=auth, json={"title": kind, "kind": kind, "text": body}
    )
    return str(response.json()["id"])


async def _work(client: AsyncClient, auth: dict[str, str], draft: str = DEMO_DRAFT) -> str:
    brief = await _paste(client, auth, "brief", "- Comparar tipos de sensores")
    draft_id = await _paste(client, auth, "draft", draft)
    response = await client.post(
        "/api/v1/works",
        headers=auth,
        json={"brief_material_id": brief, "draft_material_id": draft_id},
    )
    return str(response.json()["id"])


async def test_the_scripted_demo_against_the_sample_guide(client: AsyncClient) -> None:
    auth = await _enter(client)
    work_id = await _work(client, auth)

    reviewed = await client.post(f"/api/v1/works/{work_id}/claim-review", headers=auth)
    again = await client.get(f"/api/v1/works/{work_id}/claims", headers=auth)

    assert reviewed.status_code == 200, reviewed.text
    sections = reviewed.json()["sections"]
    assert [s["section"] for s in sections] == ["Introducción", "Conclusión"]
    statuses = [c["status"] for s in sections for c in s["claims"]]
    assert statuses == ["supported", "contradicts", "unverifiable"]
    unverifiable = sections[1]["claims"][0]
    assert unverifiable["backing_passage"] is None
    assert unverifiable["no_backing_message"] == "No hay respaldo en tu material."
    assert sections[0]["claims"][0]["no_backing_message"] is None
    assert again.json() == reviewed.json()


async def test_my_own_guide_also_backs_claims(client: AsyncClient) -> None:
    auth = await _enter(client)
    await _paste(client, auth, "guide", "Un PLC ejecuta su programa en ciclos llamados barridos.")
    work_id = await _work(client, auth, "Un PLC ejecuta el programa en ciclos llamados barridos.")

    reviewed = await client.post(f"/api/v1/works/{work_id}/claim-review", headers=auth)

    claim = reviewed.json()["sections"][0]["claims"][0]
    assert claim["status"] == "supported"
    assert "barridos" in claim["backing_passage"]


async def test_reviewing_again_replaces_the_previous_review(client: AsyncClient) -> None:
    auth = await _enter(client)
    work_id = await _work(client, auth)

    first = await client.post(f"/api/v1/works/{work_id}/claim-review", headers=auth)
    second = await client.post(f"/api/v1/works/{work_id}/claim-review", headers=auth)
    stored = await client.get(f"/api/v1/works/{work_id}/claims", headers=auth)

    first_ids = {c["id"] for s in first.json()["sections"] for c in s["claims"]}
    stored_ids = {c["id"] for s in stored.json()["sections"] for c in s["claims"]}
    assert len(stored_ids) == 3
    assert stored_ids == {c["id"] for s in second.json()["sections"] for c in s["claims"]}
    assert not first_ids & stored_ids


async def test_privacy_and_errors(client: AsyncClient) -> None:
    ana = await _enter(client, "Ana")
    luis = await _enter(client, "Luis")
    work_id = await _work(client, ana)
    empty_work = await _work(client, ana, "Hola, ¿qué tal?")

    not_reviewed = await client.get(f"/api/v1/works/{work_id}/claims", headers=ana)
    theirs = await client.post(f"/api/v1/works/{work_id}/claim-review", headers=luis)
    unknown = await client.post(f"/api/v1/works/{uuid4()}/claim-review", headers=ana)
    nothing = await client.post(f"/api/v1/works/{empty_work}/claim-review", headers=ana)

    assert not_reviewed.status_code == 404
    assert theirs.status_code == 404
    assert unknown.status_code == 404
    assert nothing.status_code == 422
    assert nothing.json()["code"] == "ClaimReview.NothingToReview"


async def test_the_database_only_accepts_the_closed_vocabulary(db_session: AsyncSession) -> None:
    with pytest.raises(IntegrityError):
        await db_session.execute(
            text(
                "INSERT INTO claims (id, work_id, person_id, position, section, fragment, "
                "status, reason, created_at) VALUES (:id, :w, :p, 0, 's', 'f', 'false', 'r', now())"
            ),
            {"id": uuid4(), "w": uuid4(), "p": uuid4()},
        )
