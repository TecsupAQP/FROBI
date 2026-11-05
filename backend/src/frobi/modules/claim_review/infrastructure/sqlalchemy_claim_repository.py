from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.claim_review.domain import Claim, ClaimStatus

from .models import ClaimModel


def _to_domain(row: ClaimModel) -> Claim:
    return Claim(
        id=row.id,
        work_id=row.work_id,
        person_id=row.person_id,
        class_id=row.class_id,
        position=row.position,
        section=row.section,
        fragment=row.fragment,
        status=ClaimStatus(row.status),
        reason=row.reason,
        backing_passage=row.backing_passage,
        created_at=row.created_at,
    )


class SqlAlchemyClaimRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace(self, work_id: UUID, claims: list[Claim]) -> None:
        await self._session.execute(delete(ClaimModel).where(ClaimModel.work_id == work_id))
        self._session.add_all(
            ClaimModel(
                id=c.id,
                work_id=c.work_id,
                person_id=c.person_id,
                class_id=c.class_id,
                position=c.position,
                section=c.section[:200],
                fragment=c.fragment,
                status=c.status.value,
                reason=c.reason,
                backing_passage=c.backing_passage,
                created_at=c.created_at,
            )
            for c in claims
        )

    async def for_work(self, work_id: UUID) -> list[Claim]:
        query = (
            select(ClaimModel).where(ClaimModel.work_id == work_id).order_by(ClaimModel.position)
        )
        return [_to_domain(row) for row in (await self._session.scalars(query)).all()]

    async def get(self, claim_id: UUID) -> Claim | None:
        row = await self._session.get(ClaimModel, claim_id)
        return None if row is None else _to_domain(row)
