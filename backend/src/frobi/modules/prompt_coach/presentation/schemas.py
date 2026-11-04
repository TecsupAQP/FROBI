"""M7 · Entrenador de instrucciones: contract with the front."""

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class RecipePiece(StrEnum):
    CONTEXT = "context"
    GOAL = "goal"
    LEVEL = "level"
    FORMAT = "format"


class EvaluatePromptRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4_000)
    material_id: UUID | None = None
    claim_id: UUID | None = None


class PieceScore(BaseModel):
    piece: RecipePiece
    score: int = Field(ge=0, le=4)
    feedback: str


class PromptEvaluationOut(BaseModel):
    id: UUID
    text: str
    scores: list[PieceScore] = Field(description="Una por pieza; primero la que más falta.")
    missing_piece: RecipePiece | None
    suggestion: str
    improved_text: str
    autonomy_level: int = Field(ge=1, le=3)
    autonomy_label: str = Field(examples=["Nivel 2: ya pides con contexto"])


class PromptRun(BaseModel):
    prompt: str
    output: str


class PromptComparisonOut(BaseModel):
    evaluation_id: UUID
    original: PromptRun
    improved: PromptRun
    fallback: bool
