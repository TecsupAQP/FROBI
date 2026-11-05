from datetime import UTC, datetime
from uuid import uuid4

import pytest

from frobi.modules.prompt_coach.domain import (
    EmptyPrompt,
    PromptEvaluation,
    RecipePiece,
    piece_scores,
)

C, G, L, F = RecipePiece
NOW = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)


def _evaluation(scores: dict[RecipePiece, int], text: str = "explícame") -> PromptEvaluation:
    return PromptEvaluation.create(
        person_id=uuid4(),
        class_id=None,
        text=text,
        scores=piece_scores(scores),
        improved_text="mejor",
        material_id=None,
        claim_id=None,
        now=NOW,
    )


def test_scores_list_the_weakest_piece_first_and_keep_recipe_order_on_ties() -> None:
    evaluation = _evaluation({C: 3, G: 2, L: 0, F: 0})

    assert [s.piece for s in evaluation.scores] == [L, F, G, C]
    assert evaluation.missing_piece is L


def test_the_suggestion_names_the_missing_piece() -> None:
    evaluation = _evaluation({C: 4, G: 4, L: 1, F: 4})

    assert evaluation.suggestion.startswith("Lo que más falta es el nivel.")


def test_nothing_is_missing_when_every_piece_is_3_or_more() -> None:
    evaluation = _evaluation({C: 3, G: 4, L: 3, F: 3})

    assert evaluation.missing_piece is None
    assert "4 piezas" in evaluation.suggestion
    assert evaluation.autonomy_level == 3
    assert evaluation.autonomy_label == "Nivel 3: armas la receta completa"


def test_default_feedback_explains_each_score() -> None:
    evaluation = _evaluation({C: 0, G: 4, L: 2, F: 2})

    assert evaluation.scores[0].feedback == "Falta: no aparece en tu instrucción."


def test_a_blank_prompt_is_rejected() -> None:
    with pytest.raises(EmptyPrompt):
        _evaluation({C: 0, G: 0, L: 0, F: 0}, text="   ")


def test_every_piece_must_be_scored() -> None:
    with pytest.raises(KeyError):
        piece_scores({C: 1, G: 1, L: 1})  # type: ignore[dict-item]


def test_a_piece_cannot_score_above_4() -> None:
    with pytest.raises(ValueError, match="0 to 4"):
        piece_scores({C: 5, G: 1, L: 1, F: 1})
