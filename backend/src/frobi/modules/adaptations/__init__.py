"""Public API of adaptations: the only thing other modules' adapters may import."""

from sqlalchemy.ext.asyncio import AsyncSession

from .application import GetAdaptationHandler
from .domain import Adaptation, AdaptedContent, Format, Recipe


def get_adaptation_handler(session: AsyncSession) -> GetAdaptationHandler:
    """Reads an adaptation its owner may see; ``find`` returns None otherwise."""
    from .infrastructure import SqlAlchemyAdaptationRepository

    return GetAdaptationHandler(SqlAlchemyAdaptationRepository(session))


__all__ = [
    "Adaptation",
    "AdaptedContent",
    "Format",
    "GetAdaptationHandler",
    "Recipe",
    "get_adaptation_handler",
]
