"""The help ladder rules, exhaustively (PLAN_BACKEND §9: «Escalera: no saltar escalones»)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from frobi.modules.tutoring.domain import (
    LADDER,
    FinalLocked,
    HelpAttempt,
    HelpStep,
    ReachedStep,
    StepOutOfOrder,
)

NOW = datetime(2026, 11, 5, 11, 0, tzinfo=UTC)
H1, H2, SBS, FINAL = HelpStep


def _attempt(reached: ReachedStep = ReachedStep.NONE, *, own: bool = False) -> HelpAttempt:
    attempt = HelpAttempt.open(
        person_id=uuid4(), class_id=None, adaptation_id=uuid4(), task_ref=" ejercicio   1 ", now=NOW
    )
    for step in LADDER[: list(ReachedStep).index(reached)]:
        if step is FINAL:
            attempt = attempt.submit_own_answer("mi intento", (), matches_guide=False)
        attempt = attempt.request(step)
    if own:
        attempt = attempt.submit_own_answer("mi intento", (), matches_guide=False)
    return attempt


def test_a_new_attempt_starts_at_level_0_and_offers_hint_1() -> None:
    attempt = _attempt()

    assert attempt.task_ref == "ejercicio 1"
    assert attempt.max_step is ReachedStep.NONE
    assert attempt.next_step is H1
    assert attempt.help_level == 0
    assert attempt.help_label == "Nivel 0, sin ayuda"
    assert attempt.final_unlocked is False


def test_the_whole_ladder_in_order_with_an_own_attempt_before_final() -> None:
    attempt = _attempt()
    for step in (H1, H2, SBS):
        attempt = attempt.request(step)
    attempt = attempt.submit_own_answer("Creo que es el capacitivo", (), matches_guide=True)
    attempt = attempt.request(FINAL)

    assert attempt.max_step is ReachedStep.FINAL
    assert attempt.next_step is None
    assert attempt.help_label == "Nivel 4, con la respuesta"
    assert attempt.solved_without_ai is False  # hints were opened


@pytest.mark.parametrize(
    ("reached", "step"),
    [
        (ReachedStep.NONE, H2),
        (ReachedStep.NONE, SBS),
        (ReachedStep.HINT_1, SBS),
    ],
)
def test_skipping_a_step_is_out_of_order(reached: ReachedStep, step: HelpStep) -> None:
    with pytest.raises(StepOutOfOrder):
        _attempt(reached).request(step)


@pytest.mark.parametrize("reached", list(ReachedStep)[:-1])
def test_final_is_locked_without_an_own_attempt_at_any_level(reached: ReachedStep) -> None:
    with pytest.raises(FinalLocked):
        _attempt(reached).request(FINAL)


@pytest.mark.parametrize("reached", [ReachedStep.NONE, ReachedStep.HINT_1, ReachedStep.HINT_2])
def test_with_an_own_attempt_final_still_cannot_skip_steps(reached: ReachedStep) -> None:
    with pytest.raises(StepOutOfOrder):
        _attempt(reached, own=True).request(FINAL)


def test_with_an_own_attempt_final_follows_step_by_step() -> None:
    attempt = _attempt(ReachedStep.STEP_BY_STEP, own=True)

    assert attempt.final_unlocked is True
    assert attempt.next_step is FINAL
    assert attempt.request(FINAL).max_step is ReachedStep.FINAL


@pytest.mark.parametrize("step", [H1, H2])
def test_asking_again_for_an_open_step_does_not_advance(step: HelpStep) -> None:
    attempt = _attempt(ReachedStep.HINT_2)

    assert attempt.request(step) is attempt


@pytest.mark.parametrize(
    ("reached", "label"),
    [
        (ReachedStep.HINT_1, "Nivel 1, con una pista"),
        (ReachedStep.HINT_2, "Nivel 2, con pistas"),
        (ReachedStep.STEP_BY_STEP, "Nivel 3, paso a paso"),
    ],
)
def test_help_level_labels(reached: ReachedStep, label: str) -> None:
    assert _attempt(reached).help_label == label


def test_solved_without_ai_needs_a_match_before_any_hint() -> None:
    attempt = _attempt()

    assert attempt.submit_own_answer("x", (), matches_guide=True).solved_without_ai is True
    assert attempt.submit_own_answer("x", (), matches_guide=False).solved_without_ai is False
    assert (
        _attempt(ReachedStep.HINT_1)
        .submit_own_answer("x", (), matches_guide=True)
        .solved_without_ai
        is False
    )


def test_solved_without_ai_is_not_lost_by_opening_help_later() -> None:
    attempt = _attempt().submit_own_answer("bien", (), matches_guide=True)

    after_help = attempt.request(H1).submit_own_answer("otra", (), matches_guide=False)

    assert after_help.solved_without_ai is True


def test_self_check_is_cleaned_and_deduplicated() -> None:
    attempt = _attempt().submit_own_answer(
        " mi idea ", (" revisé ", "revisé", " ", "comparé"), matches_guide=False
    )

    assert attempt.own_answer == "mi idea"
    assert attempt.self_check == ("revisé", "comparé")
