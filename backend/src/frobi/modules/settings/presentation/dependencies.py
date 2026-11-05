"""Wiring: builds settings' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.settings.application import GetSettingsHandler, UpdateSettingsHandler
from frobi.modules.settings.infrastructure import SqlAlchemySettingsRepository
from frobi.shared.infrastructure import SqlAlchemyUnitOfWork
from frobi.shared.presentation import get_db_session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_get_settings(db: DbSession) -> GetSettingsHandler:
    return GetSettingsHandler(SqlAlchemySettingsRepository(db))


def get_update_settings(db: DbSession) -> UpdateSettingsHandler:
    return UpdateSettingsHandler(SqlAlchemyUnitOfWork(db), SqlAlchemySettingsRepository(db))
