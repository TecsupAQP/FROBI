from dataclasses import dataclass
from uuid import UUID

from frobi.modules.adaptations.domain import Format


@dataclass(frozen=True, slots=True)
class CreateAdaptationCommand:
    person_id: UUID
    class_id: UUID | None
    material_id: UUID
    format: Format
