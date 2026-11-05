"""A brief (consigna) and a draft (borrador) organized side by side (RF18).

Deterministic and without AI: it lists what the brief asks, what the draft talks about and which
requirements the draft does not seem to cover yet. It never judges authorship.
"""

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

MAX_ITEMS = 12
_BULLET = re.compile(r"^\s*(?:[-*•·]|\d+[.)]|[a-z][.)])\s+", re.IGNORECASE)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    [
        "como",
        "cual",
        "cuales",
        "cuando",
        "debe",
        "deben",
        "donde",
        "entre",
        "esta",
        "este",
        "estos",
        "estas",
        "para",
        "pero",
        "porque",
        "puede",
        "pueden",
        "sobre",
        "tiene",
        "tienen",
        "todo",
        "todos",
        "tambien",
        "trabajo",
        "hacer",
        "cada",
        "desde",
        "hasta",
        "segun",
        "explicar",
        "explica",
        "describir",
        "describe",
        "incluir",
        "incluye",
        "realizar",
        "indicar",
        "indica",
        "mencionar",
        "presentar",
        "elaborar",
    ]
)


@dataclass(frozen=True, slots=True)
class OrganizedWork:
    requirements: tuple[str, ...]
    topics: tuple[str, ...]
    missing: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Work:
    id: UUID
    person_id: UUID
    class_id: UUID | None
    brief_material_id: UUID
    draft_material_id: UUID
    organized: OrganizedWork
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        person_id: UUID,
        brief_material_id: UUID,
        draft_material_id: UUID,
        brief_text: str,
        draft_text: str,
        now: datetime,
        class_id: UUID | None = None,
    ) -> "Work":
        return cls(
            id=uuid4(),
            person_id=person_id,
            class_id=class_id,
            brief_material_id=brief_material_id,
            draft_material_id=draft_material_id,
            organized=organize(brief_text, draft_text),
            created_at=now,
        )


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def keywords(text: str) -> set[str]:
    return {w for w in _WORD.findall(_fold(text)) if len(w) >= 5 and w not in _STOPWORDS}


def _clean(item: str) -> str:
    return _BULLET.sub("", item).strip(" :;-").rstrip(".")


def requirements_of(brief: str) -> tuple[str, ...]:
    """Bulleted or numbered lines if there are any; otherwise every sentence."""
    lines = [line for line in brief.splitlines() if line.strip()]
    bullets = [_clean(line) for line in lines if _BULLET.match(line)]
    items = bullets or [_clean(s) for line in lines for s in _SENTENCE.split(line)]
    return tuple(dict.fromkeys(item for item in items if keywords(item)))[:MAX_ITEMS]


def topics_of(draft: str) -> tuple[str, ...]:
    """Headings (`#`, or short lines without a final period); otherwise each paragraph's start."""
    lines = [line.strip() for line in draft.splitlines() if line.strip()]
    headings = [
        line.lstrip("#").strip()
        for line in lines
        if line.startswith("#") or (len(line.split()) <= 8 and not line.endswith((".", ":")))
    ]
    if not headings:
        headings = [_SENTENCE.split(line)[0].rstrip(".") for line in lines]
    return tuple(dict.fromkeys(h for h in headings if h))[:MAX_ITEMS]


def is_covered(requirement: str, draft_words: set[str]) -> bool:
    wanted = keywords(requirement)
    if not wanted:
        return True
    return len(wanted & draft_words) * 2 >= len(wanted)


def organize(brief: str, draft: str) -> OrganizedWork:
    requirements = requirements_of(brief)
    draft_words = keywords(draft)
    return OrganizedWork(
        requirements=requirements,
        topics=topics_of(draft),
        missing=tuple(r for r in requirements if not is_covered(r, draft_words)),
    )
