"""See an adaptation again (RF05). Only its owner can. Also part of the public API."""

from uuid import UUID

from frobi.modules.adaptations.application.ports import AdaptationRepository
from frobi.modules.adaptations.domain import Adaptation, AdaptationNotFound


class GetAdaptationHandler:
    def __init__(self, adaptations: AdaptationRepository) -> None:
        self._adaptations = adaptations

    async def find(self, person_id: UUID, adaptation_id: UUID) -> Adaptation | None:
        adaptation = await self._adaptations.get(adaptation_id)
        if adaptation is None or not adaptation.visible_to(person_id):
            return None
        return adaptation

    async def handle(self, person_id: UUID, adaptation_id: UUID) -> Adaptation:
        adaptation = await self.find(person_id, adaptation_id)
        if adaptation is None:
            raise AdaptationNotFound()
        return adaptation
