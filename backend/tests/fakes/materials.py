from datetime import UTC, datetime
from uuid import UUID

from frobi.modules.materials.application.ports import FileStorageUnavailable
from frobi.modules.materials.domain import (
    Material,
    MaterialKind,
    MaterialSource,
    PdfUnreadable,
    Work,
)

SAMPLE = Material(
    id=UUID("00000000-0000-4000-8000-00000000a001"),
    owner_id=None,
    class_id=None,
    title="Guía de sensores",
    kind=MaterialKind.GUIDE,
    source=MaterialSource.SAMPLE,
    text="Los sensores inductivos detectan metales sin contacto.",
    created_at=datetime(2026, 11, 4, tzinfo=UTC),
)


class InMemoryMaterials:
    def __init__(self) -> None:
        self.items: dict[UUID, Material] = {}

    async def add(self, material: Material) -> None:
        self.items[material.id] = material

    async def get(self, material_id: UUID) -> Material | None:
        return self.items.get(material_id)

    async def list_for_owner(self, owner_id: UUID, kind: MaterialKind) -> list[Material]:
        return [m for m in self.items.values() if m.owner_id == owner_id and m.kind is kind]

    async def list_for_class(self, class_id: UUID) -> list[Material]:
        return [
            m
            for m in self.items.values()
            if m.class_id == class_id and m.kind is MaterialKind.CLASS_CONTENT
        ]


class StaticSamples:
    def list(self) -> list[Material]:
        return [SAMPLE]

    def get(self, material_id: UUID) -> Material | None:
        return SAMPLE if material_id == SAMPLE.id else None


class InMemoryWorks:
    def __init__(self) -> None:
        self.items: list[Work] = []

    async def add(self, work: Work) -> None:
        self.items.append(work)

    async def get(self, work_id: UUID) -> Work | None:
        return next((w for w in self.items if w.id == work_id), None)


class FakeExtractor:
    """Returns the bytes as text; ``b"%BROKEN"`` behaves like an unreadable PDF."""

    async def extract(self, data: bytes) -> str:
        if data.startswith(b"%BROKEN"):
            raise PdfUnreadable()
        return data.decode("utf-8")


class FixedClassContext:
    """``ClassContext`` with a fixed person → class map."""

    def __init__(self, active: dict[UUID, UUID] | None = None) -> None:
        self.active = active or {}

    async def active_class(self, person_id: UUID) -> UUID | None:
        return self.active.get(person_id)


class InMemoryFileStorage:
    """``FileStorage`` in a dict; ``broken=True`` behaves like R2 being down."""

    def __init__(self, *, broken: bool = False) -> None:
        self.files: dict[str, bytes] = {}
        self.broken = broken

    async def put(self, key: str, data: bytes, content_type: str) -> None:
        if self.broken:
            raise FileStorageUnavailable("down")
        self.files[key] = data

    async def delete(self, key: str) -> None:
        self.files.pop(key, None)

    def signed_url(self, key: str, *, expires_in: int, filename: str) -> str:
        return f"https://files.test/{key}?expires={expires_in}"
