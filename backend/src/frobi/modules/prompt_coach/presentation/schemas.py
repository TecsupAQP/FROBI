"""M7 · Entrenador de instrucciones: contract with the front."""

from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.prompt_coach.application import Comparison
from frobi.modules.prompt_coach.domain import PromptEvaluation, RecipePiece


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

    @classmethod
    def from_domain(cls, evaluation: PromptEvaluation) -> "PromptEvaluationOut":
        return cls(
            id=evaluation.id,
            text=evaluation.text,
            scores=[
                PieceScore(piece=s.piece, score=s.score, feedback=s.feedback)
                for s in evaluation.scores
            ],
            missing_piece=evaluation.missing_piece,
            suggestion=evaluation.suggestion,
            improved_text=evaluation.improved_text,
            autonomy_level=evaluation.autonomy_level,
            autonomy_label=evaluation.autonomy_label,
        )


class PromptRun(BaseModel):
    prompt: str
    output: str


class PromptComparisonOut(BaseModel):
    evaluation_id: UUID
    original: PromptRun
    improved: PromptRun
    fallback: bool

    @classmethod
    def from_comparison(cls, comparison: Comparison) -> "PromptComparisonOut":
        evaluation = comparison.evaluation
        return cls(
            evaluation_id=evaluation.id,
            original=PromptRun(prompt=evaluation.text, output=comparison.original.text),
            improved=PromptRun(prompt=evaluation.improved_text, output=comparison.improved.text),
            fallback=comparison.fallback,
        )
