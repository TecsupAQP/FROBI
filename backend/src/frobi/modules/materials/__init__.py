"""Public API of materials: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from .application import GetMaterialHandler
from .domain import Material, MaterialKind, MaterialSource


def get_material_handler(session: AsyncSession) -> GetMaterialHandler:
    """Reads a material the person may see (theirs or a sample); ``find`` returns None if not."""
    from .infrastructure import FileSampleCatalog, SqlAlchemyMaterialRepository

    return GetMaterialHandler(SqlAlchemyMaterialRepository(session), FileSampleCatalog())


__all__ = [
    "GetMaterialHandler",
    "Material",
    "MaterialKind",
    "MaterialSource",
    "get_material_handler",
]
