"""Wiring: builds materials' handlers with their adapters for each request."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.materials.application import (
    CreateMaterialHandler,
    CreateWorkHandler,
    GetMaterialFileHandler,
    GetMaterialHandler,
    GuidesHandler,
    ListSamplesHandler,
    TopicFinder,
    UploadMaterialHandler,
)
from frobi.modules.materials.infrastructure import (
    ClassroomsActiveClass,
    FileSampleCatalog,
    LlmTopicSegmenter,
    PypdfTextExtractor,
    R2FileStorage,
    SqlAlchemyMaterialRepository,
    SqlAlchemyWorkRepository,
)
from frobi.shared.domain import Clock
from frobi.shared.infrastructure import Settings, SqlAlchemyUnitOfWork
from frobi.shared.infrastructure.llm import LlmClient
from frobi.shared.presentation import get_clock, get_db_session, get_llm, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
AppClock = Annotated[Clock, Depends(get_clock)]
AppSettings = Annotated[Settings, Depends(get_settings)]
Llm = Annotated[LlmClient, Depends(get_llm)]


def get_topic_finder(llm: Llm, settings: AppSettings) -> TopicFinder:
    """Structure first; the AI only reads the skeleton of long texts with no structure."""
    return TopicFinder(LlmTopicSegmenter(llm, settings.llm_timeout_seconds))


Topics = Annotated[TopicFinder, Depends(get_topic_finder)]


def get_file_storage(settings: AppSettings) -> R2FileStorage | None:
    """Cloudflare R2 when its keys are set; otherwise uploads keep only their text."""
    if not (settings.r2_endpoint and settings.r2_access_key_id and settings.r2_secret_access_key):
        return None
    return R2FileStorage(
        endpoint=settings.r2_endpoint,
        access_key_id=settings.r2_access_key_id,
        secret_access_key=settings.r2_secret_access_key.get_secret_value(),
        bucket=settings.r2_bucket,
    )


FileStorageDep = Annotated[R2FileStorage | None, Depends(get_file_storage)]


def get_list_samples() -> ListSamplesHandler:
    return ListSamplesHandler(FileSampleCatalog())


def get_guides(db: DbSession) -> GuidesHandler:
    return GuidesHandler(SqlAlchemyMaterialRepository(db), FileSampleCatalog())


def get_get_material(db: DbSession) -> GetMaterialHandler:
    return GetMaterialHandler(
        SqlAlchemyMaterialRepository(db), FileSampleCatalog(), ClassroomsActiveClass(db)
    )


def get_create_material(db: DbSession, clock: AppClock, topics: Topics) -> CreateMaterialHandler:
    return CreateMaterialHandler(
        SqlAlchemyUnitOfWork(db), SqlAlchemyMaterialRepository(db), clock, topics
    )


def get_material_file(
    db: DbSession, storage: FileStorageDep, settings: AppSettings
) -> GetMaterialFileHandler:
    return GetMaterialFileHandler(get_get_material(db), storage, settings.r2_signed_url_seconds)


def get_upload_material(
    db: DbSession, clock: AppClock, storage: FileStorageDep, topics: Topics
) -> UploadMaterialHandler:
    return UploadMaterialHandler(
        SqlAlchemyUnitOfWork(db),
        SqlAlchemyMaterialRepository(db),
        PypdfTextExtractor(),
        clock,
        storage,
        topics,
    )


def get_create_work(db: DbSession, clock: AppClock) -> CreateWorkHandler:
    return CreateWorkHandler(
        SqlAlchemyUnitOfWork(db),
        GetMaterialHandler(SqlAlchemyMaterialRepository(db), FileSampleCatalog()),
        SqlAlchemyWorkRepository(db),
        clock,
    )
