"""/health against the real Postgres and Redis from docker/compose.yml."""

import pytest
from httpx import ASGITransport, AsyncClient

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

pytestmark = pytest.mark.integration


async def test_health_reaches_real_postgres_and_redis() -> None:
    app = create_app(Settings(_env_file=None))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.json() == {"status": "ok", "checks": {"postgres": "up", "redis": "up"}}, (
        "Start the services first: docker compose -f docker/compose.yml up -d postgres redis"
    )
