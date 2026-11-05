"""Public API of materials: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from .application import GetMaterialHandler, GuidesHandler, ReadWorkHandler, WorkTexts
from .domain import Material, MaterialKind, MaterialSource


def get_material_handler(session: AsyncSession) -> GetMaterialHandler:
    """Reads a material the person may see (theirs or a sample); ``find`` returns None if not."""
    from .infrastructure import FileSampleCatalog, SqlAlchemyMaterialRepository

    return GetMaterialHandler(SqlAlchemyMaterialRepository(session), FileSampleCatalog())


def read_work_handler(session: AsyncSession) -> ReadWorkHandler:
    """A person's own work with the texts of its brief and draft; None for anyone else."""
    from .infrastructure import SqlAlchemyMaterialRepository, SqlAlchemyWorkRepository

    return ReadWorkHandler(SqlAlchemyWorkRepository(session), SqlAlchemyMaterialRepository(session))


def guides_handler(session: AsyncSession) -> GuidesHandler:
    """The guides a person studies from: their own ``guide`` materials and the samples."""
    from .infrastructure import FileSampleCatalog, SqlAlchemyMaterialRepository

    return GuidesHandler(SqlAlchemyMaterialRepository(session), FileSampleCatalog())


__all__ = [
    "GetMaterialHandler",
    "GuidesHandler",
    "Material",
    "MaterialKind",
    "MaterialSource",
    "ReadWorkHandler",
    "WorkTexts",
    "get_material_handler",
    "guides_handler",
    "read_work_handler",
]
