"""Review the claims of a draft against the person's guides, and see the review again (RF19)."""

from uuid import UUID

from frobi.modules.claim_review.application.ports import (
    ClaimRepository,
    ClaimReviewer,
    GuideReader,
    WorkReader,
)
from frobi.modules.claim_review.domain import (
    Claim,
    NothingToReview,
    ReviewNotFound,
    WorkNotAvailable,
    claims_of,
)
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock


class ReviewClaimsHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        claims: ClaimRepository,
        works: WorkReader,
        guides: GuideReader,
        reviewer: ClaimReviewer,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._claims = claims
        self._works = works
        self._guides = guides
        self._reviewer = reviewer
        self._clock = clock

    async def handle(self, person_id: UUID, class_id: UUID | None, work_id: UUID) -> list[Claim]:
        draft = await self._works.find(person_id, work_id)
        if draft is None:
            raise WorkNotAvailable()
        inputs = claims_of(draft.draft_text)
        if not inputs:
            raise NothingToReview()
        guides = await self._guides.for_person(person_id)
        verdicts = await self._reviewer.review(requested_by=person_id, claims=inputs, guides=guides)
        now = self._clock.now()
        claims = [
            Claim.create(
                work_id=work_id,
                person_id=person_id,
                class_id=class_id,
                position=position,
                claim=claim,
                verdict=verdict,
                now=now,
            )
            for position, (claim, verdict) in enumerate(zip(inputs, verdicts, strict=True))
        ]
        async with self._uow:
            await self._claims.replace(work_id, claims)
            await self._uow.commit()
        return claims


class GetReviewHandler:
    def __init__(self, claims: ClaimRepository, works: WorkReader) -> None:
        self._claims = claims
        self._works = works

    async def handle(self, person_id: UUID, work_id: UUID) -> list[Claim]:
        if await self._works.find(person_id, work_id) is None:
            raise WorkNotAvailable()
        claims = await self._claims.for_work(work_id)
        if not claims:
            raise ReviewNotFound()
        return claims


class GetClaimHandler:
    """One claim of the person's own reviews. Public API (tool recommendations, M10)."""

    def __init__(self, claims: ClaimRepository) -> None:
        self._claims = claims

    async def find(self, person_id: UUID, claim_id: UUID) -> Claim | None:
        claim = await self._claims.get(claim_id)
        return claim if claim is not None and claim.person_id == person_id else None
