from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.settings.domain import TOGGLES, IntroStatus, Language, PersonSettings

from .models import PersonSettingsModel


class SqlAlchemySettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, person_id: UUID) -> PersonSettings | None:
        row = await self._session.get(PersonSettingsModel, person_id)
        if row is None:
            return None
        return PersonSettings(
            person_id=row.person_id,
            profiles=tuple(row.profiles),
            enabled=frozenset(t for t in TOGGLES if getattr(row, t)),
            language=Language(row.language),
            intro_status=IntroStatus(row.intro_status),
            onboarding_done=row.onboarding_done,
        )

    async def save(self, settings: PersonSettings) -> None:
        await self._session.merge(
            PersonSettingsModel(
                person_id=settings.person_id,
                profiles=list(settings.profiles),
                language=settings.language.value,
                intro_status=settings.intro_status.value,
                onboarding_done=settings.onboarding_done,
                **{toggle: settings.is_on(toggle) for toggle in TOGGLES},
            )
        )
