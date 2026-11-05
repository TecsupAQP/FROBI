"""M1 · Cuenta y acceso."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from frobi.modules.identity.application import (
    EndSessionHandler,
    GetMeHandler,
    StartSessionCommand,
    StartSessionHandler,
)
from frobi.shared.presentation import AUTH_RESPONSES, CurrentPersonId, SessionToken, problem

from .dependencies import get_end_session, get_get_me, get_start_session
from .schemas import CreateSessionRequest, MeOut, SessionOut

router = APIRouter(tags=["M1 · Cuenta y acceso"])


@router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    summary="Entrar con alias, carrera y rol (sin contraseña)",
    responses={422: problem("Datos inválidos o código de clase inexistente.")},
)
async def create_session(
    body: CreateSessionRequest,
    handler: Annotated[StartSessionHandler, Depends(get_start_session)],
) -> SessionOut:
    result = await handler.handle(
        StartSessionCommand(
            alias=body.alias, career=body.career, role=body.role, class_code=body.class_code
        )
    )
    return SessionOut.from_result(result)


@router.delete(
    "/sessions/current",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar la sesión",
    responses=AUTH_RESPONSES,
)
async def delete_current_session(
    token: SessionToken,
    handler: Annotated[EndSessionHandler, Depends(get_end_session)],
) -> None:
    await handler.handle(token)


@router.get(
    "/me",
    summary="Persona actual, clase activa y estado del asistente",
    responses=AUTH_RESPONSES,
)
async def get_me(
    person_id: CurrentPersonId,
    handler: Annotated[GetMeHandler, Depends(get_get_me)],
) -> MeOut:
    return MeOut.from_view(await handler.handle(person_id))
