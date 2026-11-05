"""Wiring: builds onboarding's handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.onboarding.application import (
    CompleteOnboardingHandler,
    ResetOnboardingHandler,
    SkipOnboardingHandler,
)
from frobi.modules.onboarding.infrastructure import (
    PersonConfiguratorAdapter,
    SettingsWriterAdapter,
)
from frobi.shared.presentation import get_db_session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_complete_onboarding(db: DbSession) -> CompleteOnboardingHandler:
    return CompleteOnboardingHandler(SettingsWriterAdapter(db), PersonConfiguratorAdapter(db))


def get_skip_onboarding(db: DbSession) -> SkipOnboardingHandler:
    return SkipOnboardingHandler(SettingsWriterAdapter(db), PersonConfiguratorAdapter(db))


def get_reset_onboarding(db: DbSession) -> ResetOnboardingHandler:
    return ResetOnboardingHandler(SettingsWriterAdapter(db), PersonConfiguratorAdapter(db))
