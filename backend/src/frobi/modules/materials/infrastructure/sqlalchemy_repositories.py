from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.materials.domain import Material, MaterialKind, MaterialSource, Work

from .models import MaterialModel, WorkModel


class SqlAlchemyMaterialRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, material: Material) -> None:
        if material.owner_id is None:
            raise ValueError("Only samples have no owner, and samples are not stored.")
        self._session.add(
            MaterialModel(
                id=material.id,
                owner_id=material.owner_id,
                class_id=material.class_id,
                title=material.title,
                kind=material.kind.value,
                source=material.source.value,
                extracted_text=material.text,
                created_at=material.created_at,
            )
        )

    async def get(self, material_id: UUID) -> Material | None:
        row = await self._session.get(MaterialModel, material_id)
        if row is None:
            return None
        return Material(
            id=row.id,
            owner_id=row.owner_id,
            class_id=row.class_id,
            title=row.title,
            kind=MaterialKind(row.kind),
            source=MaterialSource(row.source),
            text=row.extracted_text,
            created_at=row.created_at,
        )


class SqlAlchemyWorkRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, work: Work) -> None:
        self._session.add(
            WorkModel(
                id=work.id,
                person_id=work.person_id,
                class_id=work.class_id,
                brief_material_id=work.brief_material_id,
                draft_material_id=work.draft_material_id,
                organized={
                    "requirements": list(work.organized.requirements),
                    "topics": list(work.organized.topics),
                    "missing": list(work.organized.missing),
                },
                created_at=work.created_at,
            )
        )
