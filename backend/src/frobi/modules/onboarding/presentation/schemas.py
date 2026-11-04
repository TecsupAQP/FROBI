"""M2 · Primera configuración: contract with the front."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class AccessibilityProfile(StrEnum):
    """Profiles offered by the wizard. Pending confirmation against the requirements (RF35)."""

    LOW_VISION = "low_vision"
    READING = "reading"
    HEARING = "hearing"
    ATTENTION = "attention"
    MOTOR = "motor"


class AccessibilitySetting(StrEnum):
    VOICE = "voice"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    SHORT_TEXTS = "short_texts"
    CAPTIONS = "captions"
    LARGE_BUTTONS = "large_buttons"
    KEYBOARD_MODE = "keyboard_mode"


class AccessibilityProfileOut(BaseModel):
    id: AccessibilityProfile
    name: str
    description: str
    icon: str = Field(description="Nombre del ícono que usa el front.")
    enables: list[AccessibilitySetting]
    suggested_format: Literal["visual_map", "real_example", "easy_read", "audio"]


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
