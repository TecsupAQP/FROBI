"""M9 · Revisión de afirmaciones."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from frobi.modules.claim_review.application import GetReviewHandler, ReviewClaimsHandler
from frobi.shared.presentation import (
    AUTH_RESPONSES,
    NOT_FOUND_RESPONSES,
    CurrentClassId,
    CurrentPersonId,
    problem,
)

from .dependencies import get_get_review, get_review_claims
from .schemas import ClaimReviewOut

router = APIRouter(
    prefix="/works/{work_id}",
    tags=["M9 · Revisión de afirmaciones"],
    responses={**AUTH_RESPONSES, **NOT_FOUND_RESPONSES},
)


@router.post(
    "/claim-review",
    summary="Revisar las afirmaciones del borrador",
    responses={422: problem("Borrador sin frases (`ClaimReview.NothingToReview`).")},
)
async def review_claims(
    work_id: UUID,
    person_id: CurrentPersonId,
    class_id: CurrentClassId,
    handler: Annotated[ReviewClaimsHandler, Depends(get_review_claims)],
) -> ClaimReviewOut:
    claims = await handler.handle(person_id, class_id, work_id)
    return ClaimReviewOut.from_claims(work_id, claims)


@router.get("/claims", summary="Volver a ver la revisión")
async def get_claims(
    work_id: UUID,
    person_id: CurrentPersonId,
    handler: Annotated[GetReviewHandler, Depends(get_get_review)],
) -> ClaimReviewOut:
    return ClaimReviewOut.from_claims(work_id, await handler.handle(person_id, work_id))
