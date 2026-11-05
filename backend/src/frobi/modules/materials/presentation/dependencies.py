"""Wiring: builds materials' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.materials.application import (
    CreateMaterialHandler,
    CreateWorkHandler,
    GetMaterialHandler,
    ListSamplesHandler,
    UploadMaterialHandler,
)
from frobi.modules.materials.infrastructure import (
    ClassroomsActiveClass,
    FileSampleCatalog,
    PypdfTextExtractor,
    SqlAlchemyMaterialRepository,
    SqlAlchemyWorkRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import SqlAlchemyUnitOfWork
from frobi.shared.presentation import get_clock, get_db_session

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
AppClock = Annotated[Clock, Depends(get_clock)]


def get_list_samples() -> ListSamplesHandler:
    return ListSamplesHandler(FileSampleCatalog())


def get_get_material(db: DbSession) -> GetMaterialHandler:
    return GetMaterialHandler(
        SqlAlchemyMaterialRepository(db), FileSampleCatalog(), ClassroomsActiveClass(db)
    )


def get_create_material(db: DbSession, clock: AppClock) -> CreateMaterialHandler:
    return CreateMaterialHandler(SqlAlchemyUnitOfWork(db), SqlAlchemyMaterialRepository(db), clock)


def get_upload_material(db: DbSession, clock: AppClock) -> UploadMaterialHandler:
    return UploadMaterialHandler(
        SqlAlchemyUnitOfWork(db), SqlAlchemyMaterialRepository(db), PypdfTextExtractor(), clock
    )


def get_create_work(db: DbSession, clock: AppClock) -> CreateWorkHandler:
    return CreateWorkHandler(
        SqlAlchemyUnitOfWork(db),
        GetMaterialHandler(SqlAlchemyMaterialRepository(db), FileSampleCatalog()),
        SqlAlchemyWorkRepository(db),
        clock,
    )
