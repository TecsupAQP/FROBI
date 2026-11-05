"""Public API of adaptations: the only thing other modules' adapters may import."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.shared.application import FormatUse, GuideAdaptation

from .application import GetAdaptationHandler
from .domain import Adaptation, AdaptedContent, Format, Recipe


def get_adaptation_handler(session: AsyncSession) -> GetAdaptationHandler:
    """Reads an adaptation its owner may see; ``find`` returns None otherwise."""
    from .infrastructure import SqlAlchemyAdaptationRepository

    return GetAdaptationHandler(SqlAlchemyAdaptationRepository(session))


async def format_uses_in_class(session: AsyncSession, class_id: UUID) -> list[FormatUse]:
    """Adaptations made inside this class only (RNF16)."""
    from .infrastructure.activity_queries import format_uses_in_class as query

    return await query(session, class_id)


async def guide_adaptations_in_class(
    session: AsyncSession, class_id: UUID
) -> list[GuideAdaptation]:
    """Which guide each adaptation made inside this class adapted (RNF16)."""
    from .infrastructure.activity_queries import guide_adaptations_in_class as query

    return await query(session, class_id)


async def format_uses_of_person(session: AsyncSession, person_id: UUID) -> list[FormatUse]:
    from .infrastructure.activity_queries import format_uses_of_person as query

    return await query(session, person_id)


async def latest_recipe_of_person(session: AsyncSession, person_id: UUID) -> Recipe | None:
    from .infrastructure.activity_queries import latest_recipe_of_person as query

    return await query(session, person_id)


__all__ = [
    "Adaptation",
    "AdaptedContent",
    "Format",
    "GetAdaptationHandler",
    "Recipe",
    "format_uses_in_class",
    "format_uses_of_person",
    "get_adaptation_handler",
    "guide_adaptations_in_class",
    "latest_recipe_of_person",
]
