import asyncio

from fastapi import FastAPI
from httpx import AsyncClient

from frobi.shared.presentation.health import get_health_probes


class Probe:
    def __init__(self, name: str, *, fails: bool = False, delay: float = 0.0) -> None:
        self.name = name
        self._fails = fails
        self._delay = delay

    async def check(self) -> None:
        await asyncio.sleep(self._delay)
        if self._fails:
            raise ConnectionError(self.name)


def use_probes(app: FastAPI, *probes: Probe) -> None:
    app.dependency_overrides[get_health_probes] = lambda: list(probes)


async def test_health_is_ok_when_postgres_and_redis_answer(
    app: FastAPI, client: AsyncClient
) -> None:
    use_probes(app, Probe("postgres"), Probe("redis"))

    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"postgres": "up", "redis": "up"}}


async def test_health_is_degraded_with_503_when_a_dependency_is_down(
    app: FastAPI, client: AsyncClient
) -> None:
    use_probes(app, Probe("postgres", fails=True), Probe("redis"))

    response = await client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "checks": {"postgres": "down", "redis": "up"}}


async def test_health_marks_a_hanging_dependency_as_down(app: FastAPI, client: AsyncClient) -> None:
    use_probes(app, Probe("postgres"), Probe("redis", delay=5))

    response = await client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["checks"]["redis"] == "down"


async def test_health_needs_no_authentication(app: FastAPI, client: AsyncClient) -> None:
    use_probes(app, Probe("postgres"), Probe("redis"))

    response = await client.get("/api/v1/health", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 200
