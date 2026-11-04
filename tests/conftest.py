from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

FRONT_ORIGIN = "http://front.test"


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        cors_origins=[FRONT_ORIGIN],
        health_timeout_seconds=0.5,
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
