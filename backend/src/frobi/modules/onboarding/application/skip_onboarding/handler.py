"""Skip the wizard (RF34) or start it again (RF38). Neither touches the current switches."""

from uuid import UUID

from frobi.modules.onboarding.application.ports import PersonConfigurator, SettingsWriter
from frobi.modules.onboarding.application.result import OnboardingResult


class SkipOnboardingHandler:
    def __init__(self, settings: SettingsWriter, persons: PersonConfigurator) -> None:
        self._settings = settings
        self._persons = persons

    async def handle(self, person_id: UUID) -> OnboardingResult:
        who = await self._persons.configured_by(person_id)
        snapshot = await self._settings.record(
            person_id, profiles=(), enabled=None, intro_status="skipped", done=True
        )
        return OnboardingResult.of(who, snapshot)


class ResetOnboardingHandler:
    def __init__(self, settings: SettingsWriter, persons: PersonConfigurator) -> None:
        self._settings = settings
        self._persons = persons

    async def handle(self, person_id: UUID) -> OnboardingResult:
        who = await self._persons.configured_by(person_id)
        snapshot = await self._settings.record(
            person_id, profiles=(), enabled=None, intro_status="pending", done=False
        )
        return OnboardingResult.of(who, snapshot)
