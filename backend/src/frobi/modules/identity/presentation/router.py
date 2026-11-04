"""M1 · Cuenta y acceso.

Stub: returns example data so the front can integrate. The real use cases replace each body.
"""

from uuid import UUID

from fastapi import APIRouter, status

from frobi.modules.identity.domain.errors import InvalidClassCode
from frobi.shared.presentation import AUTH_RESPONSES, AuthToken, problem

from .schemas import (
    ActiveMembershipOut,
    ConfiguredBy,
    CreateSessionRequest,
    IntroStatus,
    MeOut,
    OnboardingStateOut,
    PersonOut,
    Role,
    SessionOut,
)

router = APIRouter(tags=["M1 · Cuenta y acceso"])

EXAMPLE_PERSON_ID = UUID("00000000-0000-4000-8000-000000000001")
EXAMPLE_CLASS_ID = UUID("00000000-0000-4000-8000-0000000000c1")
EXAMPLE_CLASS_CODE = "SENSOR1"
EXAMPLE_MEMBERSHIP = ActiveMembershipOut(class_id=EXAMPLE_CLASS_ID, class_name="Sensores 2026-II")


@router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
    summary="Entrar con alias, carrera y rol (sin contraseña)",
    responses={422: problem("Datos inválidos o código de clase inexistente.")},
)
async def create_session(body: CreateSessionRequest) -> SessionOut:
    membership = None
    if body.class_code is not None:
        if body.class_code.strip().upper() != EXAMPLE_CLASS_CODE:
            raise InvalidClassCode()
        membership = EXAMPLE_MEMBERSHIP
    person = PersonOut(
        id=EXAMPLE_PERSON_ID,
        alias=body.alias,
        career=body.career,
        role=body.role,
        configured_by=ConfiguredBy.SELF,
    )
    return SessionOut(token="example-token", person=person, membership=membership)


@router.delete(
    "/sessions/current",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar la sesión",
    responses=AUTH_RESPONSES,
)
async def delete_current_session(_: AuthToken) -> None:
    return None


@router.get(
    "/me",
    summary="Persona actual, clase activa y estado del asistente",
    responses=AUTH_RESPONSES,
)
async def get_me(_: AuthToken) -> MeOut:
    return MeOut(
        person=PersonOut(
            id=EXAMPLE_PERSON_ID,
            alias="Ana",
            career="Mecatrónica",
            role=Role.LEARNER,
            configured_by=ConfiguredBy.SELF,
        ),
        membership=EXAMPLE_MEMBERSHIP,
        onboarding=OnboardingStateOut(done=False, intro_status=IntroStatus.PENDING),
    )
