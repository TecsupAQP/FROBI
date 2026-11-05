from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.materials.domain import (
    Material,
    MaterialKind,
    MaterialSource,
    OrganizedWork,
    TopicSpan,
    Work,
)

from .models import MaterialModel, WorkModel

MAX_GUIDES = 20


def _material(row: MaterialModel) -> Material:
    return Material(
        id=row.id,
        owner_id=row.owner_id,
        class_id=row.class_id,
        title=row.title,
        kind=MaterialKind(row.kind),
        source=MaterialSource(row.source),
        text=row.extracted_text,
        created_at=row.created_at,
        file_key=row.file_key,
        topic_spans=tuple(
            TopicSpan(
                title=t["title"],
                start=t["start"],
                end=t["end"],
                page_start=t.get("page_start"),
                page_end=t.get("page_end"),
            )
            for t in row.topics or ()
        ),
    )


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
                file_key=material.file_key,
                topics=[
                    {
                        "title": t.title,
                        "start": t.start,
                        "end": t.end,
                        "page_start": t.page_start,
                        "page_end": t.page_end,
                    }
                    for t in material.topic_spans
                ],
                created_at=material.created_at,
            )
        )

    async def get(self, material_id: UUID) -> Material | None:
        row = await self._session.get(MaterialModel, material_id)
        return None if row is None else _material(row)

    async def list_for_owner(self, owner_id: UUID, kind: MaterialKind) -> list[Material]:
        """Most recent first, capped so a review never reads an unbounded amount of text."""
        query = (
            select(MaterialModel)
            .where(MaterialModel.owner_id == owner_id, MaterialModel.kind == kind.value)
            .order_by(MaterialModel.created_at.desc())
            .limit(MAX_GUIDES)
        )
        return [_material(row) for row in (await self._session.scalars(query)).all()]

    async def list_for_class(self, class_id: UUID) -> list[Material]:
        query = (
            select(MaterialModel)
            .where(
                MaterialModel.class_id == class_id,
                MaterialModel.kind == MaterialKind.CLASS_CONTENT.value,
            )
            .order_by(MaterialModel.created_at.desc())
            .limit(MAX_GUIDES)
        )
        return [_material(row) for row in (await self._session.scalars(query)).all()]


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

    async def get(self, work_id: UUID) -> Work | None:
        row = await self._session.get(WorkModel, work_id)
        if row is None:
            return None
        return Work(
            id=row.id,
            person_id=row.person_id,
            class_id=row.class_id,
            brief_material_id=row.brief_material_id,
            draft_material_id=row.draft_material_id,
            organized=OrganizedWork(
                requirements=tuple(row.organized.get("requirements", [])),
                topics=tuple(row.organized.get("topics", [])),
                missing=tuple(row.organized.get("missing", [])),
            ),
            created_at=row.created_at,
        )
