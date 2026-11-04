"""M9 · Revisión de afirmaciones: contract with the front.

Closed vocabulary (RNF11, RNF14): there is no "false" status and no AI-percentage anywhere.
"""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class ClaimStatus(StrEnum):
    SUPPORTED = "supported"
    UNVERIFIABLE = "unverifiable"
    CONTRADICTS = "contradicts"


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
