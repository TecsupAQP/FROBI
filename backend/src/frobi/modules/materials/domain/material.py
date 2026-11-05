"""Study material: a sample guide, pasted text or an uploaded PDF (RF01, RF02)."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .errors import MAX_TEXT_CHARS, EmptyText, InvalidTitle
from .topics import Topic, TopicSpan, spans_from_boundaries, text_heading_boundaries, topics_of

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


def tidy_text(raw: str) -> str:
    """Trim each line and drop runs of blank lines, keeping paragraphs. Never fails."""
    lines = [" ".join(line.split()) for line in raw.replace("\r\n", "\n").split("\n")]
    paragraphs: list[str] = []
    for line in lines:
        if line or (paragraphs and paragraphs[-1]):
            paragraphs.append(line)
    return "\n".join(paragraphs).strip()


def normalize_text(raw: str) -> str:
    """``tidy_text``, capped, and never empty."""
    text = tidy_text(raw)[:MAX_TEXT_CHARS].strip()
    if not text:
        raise EmptyText()
    return text


def assemble_pages(pages: list[str]) -> tuple[str, tuple[int, ...]]:
    """The material's text from a PDF's pages, and where each page starts in it.

    Pages are tidied one by one and joined by a blank line, so the result is already normal
    (``normalize_text`` leaves it as is) and the offsets stay valid.
    """
    parts: list[str] = []
    offsets: list[int] = []
    length = 0
    for page in pages:
        tidy = tidy_text(page)
        offsets.append(length + (2 if parts and tidy else 0))
        if not tidy:
            continue
        if parts:
            length += 2
        parts.append(tidy)
        length += len(tidy)
        if length >= MAX_TEXT_CHARS:
            break
    text = "\n\n".join(parts)[:MAX_TEXT_CHARS].strip()
    return text, tuple(min(offset, len(text)) for offset in offsets)


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
    # Where the original upload lives in file storage; None for pasted text and samples.
    file_key: str | None = None
    # Where each topic starts and ends in ``text``. Empty for older materials and samples: then
    # ``topics()`` finds them from the headings in the text.
    topic_spans: tuple[TopicSpan, ...] = ()

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
        topic_spans: tuple[TopicSpan, ...] = (),
    ) -> "Material":
        normal = normalize_text(text)
        if normal != text or not topic_spans:
            # No spans, or spans measured on other text: find the topics on this one.
            topic_spans = spans_from_boundaries(normal, text_heading_boundaries(normal))
        return cls(
            id=uuid4(),
            owner_id=owner_id,
            class_id=class_id,
            title=normalize_title(title),
            kind=kind,
            source=source,
            text=normal,
            created_at=now,
            topic_spans=topic_spans,
        )

    def visible_to(self, person_id: UUID, active_class_id: UUID | None = None) -> bool:
        """Samples are for everyone; class content for the class; the rest only for its owner.

        RNF08: a person's own material is never shown to anyone else. Class content is what the
        teacher uploaded for the class, so the people active in that class may read it.
        """
        if self.source is MaterialSource.SAMPLE or self.owner_id == person_id:
            return True
        return (
            self.kind is MaterialKind.CLASS_CONTENT
            and self.class_id is not None
            and self.class_id == active_class_id
        )

    @property
    def has_file(self) -> bool:
        return self.file_key is not None

    def file_key_for_upload(self) -> str:
        return f"materials/{self.owner_id}/{self.id}.pdf"

    def topics(self) -> tuple[Topic, ...]:
        spans = self.topic_spans or spans_from_boundaries(
            self.text, text_heading_boundaries(self.text)
        )
        return topics_of(self.text, spans)

    def topic(self, position: int | None) -> Topic | None:
        """Topic ``position`` (from 1); the first one when None."""
        topics = self.topics()
        index = 0 if position is None else position - 1
        return topics[index] if 0 <= index < len(topics) else None

    def preview(self, length: int = 160) -> str:
        flat = " ".join(self.text.split())
        return flat if len(flat) <= length else flat[: length - 1].rstrip() + "…"
