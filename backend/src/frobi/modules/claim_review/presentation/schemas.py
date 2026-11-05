"""M9 · Revisión de afirmaciones: contract with the front.

Closed vocabulary (RNF11, RNF14): there is no "false" status and no AI-percentage anywhere.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.claim_review.domain import Claim, ClaimStatus


class ClaimOut(BaseModel):
    id: UUID
    fragment: str = Field(description="Frase del borrador que se revisó.")
    status: ClaimStatus
    reason: str
    backing_passage: str | None = Field(description="Pasaje de tu material que la respalda.")
    no_backing_message: str | None = Field(
        description="«No hay respaldo en tu material» cuando no hay pasaje."
    )


class ClaimSection(BaseModel):
    section: str
    claims: list[ClaimOut]


class ClaimReviewOut(BaseModel):
    work_id: UUID
    sections: list[ClaimSection]

    @classmethod
    def from_claims(cls, work_id: UUID, claims: list[Claim]) -> "ClaimReviewOut":
        sections: dict[str, list[ClaimOut]] = {}
        for claim in sorted(claims, key=lambda c: c.position):
            sections.setdefault(claim.section, []).append(
                ClaimOut(
                    id=claim.id,
                    fragment=claim.fragment,
                    status=claim.status,
                    reason=claim.reason,
                    backing_passage=claim.backing_passage,
                    no_backing_message=claim.no_backing_message,
                )
            )
        return cls(
            work_id=work_id,
            sections=[ClaimSection(section=name, claims=items) for name, items in sections.items()],
        )
