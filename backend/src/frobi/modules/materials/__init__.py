"""Public API of materials: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.infrastructure import SqlAlchemyUnitOfWork, SystemClock
from frobi.shared.infrastructure.llm import PdfTranscriber

from .application import (
    ClassContentHandler,
    CreateMaterialHandler,
    GetMaterialHandler,
    GuidesHandler,
    ReadWorkHandler,
    UploadMaterialHandler,
    WorkTexts,
)
from .domain import Material, MaterialKind, MaterialSource


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
    session: AsyncSession, transcriber: PdfTranscriber | None = None
) -> ClassContentHandler:
    """Stores and lists ``class_content``. Classrooms checks who may do it before calling."""
    from .infrastructure import PypdfTextExtractor, SqlAlchemyMaterialRepository

    repository = SqlAlchemyMaterialRepository(session)
    uow = SqlAlchemyUnitOfWork(session)
    clock = SystemClock()
    return ClassContentHandler(
        CreateMaterialHandler(uow, repository, clock),
        UploadMaterialHandler(uow, repository, PypdfTextExtractor(transcriber), clock),
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
    "WorkTexts",
    "class_content_handler",
    "get_material_handler",
    "guides_handler",
    "read_work_handler",
]
