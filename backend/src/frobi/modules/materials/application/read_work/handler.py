"""Read-only views used by other modules through the public API (claim review, M9)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.materials.application.ports import (
    MaterialRepository,
    SampleCatalog,
    WorkRepository,
)
from frobi.modules.materials.domain import Material, MaterialKind


@dataclass(frozen=True, slots=True)
class WorkTexts:
    work_id: UUID
    person_id: UUID
    brief_text: str
    draft_title: str
    draft_text: str


class ReadWorkHandler:
    def __init__(self, works: WorkRepository, materials: MaterialRepository) -> None:
        self._works = works
        self._materials = materials

    async def find(self, person_id: UUID, work_id: UUID) -> WorkTexts | None:
        work = await self._works.get(work_id)
        if work is None or work.person_id != person_id:
            return None
        brief = await self._materials.get(work.brief_material_id)
        draft = await self._materials.get(work.draft_material_id)
        if brief is None or draft is None:
            return None
        return WorkTexts(
            work_id=work.id,
            person_id=work.person_id,
            brief_text=brief.text,
            draft_title=draft.title,
            draft_text=draft.text,
        )


class GuidesHandler:
    """The guides a person studies from: their own ``guide`` materials and the sample guides."""

    def __init__(self, materials: MaterialRepository, samples: SampleCatalog) -> None:
        self._materials = materials
        self._samples = samples

    async def for_person(self, person_id: UUID) -> list[Material]:
        own = await self._materials.list_for_owner(person_id, MaterialKind.GUIDE)
        return [*own, *self._samples.list()]
