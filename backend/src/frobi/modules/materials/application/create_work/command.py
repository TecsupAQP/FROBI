from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateWorkCommand:
    person_id: UUID
    brief_material_id: UUID
    draft_material_id: UUID
