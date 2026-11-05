"""Finish the wizard: who uses FROBI, chosen profiles and their switches, AI intro (RF34-RF37)."""

from frobi.modules.onboarding.application.ports import PersonConfigurator, SettingsWriter
from frobi.modules.onboarding.application.result import OnboardingResult
from frobi.modules.onboarding.domain import settings_for, unique_profiles

from .command import CompleteOnboardingCommand


class CompleteOnboardingHandler:
    def __init__(self, settings: SettingsWriter, persons: PersonConfigurator) -> None:
        self._settings = settings
        self._persons = persons

    async def handle(self, command: CompleteOnboardingCommand) -> OnboardingResult:
        profiles = unique_profiles(command.profiles)
        await self._persons.set_configured_by(command.person_id, command.who_uses)
        snapshot = await self._settings.record(
            command.person_id,
            profiles=tuple(profile.value for profile in profiles),
            enabled=tuple(setting.value for setting in settings_for(profiles)),
            intro_status=command.intro,
            done=True,
        )
        return OnboardingResult.of(command.who_uses, snapshot)
