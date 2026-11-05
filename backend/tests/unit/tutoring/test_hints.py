from uuid import uuid4

import pytest

from fakes.adaptations import Limiter, ScriptedLlm
from fakes.tutoring import CONTEXT
from frobi.modules.tutoring.domain import HelpStep
from frobi.modules.tutoring.infrastructure import (
    FallbackHintGenerator,
    LlmHintGenerator,
    ResilientHintGenerator,
    material_hint,
)

TASK = "¿Qué sensor detecta el nivel de líquido en un tanque de plástico?"


def test_hint_1_points_to_the_right_section_without_the_answer() -> None:
    hint = material_hint(CONTEXT, TASK, HelpStep.HINT_1)

    assert "«Sensores capacitivos»" in hint
    assert "líquidos" not in hint


def test_hint_2_quotes_only_the_start_of_the_key_sentence() -> None:
    hint = material_hint(CONTEXT, TASK, HelpStep.HINT_2)

    assert "Los sensores capacitivos detectan plásticos" in hint
    assert hint.endswith("…»")


def test_step_by_step_lists_steps_without_the_result() -> None:
    hint = material_hint(CONTEXT, TASK, HelpStep.STEP_BY_STEP)

    assert hint.startswith("1. ")
    assert "4. " in hint
    assert "tanque" not in hint


def test_final_quotes_the_full_passage_and_asks_to_compare() -> None:
    hint = material_hint(CONTEXT, TASK, HelpStep.FINAL)

    assert "a través de un tanque" in hint
    assert "Compáralo con tu intento" in hint


def _resilient(
    llm: ScriptedLlm, *, allowed: bool = True, timeout: float = 1.0
) -> ResilientHintGenerator:
    return ResilientHintGenerator(
        LlmHintGenerator(llm), FallbackHintGenerator(), Limiter(allowed), timeout
    )


async def test_a_valid_ai_hint_is_used() -> None:
    llm = ScriptedLlm(reply={"text": "Pista de la IA"})

    hint = await _resilient(llm).hint(
        requested_by=uuid4(), context=CONTEXT, task_ref=TASK, step=HelpStep.HINT_1
    )

    assert hint.text == "Pista de la IA"
    assert hint.fallback is False


@pytest.mark.parametrize(
    "llm",
    [ScriptedLlm(reply={"text": "x"}, delay=2), ScriptedLlm(reply={"texto": "mal"})],
    ids=["slow", "invalid"],
)
async def test_slow_or_invalid_ai_hints_fall_back_to_the_material(llm: ScriptedLlm) -> None:
    hint = await _resilient(llm, timeout=0.05).hint(
        requested_by=uuid4(), context=CONTEXT, task_ref=TASK, step=HelpStep.HINT_1
    )

    assert hint.fallback is True
    assert "«Sensores capacitivos»" in hint.text
