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
