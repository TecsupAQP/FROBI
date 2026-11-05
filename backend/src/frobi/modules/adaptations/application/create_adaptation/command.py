from dataclasses import dataclass
from uuid import UUID

from frobi.modules.adaptations.domain import Format


@dataclass(frozen=True, slots=True)
class CreateAdaptationCommand:
    person_id: UUID
    class_id: UUID | None
    material_id: UUID
    format: Format
    # Topic of the material (from 1); the first one when None.
    topic: int | None = None
