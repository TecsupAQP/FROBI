from uuid import UUID

from frobi.modules.onboarding.application.ports import IntroStatus, SettingsSnapshot
from frobi.modules.onboarding.domain import WhoUses


class FakeSettingsWriter:
    def __init__(self, enabled: tuple[str, ...] = ()) -> None:
        self.enabled = enabled
        self.calls: list[dict[str, object]] = []

    async def record(
        self,
        person_id: UUID,
        *,
        profiles: tuple[str, ...],
        enabled: tuple[str, ...] | None,
        intro_status: IntroStatus,
        done: bool,
    ) -> SettingsSnapshot:
        self.calls.append(
            {"profiles": profiles, "enabled": enabled, "intro": intro_status, "done": done}
        )
        if enabled is not None:
            self.enabled = enabled
        return SettingsSnapshot(
            profiles=profiles, enabled=self.enabled, intro_status=intro_status, done=done
        )


class FakePersonConfigurator:
    def __init__(self) -> None:
        self.by: dict[UUID, WhoUses] = {}

    async def configured_by(self, person_id: UUID) -> WhoUses:
        return self.by.get(person_id, WhoUses.SELF)

    async def set_configured_by(self, person_id: UUID, who: WhoUses) -> None:
        self.by[person_id] = who
