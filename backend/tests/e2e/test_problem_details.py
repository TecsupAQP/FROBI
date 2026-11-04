from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from frobi.shared.application import Unauthenticated
from frobi.shared.domain import DomainError, ErrorKind
from frobi.shared.presentation import PROBLEM_JSON


class FinalLocked(DomainError):
    code = "Tutoring.FinalLocked"
    kind = ErrorKind.CONFLICT
    default_message = "Se desbloquea después de tu intento."


class Payload(BaseModel):
    alias: str


@pytest.fixture
def app(app: FastAPI) -> FastAPI:
    @app.get("/boom/domain")
    async def domain_error() -> None:
        raise FinalLocked()

    @app.get("/boom/auth")
    async def auth_error() -> None:
        raise Unauthenticated()

    @app.post("/boom/validation")
    async def validation(payload: Payload) -> Payload:
        return payload

    @app.get("/boom/unexpected")
    async def unexpected() -> None:
        raise RuntimeError("database exploded")

    return app


@pytest.fixture
async def lenient_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """A client that returns 500 responses instead of re-raising the server's exception."""
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_domain_error_becomes_problem_json_with_its_code(client: AsyncClient) -> None:
    response = await client.get("/boom/domain")

    assert response.status_code == 409
    assert response.headers["content-type"] == PROBLEM_JSON
    assert response.json() == {
        "type": "about:blank",
        "title": "Conflict",
        "status": 409,
        "code": "Tutoring.FinalLocked",
        "detail": "Se desbloquea después de tu intento.",
        "instance": "/boom/domain",
    }


async def test_unauthenticated_is_401_with_bearer_challenge(client: AsyncClient) -> None:
    response = await client.get("/boom/auth")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["code"] == "Identity.Unauthenticated"


async def test_invalid_input_is_422_with_one_entry_per_field(client: AsyncClient) -> None:
    response = await client.post("/boom/validation", json={})

    assert response.status_code == 422
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert body["code"] == "Validation.Invalid"
    assert body["errors"] == [
        {"loc": ["body", "alias"], "msg": "Field required", "type": "missing"}
    ]


async def test_unknown_route_is_404_problem_json(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == PROBLEM_JSON
    assert response.json()["code"] == "Http.NotFound"


async def test_unexpected_error_is_500_without_leaking_internals(
    lenient_client: AsyncClient,
) -> None:
    response = await lenient_client.get("/boom/unexpected")

    assert response.status_code == 500
    assert response.headers["content-type"] == PROBLEM_JSON
    body = response.json()
    assert body["code"] == "Internal.Unexpected"
    assert "database exploded" not in response.text
