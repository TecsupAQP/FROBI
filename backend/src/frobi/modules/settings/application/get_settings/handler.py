"""Current settings; a person who never changed anything gets the defaults (RF51)."""

from uuid import UUID

from frobi.modules.settings.application.ports import SettingsRepository
from frobi.modules.settings.domain import PersonSettings


class GetSettingsHandler:
    def __init__(self, settings: SettingsRepository) -> None:
        self._settings = settings

    async def handle(self, person_id: UUID) -> PersonSettings:
        return await self._settings.get(person_id) or PersonSettings.defaults(person_id)
