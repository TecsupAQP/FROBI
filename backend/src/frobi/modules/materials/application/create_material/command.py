from dataclasses import dataclass
from uuid import UUID

from frobi.modules.materials.domain import MaterialKind


@dataclass(frozen=True, slots=True)
class CreateMaterialCommand:
    owner_id: UUID
    title: str
    kind: MaterialKind
    text: str
    class_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class UploadMaterialCommand:
    owner_id: UUID
    title: str
    kind: MaterialKind
    data: bytes
    class_id: UUID | None = None
