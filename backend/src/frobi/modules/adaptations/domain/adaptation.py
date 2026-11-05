from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .formats import Format
from .recipe import Recipe

AI_NOTICE = (
    "Esto lo generó una IA a partir de tu material. Puede equivocarse: compáralo con la guía."
)
FALLBACK_NOTICE = (
    "Esta vez la IA no estuvo disponible, así que te mostramos una versión preparada sin IA "
    "a partir de tu material. Compárala con la guía."
)


@dataclass(frozen=True, slots=True)
class Section:
    heading: str
    body: str
    items: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class AdaptedContent:
    title: str
    sections: tuple[Section, ...]

    def plain_text(self) -> str:
        """Continuous text; for `audio` the browser reads it aloud (RF06)."""
        parts: list[str] = [self.title + "."]
        for section in self.sections:
            parts.append(section.heading.rstrip(".") + ".")
            if section.body:
                parts.append(section.body)
            parts.extend(item if item.endswith(".") else item + "." for item in section.items)
        return " ".join(parts)


@dataclass(frozen=True, slots=True)
class Adaptation:
    id: UUID
    material_id: UUID
    person_id: UUID
    class_id: UUID | None
    format: Format
    content: AdaptedContent
    recipe: Recipe
    fallback: bool
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        material_id: UUID,
        person_id: UUID,
        class_id: UUID | None,
        content: AdaptedContent,
        recipe: Recipe,
        fallback: bool,
        now: datetime,
    ) -> "Adaptation":
        return cls(
            id=uuid4(),
            material_id=material_id,
            person_id=person_id,
            class_id=class_id,
            format=recipe.format,
            content=content,
            recipe=recipe,
            fallback=fallback,
            created_at=now,
        )

    @property
    def ai_notice(self) -> str:
        return FALLBACK_NOTICE if self.fallback else AI_NOTICE

    def visible_to(self, person_id: UUID) -> bool:
        return self.person_id == person_id
