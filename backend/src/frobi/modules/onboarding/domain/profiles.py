"""Accessibility profiles offered by the wizard and the switches each one turns on (RF35).

Pending confirmation against the requirements document; this is the single place to change them.
"""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class AccessibilityProfile(StrEnum):
    LOW_VISION = "low_vision"
    READING = "reading"
    HEARING = "hearing"
    ATTENTION = "attention"
    MOTOR = "motor"


class AccessibilitySetting(StrEnum):
    """Same names as the switches stored by settings."""

    VOICE = "voice"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    SHORT_TEXTS = "short_texts"
    CAPTIONS = "captions"
    LARGE_BUTTONS = "large_buttons"
    KEYBOARD_MODE = "keyboard_mode"


class WhoUses(StrEnum):
    SELF = "self"
    COMPANION = "companion"


@dataclass(frozen=True, slots=True)
class Profile:
    id: AccessibilityProfile
    name: str
    description: str
    icon: str
    enables: tuple[AccessibilitySetting, ...]
    suggested_format: str


S = AccessibilitySetting
CATALOGUE: tuple[Profile, ...] = (
    Profile(
        AccessibilityProfile.LOW_VISION,
        "Baja visión",
        "Letra grande, alto contraste y lectura en voz alta.",
        "eye",
        (S.LARGE_TEXT, S.HIGH_CONTRAST, S.VOICE),
        "audio",
    ),
    Profile(
        AccessibilityProfile.READING,
        "Dificultad para leer",
        "Textos cortos y lectura fácil, con voz si la necesitas.",
        "book",
        (S.SHORT_TEXTS, S.VOICE),
        "easy_read",
    ),
    Profile(
        AccessibilityProfile.HEARING,
        "Audición",
        "Subtítulos en todo lo que tenga audio.",
        "ear",
        (S.CAPTIONS,),
        "visual_map",
    ),
    Profile(
        AccessibilityProfile.ATTENTION,
        "Atención",
        "Pasos cortos, un tema a la vez.",
        "target",
        (S.SHORT_TEXTS,),
        "visual_map",
    ),
    Profile(
        AccessibilityProfile.MOTOR,
        "Movilidad",
        "Botones grandes y uso completo con teclado.",
        "hand",
        (S.LARGE_BUTTONS, S.KEYBOARD_MODE),
        "real_example",
    ),
)
_BY_ID = {profile.id: profile for profile in CATALOGUE}


def unique_profiles(profiles: Iterable[AccessibilityProfile]) -> tuple[AccessibilityProfile, ...]:
    return tuple(dict.fromkeys(profiles))


def settings_for(profiles: Iterable[AccessibilityProfile]) -> tuple[AccessibilitySetting, ...]:
    """Union of the switches of every chosen profile, in a stable order."""
    chosen = {setting for profile in profiles for setting in _BY_ID[profile].enables}
    return tuple(setting for setting in AccessibilitySetting if setting in chosen)
