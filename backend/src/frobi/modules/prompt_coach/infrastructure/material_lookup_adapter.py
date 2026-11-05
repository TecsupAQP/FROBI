"""MaterialLookup over the public API of materials."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import materials
from frobi.modules.prompt_coach.application.ports import MaterialContext


class MaterialLookupAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._get = materials.get_material_handler(session)

    async def find(self, person_id: UUID, material_id: UUID) -> MaterialContext | None:
        material = await self._get.find(person_id, material_id)
        return None if material is None else MaterialContext(material.title, material.text)
