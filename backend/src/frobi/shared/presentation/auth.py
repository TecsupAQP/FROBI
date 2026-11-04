"""Bearer token extraction shared by every authenticated router.

Until M1 resolves tokens against Redis, any non-empty token is accepted, so the front can
integrate against the stubs. ``current_person`` will build on ``require_token``.
"""

from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from frobi.shared.application import Unauthenticated

from .problem import ProblemDetail

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Token opaco que devuelve `POST /api/v1/sessions`.",
)


async def require_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None or not credentials.credentials.strip():
        raise Unauthenticated()
    return credentials.credentials


AuthToken = Annotated[str, Depends(require_token)]

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
