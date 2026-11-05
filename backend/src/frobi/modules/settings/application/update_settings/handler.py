"""Flip accessibility switches and the language; only what is sent changes (RF50, RF51)."""

from frobi.modules.settings.application.ports import SettingsRepository
from frobi.modules.settings.domain import PersonSettings
from frobi.shared.application import UnitOfWork

from .command import UpdateSettingsCommand


class UpdateSettingsHandler:
    def __init__(self, uow: UnitOfWork, settings: SettingsRepository) -> None:
        self._uow = uow
        self._settings = settings

    async def handle(self, command: UpdateSettingsCommand) -> PersonSettings:
        async with self._uow:
            current = await self._settings.get(command.person_id) or PersonSettings.defaults(
                command.person_id
            )
            updated = current.switch(command.toggles)
            if command.language is not None:
                updated = updated.speak(command.language)
            await self._settings.save(updated)
            await self._uow.commit()
        return updated
