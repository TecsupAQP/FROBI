"""Public API of materials: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.infrastructure import SqlAlchemyUnitOfWork, SystemClock
from frobi.shared.infrastructure.llm import LlmClient

from .application import (
    ClassContentHandler,
    CreateMaterialHandler,
    GetMaterialHandler,
    GuidesHandler,
    ReadWorkHandler,
    UploadMaterialHandler,
    WorkTexts,
)
from .domain import Material, MaterialKind, MaterialSource, Topic


def get_material_handler(session: AsyncSession) -> GetMaterialHandler:
    """Reads a material the person may see (theirs, a sample or content of their class);
    ``find`` returns None if not."""
    from .infrastructure import (
        ClassroomsActiveClass,
        FileSampleCatalog,
        SqlAlchemyMaterialRepository,
    )

    return GetMaterialHandler(
        SqlAlchemyMaterialRepository(session), FileSampleCatalog(), ClassroomsActiveClass(session)
    )


def read_work_handler(session: AsyncSession) -> ReadWorkHandler:
    """A person's own work with the texts of its brief and draft; None for anyone else."""
    from .infrastructure import SqlAlchemyMaterialRepository, SqlAlchemyWorkRepository

    return ReadWorkHandler(SqlAlchemyWorkRepository(session), SqlAlchemyMaterialRepository(session))


def guides_handler(session: AsyncSession) -> GuidesHandler:
    """The guides a person studies from: their own, their class's content and the samples."""
    from .infrastructure import (
        ClassroomsActiveClass,
        FileSampleCatalog,
        SqlAlchemyMaterialRepository,
    )

    return GuidesHandler(
        SqlAlchemyMaterialRepository(session), FileSampleCatalog(), ClassroomsActiveClass(session)
    )


def class_content_handler(
    session: AsyncSession, llm: LlmClient | None = None, timeout_seconds: float = 15.0
) -> ClassContentHandler:
    """Stores and lists ``class_content``. Classrooms checks who may do it before calling.

    With ``llm``, long texts with no headings are split into topics by the AI."""
    from .application import TopicFinder
    from .infrastructure import (
        LlmTopicSegmenter,
        PypdfTextExtractor,
        SqlAlchemyMaterialRepository,
    )

    repository = SqlAlchemyMaterialRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    clock = SystemClock()
    topics = TopicFinder(None if llm is None else LlmTopicSegmenter(llm, timeout_seconds))
    return ClassContentHandler(
        CreateMaterialHandler(uow, repository, clock, topics),
        UploadMaterialHandler(uow, repository, PypdfTextExtractor(), clock, topics=topics),
        repository,
    )


__all__ = [
    "ClassContentHandler",
    "GetMaterialHandler",
    "GuidesHandler",
    "Material",
    "MaterialKind",
    "MaterialSource",
    "ReadWorkHandler",
    "Topic",
    "WorkTexts",
    "class_content_handler",
    "get_material_handler",
    "guides_handler",
    "read_work_handler",
]
