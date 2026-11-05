"""Bearer authentication shared by every router.

The token is resolved through the ``TokenResolver`` the app factory puts on ``app.state``
(identity's Redis session store), so shared never imports a module.
"""

from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from frobi.shared.application import TokenResolver, Unauthenticated

from .problem import ProblemDetail

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Token opaco que devuelve `POST /api/v1/sessions`.",
)


def get_token_resolver(request: Request) -> TokenResolver:
    return cast(TokenResolver, request.app.state.token_resolver)


async def session_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    resolver: Annotated[TokenResolver, Depends(get_token_resolver)],
) -> str:
    """The caller's token, once checked against the active sessions."""
    token = credentials.credentials.strip() if credentials else ""
    if not token or await resolver.resolve(token) is None:
        raise Unauthenticated()
    return token


async def current_person_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    resolver: Annotated[TokenResolver, Depends(get_token_resolver)],
) -> UUID:
    token = credentials.credentials.strip() if credentials else ""
    person_id = await resolver.resolve(token) if token else None
    if person_id is None:
        raise Unauthenticated()
    return person_id


CurrentPersonId = Annotated[UUID, Depends(current_person_id)]
SessionToken = Annotated[str, Depends(session_token)]

# Router-level dependency for routes that only need "someone is logged in".
require_token = current_person_id

AUTH_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": ProblemDetail, "description": "Sin sesión (`Identity.Unauthenticated`)."},
}

TEACHER_RESPONSES: dict[int | str, dict[str, Any]] = {
    **AUTH_RESPONSES,
    403: {"model": ProblemDetail, "description": "Solo para docentes (`Identity.Forbidden`)."},
}

NOT_FOUND_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"model": ProblemDetail, "description": "No existe (`Resource.NotFound`)."},
}


def problem(description: str) -> dict[str, Any]:
    """OpenAPI entry for an extra problem+json response on a single route."""
    return {"model": ProblemDetail, "description": description}
