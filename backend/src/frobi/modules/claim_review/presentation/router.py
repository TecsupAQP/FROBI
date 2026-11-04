"""M9 · Revisión de afirmaciones.

Stub: returns the scripted demo case. The real use cases replace each body.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from frobi.shared.presentation import AUTH_RESPONSES, NOT_FOUND_RESPONSES, require_token

from .schemas import ClaimOut, ClaimReviewOut, ClaimSection, ClaimStatus

router = APIRouter(
    prefix="/works/{work_id}",
    tags=["M9 · Revisión de afirmaciones"],
    dependencies=[Depends(require_token)],
    responses={**AUTH_RESPONSES, **NOT_FOUND_RESPONSES},
)

NO_BACKING = "No hay respaldo en tu material."


def _review(work_id: UUID) -> ClaimReviewOut:
    return ClaimReviewOut(
        work_id=work_id,
        sections=[
            ClaimSection(
                section="Introducción",
                claims=[
                    ClaimOut(
                        id=UUID("00000000-0000-4000-8000-000000002001"),
                        fragment="Los sensores inductivos detectan metales sin contacto.",
                        status=ClaimStatus.SUPPORTED,
                        reason="La guía dice lo mismo.",
                        backing_passage="Los sensores inductivos detectan metales sin contacto.",
                        no_backing_message=None,
                    ),
                    ClaimOut(
                        id=UUID("00000000-0000-4000-8000-000000002002"),
                        fragment="Los sensores capacitivos solo detectan metales.",
                        status=ClaimStatus.CONTRADICTS,
                        reason="La guía dice que también detectan plásticos y líquidos.",
                        backing_passage="Los capacitivos detectan también plásticos y líquidos.",
                        no_backing_message=None,
                    ),
                ],
            ),
            ClaimSection(
                section="Conclusión",
                claims=[
                    ClaimOut(
                        id=UUID("00000000-0000-4000-8000-000000002003"),
                        fragment="Los sensores ópticos son los más baratos del mercado.",
                        status=ClaimStatus.UNVERIFIABLE,
                        reason="Tu material no habla de precios.",
                        backing_passage=None,
                        no_backing_message=NO_BACKING,
                    )
                ],
            ),
        ],
    )


@router.post("/claim-review", summary="Revisar las afirmaciones del borrador")
async def review_claims(work_id: UUID) -> ClaimReviewOut:
    return _review(work_id)


@router.get("/claims", summary="Volver a ver la revisión")
async def get_claims(work_id: UUID) -> ClaimReviewOut:
    return _review(work_id)
