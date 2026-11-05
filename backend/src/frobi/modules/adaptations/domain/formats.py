"""The 4 formats a material can be adapted to (RF03) and which one to suggest (RF35)."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class Format(StrEnum):
    VISUAL_MAP = "visual_map"
    REAL_EXAMPLE = "real_example"
    EASY_READ = "easy_read"
    AUDIO = "audio"


@dataclass(frozen=True, slots=True)
class FormatInfo:
    id: Format
    name: str
    description: str
    icon: str
    instruction: str  # what the model is asked to produce, part of the recipe


FORMATS: tuple[FormatInfo, ...] = (
    FormatInfo(
        Format.VISUAL_MAP,
        "Mapa visual",
        "Las ideas y cómo se conectan.",
        "map",
        "un mapa de ideas: un tema central y ramas con frases cortas",
    ),
    FormatInfo(
        Format.REAL_EXAMPLE,
        "Ejemplo real",
        "El tema aplicado a un caso de la industria.",
        "factory",
        "un caso concreto de la industria que muestre cada idea en acción",
    ),
    FormatInfo(
        Format.EASY_READ,
        "Lectura fácil",
        "Frases cortas y palabras simples.",
        "text",
        "lectura fácil: frases cortas, una idea por frase, palabras comunes",
    ),
    FormatInfo(
        Format.AUDIO,
        "Audio",
        "Te lo leemos en voz alta.",
        "volume",
        "un texto para escuchar: frases que se entiendan sin ver la pantalla",
    ),
)
_INFO = {info.id: info for info in FORMATS}


def info(fmt: Format) -> FormatInfo:
    return _INFO[fmt]


def suggested_format(enabled_settings: Iterable[str]) -> Format | None:
    """First match wins: voice → audio, short texts → easy read, captions → visual map."""
    enabled = set(enabled_settings)
    if "voice" in enabled:
        return Format.AUDIO
    if "short_texts" in enabled:
        return Format.EASY_READ
    if "captions" in enabled or "high_contrast" in enabled:
        return Format.VISUAL_MAP
    if "large_buttons" in enabled or "keyboard_mode" in enabled:
        return Format.REAL_EXAMPLE
    return None
