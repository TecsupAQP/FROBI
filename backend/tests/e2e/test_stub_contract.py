"""Contract rules every stub must already respect, plus the flows the front depends on."""

import re
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from frobi.main import create_app
from frobi.shared.infrastructure import Settings
from frobi.shared.presentation import PROBLEM_JSON

PUBLIC = {("POST", "/api/v1/sessions"), ("GET", "/api/v1/health")}
AUTH = {"Authorization": "Bearer example-token"}


def _protected_routes() -> list[tuple[str, str]]:
    """Every operation in the published contract except the public ones."""
    paths = create_app(Settings(_env_file=None)).openapi()["paths"]
    routes = [(method.upper(), path) for path, operations in paths.items() for method in operations]
    return sorted(route for route in routes if route not in PUBLIC)


PROTECTED = _protected_routes()


def test_contract_lists_the_protected_routes() -> None:
    assert len(PROTECTED) >= 40


def _concrete(path: str) -> str:
    return re.sub(r"\{[^}]+\}", str(uuid4()), path)


@pytest.mark.parametrize(("method", "path"), PROTECTED)
async def test_protected_route_needs_a_token(client: AsyncClient, method: str, path: str) -> None:
    response = await client.request(method, _concrete(path))

    assert response.status_code == 401
    assert response.headers["content-type"] == PROBLEM_JSON
    assert response.json()["code"] == "Identity.Unauthenticated"


def test_every_protected_route_documents_its_401(app: FastAPI) -> None:
    paths = app.openapi()["paths"]
    missing = [
        f"{method} {path}"
        for method, path in PROTECTED
        if "401" not in paths[path][method.lower()]["responses"]
    ]
    assert missing == []


def test_every_route_belongs_to_a_known_docs_section(app: FastAPI) -> None:
    declared = {tag["name"] for tag in app.openapi()["tags"]}
    used = {
        tag
        for operations in app.openapi()["paths"].values()
        for operation in operations.values()
        for tag in operation.get("tags", [])
    }
    assert used <= declared


def test_contract_has_no_false_claim_status_or_ai_percentage(app: FastAPI) -> None:
    """RNF11/RNF14: closed vocabulary for claims, and no 'percentage of AI' field anywhere."""
    schemas = app.openapi()["components"]["schemas"]

    assert schemas["ClaimStatus"]["enum"] == ["supported", "unverifiable", "contradicts"]
    field_names = {name for schema in schemas.values() for name in schema.get("properties", {})}
    assert not any("percent" in name or "ai_score" in name for name in field_names)


async def test_enter_without_class(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/sessions", json={"alias": "Ana", "career": "Mecatrónica", "role": "learner"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token"]
    assert body["person"]["alias"] == "Ana"
    assert body["membership"] is None


async def test_enter_with_the_example_class_code(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/sessions",
        json={"alias": "Ana", "career": "Mecatrónica", "role": "learner", "class_code": "sensor1"},
    )

    assert response.status_code == 201
    assert response.json()["membership"]["status"] == "joined"


async def test_unknown_class_code_is_422_with_stable_code(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/sessions",
        json={"alias": "Ana", "career": "Mecatrónica", "role": "learner", "class_code": "NOPE"},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "Classrooms.InvalidCode"


async def test_onboarding_applies_the_settings_of_each_profile(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/me/onboarding",
        headers=AUTH,
        json={"who_uses": "companion", "profiles": ["low_vision", "motor"], "intro": "seen"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["done"] is True
    assert body["configured_by"] == "companion"
    assert body["enabled_settings"] == [
        "voice",
        "high_contrast",
        "large_text",
        "large_buttons",
        "keyboard_mode",
    ]


async def test_upload_rejects_a_file_that_is_not_a_pdf(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/materials/upload",
        headers=AUTH,
        data={"title": "Guía"},
        files={"file": ("guia.pdf", b"not a pdf", "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "Materials.PdfUnreadable"


async def test_final_step_is_locked_until_own_attempt(client: AsyncClient) -> None:
    response = await client.post(
        f"/api/v1/help-attempts/{uuid4()}/steps", headers=AUTH, json={"step": "final"}
    )

    assert response.status_code == 409
    assert response.json()["code"] == "Tutoring.FinalLocked"


async def test_wrong_answer_suggests_another_format(client: AsyncClient) -> None:
    response = await client.post(
        f"/api/v1/questions/{uuid4()}/answers", headers=AUTH, json={"option": "a"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_correct"] is False
    assert body["suggested_format"] == "visual_map"


async def test_questions_never_reveal_the_correct_option(client: AsyncClient) -> None:
    response = await client.post(f"/api/v1/adaptations/{uuid4()}/questions", headers=AUTH)

    assert response.status_code == 201
    assert all("correct_option" not in question for question in response.json())


async def test_dashboard_flags_sample_data(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/classes/{uuid4()}/dashboard", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["sample_data"] is True
