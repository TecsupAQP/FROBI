"""A scored prompt: 0-4 per piece, weakest first, and an autonomy level (RF09-RF12, RF23)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from .errors import EmptyPrompt
from .rubric import FEEDBACK, PIECE_NAMES, TIPS, RecipePiece

PROMPT_MAX = 4000
MISSING_BELOW = 3

AUTONOMY_LABELS: dict[int, str] = {
    1: "Nivel 1: todavía pides sin receta",
    2: "Nivel 2: ya pides con contexto",
    3: "Nivel 3: armas la receta completa",
}


def autonomy_for(total: int) -> int:
    """Total of the 4 pieces (0-16): up to 6 is level 1, up to 11 level 2, from 12 level 3."""
    if total >= 12:
        return 3
    if total >= 7:
        return 2
    return 1


def clean_prompt(raw: str) -> str:
    prompt = raw.strip()
    if not prompt:
        raise EmptyPrompt()
    return prompt[:PROMPT_MAX]


@dataclass(frozen=True, slots=True)
class PieceScore:
    piece: RecipePiece
    score: int
    feedback: str

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 4:
            raise ValueError("A piece is scored from 0 to 4")


def piece_scores(
    scores: dict[RecipePiece, int], feedback: dict[RecipePiece, str] | None = None
) -> tuple[PieceScore, ...]:
    """Weakest first; ties keep the recipe order (context, goal, level, format)."""
    if any(not 0 <= scores[p] <= 4 for p in RecipePiece):
        raise ValueError("A piece is scored from 0 to 4")
    order = list(RecipePiece)
    ranked = sorted(RecipePiece, key=lambda p: (scores[p], order.index(p)))
    return tuple(
        PieceScore(p, scores[p], (feedback or {}).get(p) or FEEDBACK[scores[p]]) for p in ranked
    )


@dataclass(frozen=True, slots=True)
class PromptEvaluation:
    id: UUID
    person_id: UUID
    class_id: UUID | None
    text: str
    scores: tuple[PieceScore, ...]
    improved_text: str
    material_id: UUID | None
    claim_id: UUID | None
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        person_id: UUID,
        class_id: UUID | None,
        text: str,
        scores: tuple[PieceScore, ...],
        improved_text: str,
        material_id: UUID | None,
        claim_id: UUID | None,
        now: datetime,
    ) -> "PromptEvaluation":
        if {s.piece for s in scores} != set(RecipePiece):
            raise ValueError("Every piece must be scored exactly once")
        return cls(
            id=uuid4(),
            person_id=person_id,
            class_id=class_id,
            text=clean_prompt(text),
            scores=scores,
            improved_text=improved_text.strip(),
            material_id=material_id,
            claim_id=claim_id,
            created_at=now,
        )

    @property
    def total(self) -> int:
        return sum(s.score for s in self.scores)

    @property
    def missing_piece(self) -> RecipePiece | None:
        weakest = self.scores[0]
        return weakest.piece if weakest.score < MISSING_BELOW else None

    @property
    def suggestion(self) -> str:
        missing = self.missing_piece
        if missing is None:
            return "Tu instrucción tiene las 4 piezas. Pruébala y compara el resultado."
        return f"Lo que más falta es el {PIECE_NAMES[missing]}. {TIPS[missing]}"

    @property
    def autonomy_level(self) -> int:
        return autonomy_for(self.total)

    @property
    def autonomy_label(self) -> str:
        return AUTONOMY_LABELS[self.autonomy_level]

    def visible_to(self, person_id: UUID) -> bool:
        return self.person_id == person_id
