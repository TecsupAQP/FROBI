from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.modules.materials.domain import Material, MaterialKind, Work


class MaterialRepository(Protocol):
    async def add(self, material: Material) -> None: ...

    async def get(self, material_id: UUID) -> Material | None: ...

    async def list_for_owner(self, owner_id: UUID, kind: MaterialKind) -> list[Material]: ...

    async def list_for_class(self, class_id: UUID) -> list[Material]:
        """The `class_content` of a class, most recent first."""
        ...


class SampleCatalog(Protocol):
    """Example guides shipped with FROBI (RF01). Read-only and visible to everyone."""

    def list(self) -> list[Material]: ...

    def get(self, material_id: UUID) -> Material | None: ...


class WorkRepository(Protocol):
    async def add(self, work: Work) -> None: ...

    async def get(self, work_id: UUID) -> Work | None: ...


@dataclass(frozen=True, slots=True)
class OutlineEntry:
    """A bookmark of the PDF: its title, the page it opens (from 0) and its depth (0 = top)."""

    title: str
    page: int
    level: int


@dataclass(frozen=True, slots=True)
class PdfContent:
    pages: tuple[str, ...]
    outline: tuple[OutlineEntry, ...] = ()
    # (page, line) written clearly bigger than the body text: likely headings.
    headings: tuple[tuple[int, str], ...] = ()
    # False when the text is not split by real pages (a scan transcribed as one text).
    paginated: bool = True


class PdfTextExtractor(Protocol):
    async def extract(self, data: bytes) -> PdfContent:
        """Text of each page plus its structure. Raises PdfUnreadable when there is none."""
        ...


class TopicSegmenter(Protocol):
    """Finds topics in a long text with no structure, reading only its skeleton."""

    async def segment(self, title: str, blocks: Sequence[str]) -> list[tuple[int, str]] | None:
        """(block index, topic title) where each topic starts; None when it cannot tell."""
        ...


class FileStorageUnavailable(Exception):
    """The storage did not take or give the file. Uploads still keep their text."""


class FileStorage(Protocol):
    """Original uploaded files (the PDF), private to whoever may see the material."""

    async def put(self, key: str, data: bytes, content_type: str) -> None: ...

    async def delete(self, key: str) -> None: ...

    def signed_url(self, key: str, *, expires_in: int, filename: str) -> str:
        """A temporary URL the browser can open without FROBI's token."""
        ...


__all__ = [
    "FileStorage",
    "FileStorageUnavailable",
    "MaterialRepository",
    "OutlineEntry",
    "PdfContent",
    "PdfTextExtractor",
    "SampleCatalog",
    "TopicSegmenter",
    "WorkRepository",
]
