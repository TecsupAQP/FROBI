from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.adaptations.domain import Adaptation, Format, Recipe

from .content_codec import content_from_json, content_to_json, recipe_to_json
from .models import AdaptationModel


class SqlAlchemyAdaptationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, adaptation: Adaptation) -> None:
        self._session.add(
            AdaptationModel(
                id=adaptation.id,
                material_id=adaptation.material_id,
                person_id=adaptation.person_id,
                class_id=adaptation.class_id,
                format=adaptation.format.value,
                content=content_to_json(adaptation.content),
                recipe=recipe_to_json(adaptation.recipe),
                fallback=adaptation.fallback,
                created_at=adaptation.created_at,
            )
        )

    async def get(self, adaptation_id: UUID) -> Adaptation | None:
        row = await self._session.get(AdaptationModel, adaptation_id)
        if row is None:
            return None
        return Adaptation(
            id=row.id,
            material_id=row.material_id,
            person_id=row.person_id,
            class_id=row.class_id,
            format=Format(row.format),
            content=content_from_json(row.content),
            recipe=Recipe(
                context=row.recipe["context"],
                goal=row.recipe["goal"],
                level=row.recipe["level"],
                format=Format(row.recipe["format"]),
            ),
            fallback=row.fallback,
            created_at=row.created_at,
        )
