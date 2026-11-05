from dataclasses import dataclass
from uuid import UUID

from frobi.modules.settings.domain import IntroStatus


@dataclass(frozen=True, slots=True)
class ApplyOnboardingCommand:
    """What the wizard decided.

    ``enabled`` is ``None`` to keep the current switches (skip, reset), or the exact set of
    switches the chosen profiles turn on.
    """

    person_id: UUID
    profiles: tuple[str, ...]
    enabled: frozenset[str] | None
    intro_status: IntroStatus
    done: bool
