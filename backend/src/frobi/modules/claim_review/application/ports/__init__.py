"""What claim_review needs, in its own words. Adapters live in claim_review/infrastructure."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.modules.claim_review.domain import Claim, ClaimInput, Verdict


@dataclass(frozen=True, slots=True)
class DraftToReview:
    work_id: UUID
    draft_text: str


class WorkReader(Protocol):
    """Over the public API of materials: only the person's own works."""

    async def find(self, person_id: UUID, work_id: UUID) -> DraftToReview | None: ...


class GuideReader(Protocol):
    """The texts the person studies from (their guides and the samples): the source of truth."""

    async def for_person(self, person_id: UUID) -> list[str]: ...


class ClaimReviewer(Protocol):
    """One verdict per claim, in the same order. Never waits more than the AI time cap."""

    async def review(
        self, *, requested_by: UUID, claims: list[ClaimInput], guides: list[str]
    ) -> list[Verdict]: ...


class ClaimRepository(Protocol):
    async def replace(self, work_id: UUID, claims: list[Claim]) -> None:
        """A new review of a work replaces the previous one."""
        ...

    async def for_work(self, work_id: UUID) -> list[Claim]: ...

    async def get(self, claim_id: UUID) -> Claim | None: ...


__all__ = ["ClaimRepository", "ClaimReviewer", "DraftToReview", "GuideReader", "WorkReader"]
