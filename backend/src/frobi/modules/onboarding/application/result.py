from dataclasses import dataclass

from frobi.modules.onboarding.application.ports import IntroStatus, SettingsSnapshot
from frobi.modules.onboarding.domain import WhoUses


@dataclass(frozen=True, slots=True)
class OnboardingResult:
    done: bool
    configured_by: WhoUses
    profiles: tuple[str, ...]
    enabled_settings: tuple[str, ...]
    intro_status: IntroStatus

    @classmethod
    def of(cls, who: WhoUses, snapshot: SettingsSnapshot) -> "OnboardingResult":
        return cls(
            done=snapshot.done,
            configured_by=who,
            profiles=snapshot.profiles,
            enabled_settings=snapshot.enabled,
            intro_status=snapshot.intro_status,
        )
