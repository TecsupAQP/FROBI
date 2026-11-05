"""What onboarding needs from other modules, in its own words."""

from dataclasses import dataclass
from typing import Literal, Protocol
from uuid import UUID

from frobi.modules.onboarding.domain import WhoUses

IntroStatus = Literal["seen", "skipped", "pending"]


@dataclass(frozen=True, slots=True)
class SettingsSnapshot:
    profiles: tuple[str, ...]
    enabled: tuple[str, ...]
    intro_status: IntroStatus
    done: bool


class SettingsWriter(Protocol):
    """Implemented over the public API of settings."""

    async def record(
        self,
        person_id: UUID,
        *,
        profiles: tuple[str, ...],
        enabled: tuple[str, ...] | None,
        intro_status: IntroStatus,
        done: bool,
    ) -> SettingsSnapshot:
        """Store the wizard result. ``enabled=None`` keeps the current switches."""
        ...


class PersonConfigurator(Protocol):
    """Implemented over the public API of identity."""

    async def configured_by(self, person_id: UUID) -> WhoUses: ...

    async def set_configured_by(self, person_id: UUID, who: WhoUses) -> None: ...


__all__ = ["IntroStatus", "PersonConfigurator", "SettingsSnapshot", "SettingsWriter"]
