"""OnboardingStatusReader over the public API of settings (where the wizard state is stored)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.identity.application.ports import OnboardingStatus
from frobi.modules.settings import get_settings_handler


class SettingsOnboardingStatus:
    def __init__(self, session: AsyncSession) -> None:
        self._get_settings = get_settings_handler(session)

    async def for_person(self, person_id: UUID) -> OnboardingStatus:
        settings = await self._get_settings.handle(person_id)
        return OnboardingStatus(
            done=settings.onboarding_done, intro_status=settings.intro_status.value
        )
