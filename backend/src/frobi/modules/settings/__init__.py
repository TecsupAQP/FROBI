"""Public API of settings: the only thing other modules' adapters may import.

Factories take the request's AsyncSession so the caller does not need settings' internals.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.infrastructure import SqlAlchemyUnitOfWork

from .application import ApplyOnboardingCommand, ApplyOnboardingHandler, GetSettingsHandler
from .domain import IntroStatus, PersonSettings
from .infrastructure import SqlAlchemySettingsRepository


def get_settings_handler(session: AsyncSession) -> GetSettingsHandler:
    return GetSettingsHandler(SqlAlchemySettingsRepository(session))


def apply_onboarding_handler(session: AsyncSession) -> ApplyOnboardingHandler:
    return ApplyOnboardingHandler(
        SqlAlchemyUnitOfWork(session), SqlAlchemySettingsRepository(session)
    )


__all__ = [
    "ApplyOnboardingCommand",
    "ApplyOnboardingHandler",
    "GetSettingsHandler",
    "IntroStatus",
    "PersonSettings",
    "apply_onboarding_handler",
    "get_settings_handler",
]
