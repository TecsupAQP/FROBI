"""RFC 9457 problem details: every error leaves the API as ``application/problem+json``.

The ``code`` field is stable and is what the front uses to pick the message and icon (RF31).
"""

import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from frobi.shared.domain import DomainError, ErrorKind

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"

STATUS_BY_KIND: dict[ErrorKind, int] = {
    ErrorKind.VALIDATION: 422,
    ErrorKind.NOT_FOUND: 404,
    ErrorKind.CONFLICT: 409,
    ErrorKind.UNAUTHENTICATED: 401,
    ErrorKind.FORBIDDEN: 403,
}

_HTTP_CODES: dict[int, str] = {
    401: "Identity.Unauthenticated",
    403: "Identity.Forbidden",
    404: "Http.NotFound",
    405: "Http.MethodNotAllowed",
}


class InvalidParam(BaseModel):
    loc: list[str | int] = Field(
        description="Ruta al campo inválido, por ejemplo ['body', 'alias']."
    )
    msg: str
    type: str


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    code: str = Field(
        description="Código estable para el front, por ejemplo 'Tutoring.FinalLocked'."
    )
    detail: str | None = None
    instance: str | None = None
    errors: list[InvalidParam] | None = Field(
        default=None, description="Solo en 422: un elemento por campo inválido."
    )


PROBLEM_RESPONSES: dict[int | str, dict[str, Any]] = {
    422: {"model": ProblemDetail, "description": "Datos inválidos (`Validation.Invalid`)."},
}


def problem_response(problem: ProblemDetail, headers: dict[str, str] | None = None) -> JSONResponse:
    return JSONResponse(
        problem.model_dump(mode="json", exclude_none=True),
        status_code=problem.status,
        media_type=PROBLEM_JSON,
        headers=headers,
    )


def _phrase(status: int) -> str:
    try:
        return HTTPStatus(status).phrase
    except ValueError:
        return "Error"


async def _domain_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    status = STATUS_BY_KIND[exc.kind]
    headers = {"WWW-Authenticate": "Bearer"} if status == 401 else None
    problem = ProblemDetail(
        title=_phrase(status),
        status=status,
        code=exc.code,
        detail=exc.message,
        instance=request.url.path,
    )
    return problem_response(problem, headers)


async def _validation_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [
        InvalidParam(loc=list(error["loc"]), msg=error["msg"], type=error["type"])
        for error in exc.errors()
    ]
    problem = ProblemDetail(
        title=_phrase(422),
        status=422,
        code="Validation.Invalid",
        detail="Revisa los datos enviados.",
        instance=request.url.path,
        errors=errors,
    )
    return problem_response(problem)


async def _http_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    status = exc.status_code
    problem = ProblemDetail(
        title=_phrase(status),
        status=status,
        code=_HTTP_CODES.get(status, f"Http.{status}"),
        detail=exc.detail if isinstance(exc.detail, str) else None,
        instance=request.url.path,
    )
    return problem_response(problem, dict(exc.headers) if exc.headers else None)


async def _unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    problem = ProblemDetail(
        title=_phrase(500),
        status=500,
        code="Internal.Unexpected",
        detail="Algo salió mal de nuestro lado. Intenta de nuevo en un momento.",
        instance=request.url.path,
    )
    return problem_response(problem)


def register_problem_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, _domain_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unexpected_error)
