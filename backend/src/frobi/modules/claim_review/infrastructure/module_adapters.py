"""claim_review's ports over the public API of materials."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import materials
from frobi.modules.claim_review.application.ports import DraftToReview


class WorkReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._works = materials.read_work_handler(session)

    async def find(self, person_id: UUID, work_id: UUID) -> DraftToReview | None:
        work = await self._works.find(person_id, work_id)
        return None if work is None else DraftToReview(work.work_id, work.draft_text)


class GuideReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._guides = materials.guides_handler(session)

    async def for_person(self, person_id: UUID) -> list[str]:
        return [guide.text for guide in await self._guides.for_person(person_id)]
