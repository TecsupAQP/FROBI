from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from frobi.main import create_app
from frobi.shared.infrastructure import Settings

FRONT_ORIGIN = "http://front.test"
EXAMPLE_TOKEN = "example-token"
EXAMPLE_PERSON_ID = UUID("00000000-0000-4000-8000-000000000001")


class AcceptExampleToken:
    """Token resolver for tests that do not exercise sessions: only `example-token` is valid."""

    async def resolve(self, token: str) -> UUID | None:
        return EXAMPLE_PERSON_ID if token == EXAMPLE_TOKEN else None


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        cors_origins=[FRONT_ORIGIN],
        health_timeout_seconds=0.5,
        llm_api_key=None,  # tests never call a real AI provider
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    app = create_app(settings)
    app.state.token_resolver = AcceptExampleToken()
    return app


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
