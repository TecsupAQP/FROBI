from uuid import UUID, uuid4

import pytest

from fakes.adaptations import Limiter, ScriptedLlm
from fakes.identity import FakeUnitOfWork, FixedClock
from frobi.modules.prompt_coach.application import (
    ComparePromptsHandler,
    EvaluatePromptCommand,
    EvaluatePromptHandler,
)
from frobi.modules.prompt_coach.application.ports import MaterialContext
from frobi.modules.prompt_coach.domain import (
    EvaluationNotFound,
    MaterialNotAvailable,
    PromptEvaluation,
    RecipePiece,
)
from frobi.modules.prompt_coach.infrastructure import (
    LlmRunner,
    LlmScorer,
    ResilientRunner,
    ResilientScorer,
    RubricScorer,
    SimulatedRunner,
    simulate,
)

ANA = uuid4()
MATERIAL_ID = uuid4()
MATERIAL = MaterialContext(
    title="Guía",
    text="## Inductivos\nLos sensores inductivos detectan metales sin contacto. Tienen poco "
    "alcance.\n## Capacitivos\nLos sensores capacitivos detectan plásticos y líquidos.",
)
VALID_SCORE = {
    "context": {"score": 1, "feedback": "c"},
    "goal": {"score": 3, "feedback": "g"},
    "level": {"score": 0, "feedback": "l"},
    "format": {"score": 2, "feedback": "f"},
    "improved_text": "Versión de la IA",
}


class Materials:
    async def find(self, person_id: UUID, material_id: UUID) -> MaterialContext | None:
        return MATERIAL if person_id == ANA and material_id == MATERIAL_ID else None


class Evaluations:
    def __init__(self) -> None:
        self.items: dict[UUID, PromptEvaluation] = {}

    async def add(self, evaluation: PromptEvaluation) -> None:
        self.items[evaluation.id] = evaluation

    async def get(self, evaluation_id: UUID) -> PromptEvaluation | None:
        return self.items.get(evaluation_id)


def _scorer(llm: ScriptedLlm, timeout: float = 1.0) -> ResilientScorer:
    return ResilientScorer(LlmScorer(llm), RubricScorer(), Limiter(True), timeout)


async def test_a_valid_ai_score_is_used_with_its_feedback() -> None:
    draft = await _scorer(ScriptedLlm(reply=VALID_SCORE)).score(
        requested_by=ANA, prompt="x", material=None
    )

    assert draft.scores[RecipePiece.GOAL] == 3
    assert draft.feedback[RecipePiece.LEVEL] == "l"
    assert draft.improved_text == "Versión de la IA"


@pytest.mark.parametrize(
    "llm",
    [
        ScriptedLlm(reply={**VALID_SCORE, "goal": {"score": 9, "feedback": "x"}}),
        ScriptedLlm(reply={"context": {}}),
        ScriptedLlm(reply=VALID_SCORE, delay=2),
    ],
    ids=["score-out-of-range", "wrong-shape", "slow"],
)
async def test_bad_or_slow_ai_scores_fall_back_to_the_rubric(llm: ScriptedLlm) -> None:
    draft = await _scorer(llm, timeout=0.05).score(
        requested_by=ANA, prompt="explicame sensores", material=None
    )

    assert draft.scores == {
        RecipePiece.CONTEXT: 0,
        RecipePiece.GOAL: 2,
        RecipePiece.LEVEL: 0,
        RecipePiece.FORMAT: 0,
    }


def test_the_simulation_shows_why_the_recipe_matters() -> None:
    vague = simulate("explicame sensores", MATERIAL)
    shaped = simulate("Explícame los capacitivos con palabras simples en 3 puntos", MATERIAL)

    assert vague.startswith("Los sensores inductivos detectan metales")
    assert shaped.startswith("• Los sensores capacitivos")
    assert shaped.count("•") == 3


async def test_runner_uses_the_ai_when_it_answers() -> None:
    runner = ResilientRunner(
        LlmRunner(ScriptedLlm(reply={"text": "salida IA"})), SimulatedRunner(), Limiter(True), 1
    )

    output = await runner.run(requested_by=ANA, prompt="x", material=MATERIAL)

    assert (output.text, output.fallback) == ("salida IA", False)


def _evaluate_handler(evaluations: Evaluations) -> EvaluatePromptHandler:
    return EvaluatePromptHandler(
        FakeUnitOfWork(), evaluations, Materials(), RubricScorer(), FixedClock()
    )


async def test_evaluate_stores_scores_class_and_references() -> None:
    evaluations, class_id, claim = Evaluations(), uuid4(), uuid4()

    evaluation = await _evaluate_handler(evaluations).handle(
        EvaluatePromptCommand(
            person_id=ANA,
            class_id=class_id,
            text="  explicame sensores ",
            material_id=MATERIAL_ID,
            claim_id=claim,
        )
    )

    assert evaluations.items[evaluation.id] == evaluation
    assert evaluation.text == "explicame sensores"
    assert evaluation.class_id == class_id
    assert evaluation.claim_id == claim
    assert evaluation.missing_piece is RecipePiece.CONTEXT
    assert "«Guía»" in evaluation.improved_text


async def test_evaluate_with_someone_elses_material_is_not_found() -> None:
    with pytest.raises(MaterialNotAvailable):
        await _evaluate_handler(Evaluations()).handle(
            EvaluatePromptCommand(
                person_id=uuid4(), class_id=None, text="x", material_id=MATERIAL_ID
            )
        )


async def test_compare_runs_both_prompts_and_reports_fallback() -> None:
    evaluations = Evaluations()
    evaluation = await _evaluate_handler(evaluations).handle(
        EvaluatePromptCommand(
            person_id=ANA, class_id=None, text="explicame sensores", material_id=MATERIAL_ID
        )
    )

    comparison = await ComparePromptsHandler(evaluations, Materials(), SimulatedRunner()).handle(
        ANA, evaluation.id
    )

    assert comparison.fallback is True
    assert comparison.original.text != comparison.improved.text
    assert comparison.improved.text.startswith("•")


async def test_compare_someone_elses_evaluation_is_not_found() -> None:
    evaluations = Evaluations()
    evaluation = await _evaluate_handler(evaluations).handle(
        EvaluatePromptCommand(person_id=ANA, class_id=None, text="explicame")
    )

    with pytest.raises(EvaluationNotFound):
        await ComparePromptsHandler(evaluations, Materials(), SimulatedRunner()).handle(
            uuid4(), evaluation.id
        )
