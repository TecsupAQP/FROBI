"""Onboarding's ports implemented over the public APIs of settings and identity."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import identity, settings
from frobi.modules.onboarding.application.ports import IntroStatus, SettingsSnapshot
from frobi.modules.onboarding.domain import WhoUses


class SettingsWriterAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._apply = settings.apply_onboarding_handler(session)

    async def record(
        self,
        person_id: UUID,
        *,
        profiles: tuple[str, ...],
        enabled: tuple[str, ...] | None,
        intro_status: IntroStatus,
        done: bool,
    ) -> SettingsSnapshot:
        stored = await self._apply.handle(
            settings.ApplyOnboardingCommand(
                person_id=person_id,
                profiles=profiles,
                enabled=None if enabled is None else frozenset(enabled),
                intro_status=settings.IntroStatus(intro_status),
                done=done,
            )
        )
        return SettingsSnapshot(
            profiles=stored.profiles,
            enabled=tuple(stored.enabled_in_order()),
            intro_status=stored.intro_status.value,
            done=stored.onboarding_done,
        )


class PersonConfiguratorAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._configure = identity.configure_person_handler(session)

    async def configured_by(self, person_id: UUID) -> WhoUses:
        return WhoUses((await self._configure.configured_by(person_id)).value)

    async def set_configured_by(self, person_id: UUID, who: WhoUses) -> None:
        await self._configure.set_configured_by(person_id, identity.ConfiguredBy(who.value))
