from uuid import UUID, uuid4

import pytest

from fakes.identity import FakeUnitOfWork, FixedClock
from fakes.tutoring import ADAPTATION_ID, EchoHints, InMemoryAttempts, StaticContexts
from frobi.modules.tutoring.application import (
    GetAttemptHandler,
    OpenAttemptCommand,
    OpenAttemptHandler,
    RequestStepCommand,
    RequestStepHandler,
    SubmitOwnAnswerCommand,
    SubmitOwnAnswerHandler,
)
from frobi.modules.tutoring.domain import (
    AdaptationNotAvailable,
    AttemptNotFound,
    FinalLocked,
    HelpAttempt,
    HelpStep,
    ReachedStep,
)

ANA = uuid4()
CLASS_ID = uuid4()


@pytest.fixture
def attempts() -> InMemoryAttempts:
    return InMemoryAttempts()


async def _open(attempts: InMemoryAttempts, adaptation_id: UUID = ADAPTATION_ID) -> HelpAttempt:
    return await OpenAttemptHandler(
        FakeUnitOfWork(), attempts, StaticContexts(ANA), FixedClock()
    ).handle(
        OpenAttemptCommand(
            person_id=ANA, class_id=CLASS_ID, adaptation_id=adaptation_id, task_ref="ej-1"
        )
    )


def _steps(attempts: InMemoryAttempts, hints: EchoHints | None = None) -> RequestStepHandler:
    return RequestStepHandler(FakeUnitOfWork(), attempts, StaticContexts(ANA), hints or EchoHints())


async def test_opening_stores_the_attempt_with_its_class(attempts: InMemoryAttempts) -> None:
    attempt = await _open(attempts)

    assert attempts.items[attempt.id].class_id == CLASS_ID


async def test_cannot_open_on_an_adaptation_i_cannot_see(attempts: InMemoryAttempts) -> None:
    with pytest.raises(AdaptationNotAvailable):
        await _open(attempts, adaptation_id=uuid4())


async def test_a_step_advances_locks_the_row_and_returns_its_help(
    attempts: InMemoryAttempts,
) -> None:
    attempt = await _open(attempts)
    hints = EchoHints()

    result = await _steps(attempts, hints).handle(
        RequestStepCommand(person_id=ANA, attempt_id=attempt.id, step=HelpStep.HINT_1)
    )

    assert result.content == "ayuda hint_1"
    assert result.attempt.max_step is ReachedStep.HINT_1
    assert attempts.items[attempt.id].max_step is ReachedStep.HINT_1
    assert attempts.locked == [attempt.id]


async def test_a_locked_final_asks_no_help_and_saves_nothing(attempts: InMemoryAttempts) -> None:
    attempt = await _open(attempts)
    hints = EchoHints()

    with pytest.raises(FinalLocked):
        await _steps(attempts, hints).handle(
            RequestStepCommand(person_id=ANA, attempt_id=attempt.id, step=HelpStep.FINAL)
        )

    assert hints.asked == []
    assert attempts.items[attempt.id].max_step is ReachedStep.NONE


async def test_someone_elses_attempt_looks_like_it_does_not_exist(
    attempts: InMemoryAttempts,
) -> None:
    attempt = await _open(attempts)

    with pytest.raises(AttemptNotFound):
        await _steps(attempts).handle(
            RequestStepCommand(person_id=uuid4(), attempt_id=attempt.id, step=HelpStep.HINT_1)
        )
    with pytest.raises(AttemptNotFound):
        await GetAttemptHandler(attempts).handle(uuid4(), attempt.id)


async def test_own_answer_matching_the_guide_counts_as_solved_without_ai(
    attempts: InMemoryAttempts,
) -> None:
    attempt = await _open(attempts)

    result = await SubmitOwnAnswerHandler(FakeUnitOfWork(), attempts, StaticContexts(ANA)).handle(
        SubmitOwnAnswerCommand(
            person_id=ANA,
            attempt_id=attempt.id,
            answer="El capacitivo, porque detecta líquidos y plásticos",
            self_check=("Revisé la guía",),
        )
    )

    assert result.attempt.solved_without_ai is True
    assert result.attempt.final_unlocked is True
    assert result.matching_passages
    assert attempts.items[attempt.id].own_answer is not None


async def test_own_answer_that_does_not_match_is_not_solved(attempts: InMemoryAttempts) -> None:
    attempt = await _open(attempts)

    result = await SubmitOwnAnswerHandler(FakeUnitOfWork(), attempts, StaticContexts(ANA)).handle(
        SubmitOwnAnswerCommand(person_id=ANA, attempt_id=attempt.id, answer="No lo sé")
    )

    assert result.matching_passages == []
    assert result.attempt.solved_without_ai is False
    assert result.attempt.final_unlocked is True
