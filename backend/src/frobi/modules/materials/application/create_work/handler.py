"""Put a brief and a draft side by side: requirements, topics and what is missing (RF18)."""

from frobi.modules.materials.application.get_material import GetMaterialHandler
from frobi.modules.materials.application.ports import WorkRepository
from frobi.modules.materials.domain import MaterialKind, Work, WrongKind
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock

from .command import CreateWorkCommand


class CreateWorkHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        materials: GetMaterialHandler,
        works: WorkRepository,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._materials = materials
        self._works = works
        self._clock = clock

    async def handle(self, command: CreateWorkCommand) -> Work:
        brief = await self._materials.handle(command.person_id, command.brief_material_id)
        draft = await self._materials.handle(command.person_id, command.draft_material_id)
        if brief.kind is not MaterialKind.BRIEF or draft.kind is not MaterialKind.DRAFT:
            raise WrongKind()
        work = Work.create(
            person_id=command.person_id,
            brief_material_id=brief.id,
            draft_material_id=draft.id,
            brief_text=brief.text,
            draft_text=draft.text,
            now=self._clock.now(),
        )
        async with self._uow:
            await self._works.add(work)
            await self._uow.commit()
        return work
