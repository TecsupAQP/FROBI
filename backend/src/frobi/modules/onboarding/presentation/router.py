"""M2 · Primera configuración."""

from typing import Annotated

from fastapi import APIRouter, Depends

from frobi.modules.onboarding.application import (
    CompleteOnboardingCommand,
    CompleteOnboardingHandler,
    ResetOnboardingHandler,
    SkipOnboardingHandler,
)
from frobi.modules.onboarding.domain import CATALOGUE, WhoUses
from frobi.shared.presentation import AUTH_RESPONSES, CurrentPersonId

from .dependencies import get_complete_onboarding, get_reset_onboarding, get_skip_onboarding
from .schemas import AccessibilityProfileOut, OnboardingOut, OnboardingRequest

router = APIRouter(tags=["M2 · Primera configuración"], responses=AUTH_RESPONSES)
me_router = APIRouter(
    prefix="/me/onboarding", tags=["M2 · Primera configuración"], responses=AUTH_RESPONSES
)

PROFILES = [AccessibilityProfileOut.from_domain(profile) for profile in CATALOGUE]


@router.get(
    "/accessibility-profiles",
    summary="Catálogo de perfiles y los ajustes que activa cada uno",
)
async def list_accessibility_profiles(_: CurrentPersonId) -> list[AccessibilityProfileOut]:
    return PROFILES


@me_router.post("", summary="Completar el asistente y aplicar los perfiles")
async def complete_onboarding(
    body: OnboardingRequest,
    person_id: CurrentPersonId,
    handler: Annotated[CompleteOnboardingHandler, Depends(get_complete_onboarding)],
) -> OnboardingOut:
    result = await handler.handle(
        CompleteOnboardingCommand(
            person_id=person_id,
            who_uses=WhoUses(body.who_uses),
            profiles=tuple(body.profiles),
            intro=body.intro,
        )
    )
    return OnboardingOut.from_result(result)


@me_router.post("/skip", summary="Omitir el asistente")
async def skip_onboarding(
    person_id: CurrentPersonId,
    handler: Annotated[SkipOnboardingHandler, Depends(get_skip_onboarding)],
) -> OnboardingOut:
    return OnboardingOut.from_result(await handler.handle(person_id))


@me_router.post("/reset", summary="Volver a hacer el asistente")
async def reset_onboarding(
    person_id: CurrentPersonId,
    handler: Annotated[ResetOnboardingHandler, Depends(get_reset_onboarding)],
) -> OnboardingOut:
    return OnboardingOut.from_result(await handler.handle(person_id))
