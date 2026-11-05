from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from frobi.modules.onboarding.domain import AccessibilityProfile, WhoUses


@dataclass(frozen=True, slots=True)
class CompleteOnboardingCommand:
    person_id: UUID
    who_uses: WhoUses
    profiles: tuple[AccessibilityProfile, ...]
    intro: Literal["seen", "skipped"]
