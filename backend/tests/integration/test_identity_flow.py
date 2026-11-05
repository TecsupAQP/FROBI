"""M1 end to end on the real stack: HTTP → handlers → Postgres (frobi_test) and Redis (db 15)."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration


@pytest.fixture
async def live_client(
    test_settings: Settings, migrated_database: str, redis: "Redis"
) -> AsyncIterator[AsyncClient]:
    app = create_app(test_settings)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    await app.state.redis.aclose()
    await app.state.engine.dispose()


async def test_enter_use_the_token_and_leave(live_client: AsyncClient) -> None:
    entered = await live_client.post(
        "/api/v1/sessions",
        json={
            "alias": " Luis ",
            "career": "Electrónica",
            "role": "learner",
            "class_code": "SENSOR1",
        },
    )
    assert entered.status_code == 201, entered.text
    session = entered.json()
    headers = {"Authorization": f"Bearer {session['token']}"}

    me = await live_client.get("/api/v1/me", headers=headers)
    other_module = await live_client.get("/api/v1/formats", headers=headers)
    left = await live_client.delete("/api/v1/sessions/current", headers=headers)
    after = await live_client.get("/api/v1/me", headers=headers)

    assert me.status_code == 200
    assert me.json()["person"]["alias"] == "Luis"
    assert me.json()["membership"]["class_name"] == "Sensores 2026-II"
    assert other_module.status_code == 200
    assert left.status_code == 204
    assert after.status_code == 401


async def test_the_old_example_token_no_longer_works(live_client: AsyncClient) -> None:
    response = await live_client.get(
        "/api/v1/me", headers={"Authorization": "Bearer example-token"}
    )

    assert response.status_code == 401
