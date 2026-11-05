"""M2 · Primera configuración: contract with the front."""

from typing import Literal

from pydantic import BaseModel, Field

from frobi.modules.onboarding.application import OnboardingResult
from frobi.modules.onboarding.domain import AccessibilityProfile, AccessibilitySetting, Profile


class AccessibilityProfileOut(BaseModel):
    id: AccessibilityProfile
    name: str
    description: str
    icon: str = Field(description="Nombre del ícono que usa el front.")
    enables: list[AccessibilitySetting]
    suggested_format: Literal["visual_map", "real_example", "easy_read", "audio"]

    @classmethod
    def from_domain(cls, profile: Profile) -> "AccessibilityProfileOut":
        return cls(
            id=profile.id,
            name=profile.name,
            description=profile.description,
            icon=profile.icon,
            enables=list(profile.enables),
            suggested_format=profile.suggested_format,  # type: ignore[arg-type]
        )


class OnboardingRequest(BaseModel):
    who_uses: Literal["self", "companion"] = Field(
        description="`companion`: alguien configura FROBI para la persona (RF36)."
    )
    profiles: list[AccessibilityProfile] = Field(default_factory=list, max_length=5)
    intro: Literal["seen", "skipped"] = Field(description="Introducción a la IA (RF37).")


class OnboardingOut(BaseModel):
    done: bool
    configured_by: Literal["self", "companion"] | None
    profiles: list[AccessibilityProfile]
    enabled_settings: list[AccessibilitySetting] = Field(
        description="Ajustes que quedaron activos por los perfiles elegidos."
    )
    intro_status: Literal["seen", "skipped", "pending"]

    @classmethod
    def from_result(cls, result: OnboardingResult) -> "OnboardingOut":
        return cls(
            done=result.done,
            configured_by=result.configured_by.value,
            profiles=[AccessibilityProfile(p) for p in result.profiles],
            enabled_settings=[AccessibilitySetting(s) for s in result.enabled_settings],
            intro_status=result.intro_status,
        )
