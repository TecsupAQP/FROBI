from dataclasses import dataclass
from uuid import UUID

from frobi.modules.materials.domain import MaterialKind


@dataclass(frozen=True, slots=True)
class CreateMaterialCommand:
    owner_id: UUID
    title: str
    kind: MaterialKind
    text: str


@dataclass(frozen=True, slots=True)
class UploadMaterialCommand:
    owner_id: UUID
    title: str
    kind: MaterialKind
    data: bytes
