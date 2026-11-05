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


class PdfTextExtractor(Protocol):
    async def extract(self, data: bytes) -> str:
        """Plain text of the PDF. Raises PdfUnreadable when there is none to get."""
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
    "PdfTextExtractor",
    "SampleCatalog",
    "WorkRepository",
]
