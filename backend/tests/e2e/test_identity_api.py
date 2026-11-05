"""M1 over HTTP, with in-memory adapters behind the real handlers."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from fakes.identity import IdentityFakes
from frobi.modules.identity.presentation.dependencies import (
    get_end_session,
    get_get_me,
    get_start_session,
)

ANA = {"alias": "Ana", "career": "Mecatrónica", "role": "learner"}


@pytest.fixture
def fakes(app: FastAPI) -> IdentityFakes:
    fakes = IdentityFakes()
    app.dependency_overrides[get_start_session] = fakes.start_session
    app.dependency_overrides[get_end_session] = fakes.end_session
    app.dependency_overrides[get_get_me] = fakes.get_me
    app.state.token_resolver = fakes.sessions
    return fakes


async def _enter(client: AsyncClient, **extra: str) -> dict[str, object]:
    response = await client.post("/api/v1/sessions", json={**ANA, **extra})
    assert response.status_code == 201, response.text
    body: dict[str, object] = response.json()
    return body


async def test_enter_then_me_returns_the_same_person(
    client: AsyncClient, fakes: IdentityFakes
) -> None:
    session = await _enter(client)

    response = await client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {session['token']}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["person"] == session["person"]
    assert body["membership"] is None
    assert body["onboarding"] == {"done": False, "intro_status": "pending"}


async def test_enter_with_code_shows_the_class_in_me(
    client: AsyncClient, fakes: IdentityFakes
) -> None:
    session = await _enter(client, class_code="SENSOR1")

    response = await client.get(
        "/api/v1/me", headers={"Authorization": f"Bearer {session['token']}"}
    )

    assert response.json()["membership"]["class_name"] == "Sensores 2026-II"


async def test_unknown_code_is_422_and_nobody_is_created(
    client: AsyncClient, fakes: IdentityFakes
) -> None:
    response = await client.post("/api/v1/sessions", json={**ANA, "class_code": "NOPE"})

    assert response.status_code == 422
    assert response.json()["code"] == "Classrooms.InvalidCode"
    assert fakes.persons.items == {}


async def test_blank_alias_is_422_with_identity_code(
    client: AsyncClient, fakes: IdentityFakes
) -> None:
    response = await client.post("/api/v1/sessions", json={**ANA, "alias": "   "})

    assert response.status_code == 422
    assert response.json()["code"] == "Identity.InvalidAlias"


async def test_logout_makes_the_token_useless(client: AsyncClient, fakes: IdentityFakes) -> None:
    session = await _enter(client)
    headers = {"Authorization": f"Bearer {session['token']}"}

    logout = await client.delete("/api/v1/sessions/current", headers=headers)
    me = await client.get("/api/v1/me", headers=headers)

    assert logout.status_code == 204
    assert me.status_code == 401
    assert me.json()["code"] == "Identity.Unauthenticated"


async def test_a_made_up_token_is_rejected(client: AsyncClient, fakes: IdentityFakes) -> None:
    response = await client.get("/api/v1/me", headers={"Authorization": "Bearer made-up"})

    assert response.status_code == 401
