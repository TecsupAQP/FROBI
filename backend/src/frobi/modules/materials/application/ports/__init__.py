from typing import Protocol
from uuid import UUID

from frobi.modules.materials.domain import Material, Work


class MaterialRepository(Protocol):
    async def add(self, material: Material) -> None: ...

    async def get(self, material_id: UUID) -> Material | None: ...


class SampleCatalog(Protocol):
    """Example guides shipped with FROBI (RF01). Read-only and visible to everyone."""

    def list(self) -> list[Material]: ...

    def get(self, material_id: UUID) -> Material | None: ...


class WorkRepository(Protocol):
    async def add(self, work: Work) -> None: ...


class PdfTextExtractor(Protocol):
    async def extract(self, data: bytes) -> str:
        """Plain text of the PDF. Raises PdfUnreadable when there is none to get."""
        ...


__all__ = ["MaterialRepository", "PdfTextExtractor", "SampleCatalog", "WorkRepository"]
