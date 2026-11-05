"""Store the result of the onboarding wizard. Called by the onboarding module (public API)."""

from frobi.modules.settings.application.ports import SettingsRepository
from frobi.modules.settings.domain import PersonSettings
from frobi.shared.application import UnitOfWork

from .command import ApplyOnboardingCommand


class ApplyOnboardingHandler:
    def __init__(self, uow: UnitOfWork, settings: SettingsRepository) -> None:
        self._uow = uow
        self._settings = settings

    async def handle(self, command: ApplyOnboardingCommand) -> PersonSettings:
        async with self._uow:
            current = await self._settings.get(command.person_id) or PersonSettings.defaults(
                command.person_id
            )
            updated = current.after_onboarding(
                profiles=command.profiles,
                enabled=current.enabled if command.enabled is None else command.enabled,
                intro_status=command.intro_status,
                done=command.done,
            )
            await self._settings.save(updated)
            await self._uow.commit()
        return updated
