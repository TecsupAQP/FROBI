from uuid import UUID, uuid4

import pytest

from fakes.adaptations import Limiter, ScriptedLlm
from fakes.identity import FakeUnitOfWork, FixedClock
from frobi.modules.comprehension.application import (
    AnswerQuestionCommand,
    AnswerQuestionHandler,
    GenerateQuestionsHandler,
)
from frobi.modules.comprehension.application.ports import QuizContext
from frobi.modules.comprehension.domain import (
    AdaptationNotAvailable,
    Answer,
    NotEnoughMaterial,
    Question,
    QuestionKind,
    QuestionNotFound,
)
from frobi.modules.comprehension.infrastructure import (
    FallbackQuestionGenerator,
    LlmQuestionGenerator,
    ResilientQuestionGenerator,
)

ANA = uuid4()
ADAPTATION = uuid4()
SAMPLE = UUID("00000000-0000-4000-8000-00000000a001")
SAMPLE_CONTEXT = QuizContext(ADAPTATION, SAMPLE, "Guía", "texto", "easy_read")
NOTES_CONTEXT = QuizContext(
    ADAPTATION,
    uuid4(),
    "Notas",
    "El termopar mide temperatura mediante la unión de dos metales distintos. "
    "Un transmisor convierte la presión del fluido en una corriente eléctrica estable. "
    "Los sensores capacitivos permiten medir el nivel de líquidos dentro de tanques.",
    "audio",
)
VALID_LLM = {
    "questions": [
        {
            "statement": "¿Qué mide un termopar?",
            "options": ["Presión", "Temperatura", "Nivel"],
            "correct_index": 1,
            "feedback_correct": "Bien",
            "feedback_wrong": "Revisa",
        }
    ]
}


async def _fallback(context: QuizContext, kind: QuestionKind, n: int, skip: int = 0):  # type: ignore[no-untyped-def]
    return await FallbackQuestionGenerator().generate(
        requested_by=ANA, context=context, kind=kind, n=n, skip=skip
    )


async def test_the_sample_guide_has_prewritten_questions_that_rotate() -> None:
    first = await _fallback(SAMPLE_CONTEXT, QuestionKind.COMPREHENSION, 3)
    second = await _fallback(SAMPLE_CONTEXT, QuestionKind.COMPREHENSION, 3, skip=3)

    assert len(first) == 3
    assert first[0].statement == "¿Qué sensor detecta una botella de plástico?"
    assert second[0].statement != first[0].statement


async def test_the_sample_guide_has_transfer_questions() -> None:
    [question] = await _fallback(SAMPLE_CONTEXT, QuestionKind.TRANSFER, 1)

    assert "envasado de jugo" in question.statement


async def test_other_materials_get_fill_in_the_blank_questions() -> None:
    questions = await _fallback(NOTES_CONTEXT, QuestionKind.COMPREHENSION, 3)

    assert questions
    assert all("_____" in q.statement for q in questions)


def _resilient(llm: ScriptedLlm, timeout: float = 1.0) -> ResilientQuestionGenerator:
    return ResilientQuestionGenerator(
        LlmQuestionGenerator(llm), FallbackQuestionGenerator(), Limiter(True), timeout
    )


async def test_valid_ai_questions_are_used() -> None:
    [question] = await _resilient(ScriptedLlm(reply=VALID_LLM)).generate(
        requested_by=ANA, context=SAMPLE_CONTEXT, kind=QuestionKind.COMPREHENSION, n=1
    )

    assert question.statement == "¿Qué mide un termopar?"
    correct = next(o.text for o in question.options if o.id == question.correct_option)
    assert correct == "Temperatura"


async def test_right_answers_do_not_always_sit_at_the_same_letter() -> None:
    questions = await _fallback(SAMPLE_CONTEXT, QuestionKind.COMPREHENSION, 5)

    assert len({q.correct_option for q in questions}) > 1
    first = next(o.text for o in questions[0].options if o.id == questions[0].correct_option)
    assert first == "Capacitivo"


@pytest.mark.parametrize(
    "llm",
    [
        ScriptedLlm(reply={"questions": [{**VALID_LLM["questions"][0], "correct_index": 3}]}),
        ScriptedLlm(
            reply={"questions": [{**VALID_LLM["questions"][0], "options": ["x", "x", "y"]}]}
        ),
        ScriptedLlm(reply={"preguntas": []}),
        ScriptedLlm(reply=VALID_LLM, delay=2),
    ],
    ids=["index-out-of-range", "repeated-options", "wrong-shape", "slow"],
)
async def test_bad_or_slow_ai_questions_fall_back(llm: ScriptedLlm) -> None:
    questions = await _resilient(llm, timeout=0.05).generate(
        requested_by=ANA, context=SAMPLE_CONTEXT, kind=QuestionKind.COMPREHENSION, n=3
    )

    assert questions[0].statement == "¿Qué sensor detecta una botella de plástico?"


class Questions:
    def __init__(self) -> None:
        self.items: dict[UUID, Question] = {}

    async def add_all(self, questions: list[Question]) -> None:
        self.items.update({q.id: q for q in questions})

    async def get(self, question_id: UUID) -> Question | None:
        return self.items.get(question_id)

    async def count(self, adaptation_id: UUID, kind: QuestionKind) -> int:
        return sum(
            1 for q in self.items.values() if q.adaptation_id == adaptation_id and q.kind is kind
        )


class Answers:
    def __init__(self) -> None:
        self.items: list[Answer] = []

    async def add(self, answer: Answer) -> None:
        self.items.append(answer)


class Contexts:
    def __init__(self, context: QuizContext) -> None:
        self._context = context

    async def get(self, person_id: UUID, adaptation_id: UUID) -> QuizContext | None:
        return self._context if person_id == ANA and adaptation_id == ADAPTATION else None


def _generate(
    questions: Questions, context: QuizContext = SAMPLE_CONTEXT
) -> GenerateQuestionsHandler:
    return GenerateQuestionsHandler(
        FakeUnitOfWork(), questions, Contexts(context), FallbackQuestionGenerator(), FixedClock()
    )


async def test_generate_stores_3_questions_with_the_adaptation_format() -> None:
    questions = Questions()

    created = await _generate(questions).handle(ANA, ADAPTATION, QuestionKind.COMPREHENSION)

    assert len(created) == 3
    assert all(q.source_format == "easy_read" for q in created)
    assert set(questions.items) == {q.id for q in created}


async def test_asking_again_gives_new_questions() -> None:
    questions = Questions()
    handler = _generate(questions)

    first = await handler.handle(ANA, ADAPTATION, QuestionKind.COMPREHENSION)
    second = await handler.handle(ANA, ADAPTATION, QuestionKind.COMPREHENSION)

    assert first[0].statement != second[0].statement


async def test_cannot_generate_for_an_adaptation_i_cannot_see() -> None:
    with pytest.raises(AdaptationNotAvailable):
        await _generate(Questions()).handle(uuid4(), ADAPTATION, QuestionKind.COMPREHENSION)


async def test_a_too_short_material_is_a_clear_error() -> None:
    short = QuizContext(ADAPTATION, uuid4(), "Notas", "Hola.", "audio")

    with pytest.raises(NotEnoughMaterial):
        await _generate(Questions(), short).handle(ANA, ADAPTATION, QuestionKind.COMPREHENSION)


async def test_answering_records_the_class_and_the_verdict() -> None:
    questions, answers, class_id = Questions(), Answers(), uuid4()
    [question, *_] = await _generate(questions).handle(ANA, ADAPTATION, QuestionKind.COMPREHENSION)
    wrong = next(o.id for o in question.options if o.id != question.correct_option)

    answer = await AnswerQuestionHandler(FakeUnitOfWork(), questions, answers, FixedClock()).handle(
        AnswerQuestionCommand(
            person_id=ANA, class_id=class_id, question_id=question.id, option=f" {wrong.upper()} "
        )
    )

    assert answers.items == [answer]
    assert answer.chosen_option == wrong
    assert answer.class_id == class_id
    assert answer.verdict.is_correct is False
    assert answer.verdict.suggested_format == "visual_map"


async def test_someone_elses_question_cannot_be_answered() -> None:
    questions = Questions()
    [question, *_] = await _generate(questions).handle(ANA, ADAPTATION, QuestionKind.COMPREHENSION)

    with pytest.raises(QuestionNotFound):
        await AnswerQuestionHandler(FakeUnitOfWork(), questions, Answers(), FixedClock()).handle(
            AnswerQuestionCommand(
                person_id=uuid4(), class_id=None, question_id=question.id, option="b"
            )
        )
