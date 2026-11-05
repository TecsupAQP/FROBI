"""The 4-piece recipe (context, goal, level, format) — built here and only here (RF07).

The same recipe is shown to the person, copied with «Copiar receta» (RF08) and sent to the model,
so what the person learns to ask for is exactly what FROBI asked for.
"""

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass

from .formats import Format, info

ENGINE_RULE = "Usa solo el material que te doy y avisa si algo no está en él."


@dataclass(frozen=True, slots=True)
class Recipe:
    context: str
    goal: str
    level: str
    format: Format

    @classmethod
    def build(
        cls, *, material_title: str, fmt: Format, enabled_settings: Iterable[str]
    ) -> "Recipe":
        enabled = set(enabled_settings)
        if "short_texts" in enabled:
            level = "Explicación muy simple, frases cortas, sin conocimientos previos."
        else:
            level = "Primer contacto con el tema, sin conocimientos previos."
        return cls(
            context=f"Estudio el material «{material_title}».",
            goal="Entender las ideas principales y poder explicarlas con mis palabras.",
            level=level,
            format=fmt,
        )

    def prompt_text(self) -> str:
        return (
            f"Contexto: {self.context}\n"
            f"Objetivo: {self.goal}\n"
            f"Nivel: {self.level}\n"
            f"Formato: {info(self.format).instruction}.\n"
            f"{ENGINE_RULE}"
        )


def cache_key(text: str, fmt: Format, enabled_settings: Iterable[str]) -> str:
    """sha256(text + format + profile) — same material, format and profile, same adaptation."""
    profile = ",".join(sorted(set(enabled_settings)))
    return hashlib.sha256(f"{fmt.value}\x00{profile}\x00{text}".encode()).hexdigest()
