"""M2 · Primera configuración.

Stub: returns example data so the front can integrate. The real use cases replace each body.
"""

from fastapi import APIRouter, Depends

from frobi.shared.presentation import AUTH_RESPONSES, CurrentPersonId, require_token

from .schemas import (
    AccessibilityProfile,
    AccessibilityProfileOut,
    AccessibilitySetting,
    OnboardingOut,
    OnboardingRequest,
)

router = APIRouter(tags=["M2 · Primera configuración"])
me_router = APIRouter(
    prefix="/me/onboarding",
    tags=["M2 · Primera configuración"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)

S = AccessibilitySetting
PROFILES = [
    AccessibilityProfileOut(
        id=AccessibilityProfile.LOW_VISION,
        name="Baja visión",
        description="Letra grande, alto contraste y lectura en voz alta.",
        icon="eye",
        enables=[S.LARGE_TEXT, S.HIGH_CONTRAST, S.VOICE],
        suggested_format="audio",
    ),
    AccessibilityProfileOut(
        id=AccessibilityProfile.READING,
        name="Dificultad para leer",
        description="Textos cortos y lectura fácil, con voz si la necesitas.",
        icon="book",
        enables=[S.SHORT_TEXTS, S.VOICE],
        suggested_format="easy_read",
    ),
    AccessibilityProfileOut(
        id=AccessibilityProfile.HEARING,
        name="Audición",
        description="Subtítulos en todo lo que tenga audio.",
        icon="ear",
        enables=[S.CAPTIONS],
        suggested_format="visual_map",
    ),
    AccessibilityProfileOut(
        id=AccessibilityProfile.ATTENTION,
        name="Atención",
        description="Pasos cortos, un tema a la vez.",
        icon="target",
        enables=[S.SHORT_TEXTS],
        suggested_format="visual_map",
    ),
    AccessibilityProfileOut(
        id=AccessibilityProfile.MOTOR,
        name="Movilidad",
        description="Botones grandes y uso completo con teclado.",
        icon="hand",
        enables=[S.LARGE_BUTTONS, S.KEYBOARD_MODE],
        suggested_format="real_example",
    ),
]
_ENABLES = {profile.id: profile.enables for profile in PROFILES}


def _enabled(profiles: list[AccessibilityProfile]) -> list[AccessibilitySetting]:
    selected = {setting for profile in profiles for setting in _ENABLES[profile]}
    return [setting for setting in AccessibilitySetting if setting in selected]


@router.get(
    "/accessibility-profiles",
    summary="Catálogo de perfiles y los ajustes que activa cada uno",
    responses=AUTH_RESPONSES,
)
async def list_accessibility_profiles(_: CurrentPersonId) -> list[AccessibilityProfileOut]:
    return PROFILES


@me_router.post("", summary="Completar el asistente y aplicar los perfiles")
async def complete_onboarding(body: OnboardingRequest) -> OnboardingOut:
    unique = list(dict.fromkeys(body.profiles))
    return OnboardingOut(
        done=True,
        configured_by=body.who_uses,
        profiles=unique,
        enabled_settings=_enabled(unique),
        intro_status=body.intro,
    )


@me_router.post("/skip", summary="Omitir el asistente")
async def skip_onboarding() -> OnboardingOut:
    return OnboardingOut(
        done=True, configured_by=None, profiles=[], enabled_settings=[], intro_status="skipped"
    )


@me_router.post("/reset", summary="Volver a hacer el asistente")
async def reset_onboarding() -> OnboardingOut:
    return OnboardingOut(
        done=False, configured_by=None, profiles=[], enabled_settings=[], intro_status="pending"
    )
