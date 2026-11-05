"""TutoringContextReader over the public APIs of adaptations and materials."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import adaptations, materials
from frobi.modules.tutoring.application.ports import TutoringContext


class TutoringContextReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._adaptations = adaptations.get_adaptation_handler(session)
        self._materials = materials.get_material_handler(session)

    async def get(self, person_id: UUID, adaptation_id: UUID) -> TutoringContext | None:
        adaptation = await self._adaptations.find(person_id, adaptation_id)
        if adaptation is None:
            return None
        material = await self._materials.find(person_id, adaptation.material_id)
        if material is None:
            return None
        return TutoringContext(
            adaptation_id=adaptation.id,
            material_title=material.title,
            material_text=material.text,
            adapted_text=adaptation.content.plain_text(),
        )
