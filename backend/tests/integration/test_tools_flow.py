"""M10 on the real stack, recommending from a claim reviewed in M9."""

from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration


@pytest.fixture
async def client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


async def _enter(client: AsyncClient, alias: str) -> dict[str, str]:
    response = await client.post(
        "/api/v1/sessions", json={"alias": alias, "career": "Mecatrónica", "role": "learner"}
    )
    return {"Authorization": f"Bearer {response.json()['token']}"}


async def _reviewed_claims(client: AsyncClient, auth: dict[str, str]) -> dict[str, str]:
    async def paste(kind: str, body: str) -> str:
        response = await client.post(
            "/api/v1/materials", headers=auth, json={"title": kind, "kind": kind, "text": body}
        )
        return str(response.json()["id"])

    work = await client.post(
        "/api/v1/works",
        headers=auth,
        json={
            "brief_material_id": await paste("brief", "- Comparar sensores"),
            "draft_material_id": await paste(
                "draft",
                "Los sensores capacitivos solo detectan metales.\n"
                "Los sensores ópticos son los más baratos del mercado.",
            ),
        },
    )
    review = await client.post(f"/api/v1/works/{work.json()['id']}/claim-review", headers=auth)
    claims = [c for s in review.json()["sections"] for c in s["claims"]]
    return {c["status"]: c["id"] for c in claims}


async def test_recommendations_follow_the_claim_review(client: AsyncClient) -> None:
    auth = await _enter(client, "Ana")
    claims = await _reviewed_claims(client, auth)

    for_unverifiable = await client.post(
        "/api/v1/tools/recommendations", headers=auth, json={"claim_id": claims["unverifiable"]}
    )
    for_contradiction = await client.post(
        "/api/v1/tools/recommendations", headers=auth, json={"claim_id": claims["contradicts"]}
    )

    assert for_unverifiable.status_code == 200, for_unverifiable.text
    assert for_unverifiable.json()["tool"]["id"] == "google-scholar"
    assert "ópticos" in for_unverifiable.json()["why"]
    assert for_contradiction.json()["tool"]["id"] == "notebooklm"


async def test_catalogue_need_and_errors(client: AsyncClient) -> None:
    ana = await _enter(client, "Ana")
    luis = await _enter(client, "Luis")
    claims = await _reviewed_claims(client, ana)

    catalogue = await client.get("/api/v1/tools", headers=ana)
    visualize = await client.get("/api/v1/tools?need=visualize", headers=ana)
    by_need = await client.post(
        "/api/v1/tools/recommendations", headers=ana, json={"need": "write"}
    )
    nothing = await client.post("/api/v1/tools/recommendations", headers=ana, json={})
    unknown_need = await client.get("/api/v1/tools?need=magia", headers=ana)
    theirs = await client.post(
        "/api/v1/tools/recommendations", headers=luis, json={"claim_id": claims["contradicts"]}
    )
    missing = await client.post(
        "/api/v1/tools/recommendations", headers=ana, json={"claim_id": str(uuid4())}
    )

    assert len(catalogue.json()) == 5
    assert [t["id"] for t in visualize.json()] == ["excalidraw"]
    assert by_need.json()["tool"]["id"] == "languagetool"
    assert nothing.status_code == 422
    assert nothing.json()["code"] == "Tools.NeedRequired"
    assert unknown_need.status_code == 422
    assert unknown_need.json()["code"] == "Tools.UnknownNeed"
    assert theirs.status_code == 404
    assert missing.status_code == 404
