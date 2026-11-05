"""Study material: a sample guide, pasted text or an uploaded PDF (RF01, RF02)."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .errors import MAX_TEXT_CHARS, EmptyText, InvalidTitle

TITLE_MAX = 120


class MaterialKind(StrEnum):
    GUIDE = "guide"
    BRIEF = "brief"
    DRAFT = "draft"
    CLASS_CONTENT = "class_content"


class MaterialSource(StrEnum):
    SAMPLE = "sample"
    UPLOAD = "upload"
    PASTE = "paste"


def normalize_title(raw: str) -> str:
    title = " ".join(raw.split())
    if not 1 <= len(title) <= TITLE_MAX:
        raise InvalidTitle()
    return title


def normalize_text(raw: str) -> str:
    """Trim each line, drop runs of blank lines, keep paragraphs."""
    lines = [" ".join(line.split()) for line in raw.replace("\r\n", "\n").split("\n")]
    paragraphs: list[str] = []
    for line in lines:
        if line or (paragraphs and paragraphs[-1]):
            paragraphs.append(line)
    text = "\n".join(paragraphs).strip()
    if not text:
        raise EmptyText()
    return text[:MAX_TEXT_CHARS]


@dataclass(frozen=True, slots=True)
class Material:
    id: UUID
    owner_id: UUID | None
    class_id: UUID | None
    title: str
    kind: MaterialKind
    source: MaterialSource
    text: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        owner_id: UUID,
        title: str,
        kind: MaterialKind,
        source: MaterialSource,
        text: str,
        now: datetime,
        class_id: UUID | None = None,
    ) -> "Material":
        return cls(
            id=uuid4(),
            owner_id=owner_id,
            class_id=class_id,
            title=normalize_title(title),
            kind=kind,
            source=source,
            text=normalize_text(text),
            created_at=now,
        )

    def visible_to(self, person_id: UUID) -> bool:
        """Samples are for everyone; anything else only for whoever brought it (RNF08)."""
        return self.source is MaterialSource.SAMPLE or self.owner_id == person_id

    def preview(self, length: int = 160) -> str:
        flat = " ".join(self.text.split())
        return flat if len(flat) <= length else flat[: length - 1].rstrip() + "…"
