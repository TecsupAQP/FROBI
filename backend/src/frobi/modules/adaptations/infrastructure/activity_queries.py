"""Activity of adaptations for progress and the teacher panel (see shared.application.activity)."""

from uuid import UUID

from sqlalchemy import ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.adaptations.domain import Format, Recipe
from frobi.shared.application import FormatUse, GuideAdaptation

from .models import AdaptationModel


async def _uses(session: AsyncSession, where: ColumnElement[bool]) -> list[FormatUse]:
    query = (
        select(AdaptationModel.person_id, AdaptationModel.format, AdaptationModel.created_at)
        .where(where)
        .order_by(AdaptationModel.created_at)
    )
    return [
        FormatUse(row.person_id, row.format, row.created_at) for row in await session.execute(query)
    ]


async def format_uses_in_class(session: AsyncSession, class_id: UUID) -> list[FormatUse]:
    return await _uses(session, AdaptationModel.class_id == class_id)


async def format_uses_of_person(session: AsyncSession, person_id: UUID) -> list[FormatUse]:
    return await _uses(session, AdaptationModel.person_id == person_id)


async def latest_recipe_of_person(session: AsyncSession, person_id: UUID) -> Recipe | None:
    recipe = await session.scalar(
        select(AdaptationModel.recipe)
        .where(AdaptationModel.person_id == person_id)
        .order_by(AdaptationModel.created_at.desc())
        .limit(1)
    )
    if recipe is None:
        return None
    return Recipe(recipe["context"], recipe["goal"], recipe["level"], Format(recipe["format"]))


async def guide_adaptations_in_class(
    session: AsyncSession, class_id: UUID
) -> list[GuideAdaptation]:
    query = select(
        AdaptationModel.id,
        AdaptationModel.person_id,
        AdaptationModel.material_id,
        AdaptationModel.created_at,
    ).where(AdaptationModel.class_id == class_id)
    return [
        GuideAdaptation(row.id, row.person_id, row.material_id, row.created_at)
        for row in await session.execute(query)
    ]
