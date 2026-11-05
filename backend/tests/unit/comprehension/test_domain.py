from datetime import UTC, datetime
from uuid import uuid4

import pytest

from frobi.modules.comprehension.domain import (
    Answer,
    InvalidOption,
    InvalidQuestion,
    Option,
    Question,
    QuestionDraft,
    QuestionKind,
    cloze_questions,
    suggest_other_format,
)

NOW = datetime(2026, 11, 5, 13, 0, tzinfo=UTC)
DRAFT = QuestionDraft(
    statement="¿Qué sensor detecta plástico?",
    options=(Option("a", "Inductivo"), Option("b", "Capacitivo"), Option("c", "Termopar")),
    correct_option="b",
    feedback_correct="Bien",
    feedback_wrong="Revisa capacitivos",
)


def _question(kind: QuestionKind = QuestionKind.COMPREHENSION, fmt: str = "easy_read") -> Question:
    return Question.from_draft(
        DRAFT, person_id=uuid4(), adaptation_id=uuid4(), kind=kind, source_format=fmt, now=NOW
    )


def test_a_right_answer_gets_praise_and_no_suggestion() -> None:
    verdict = _question().judge("b")

    assert verdict.is_correct is True
    assert verdict.feedback == "Bien"
    assert verdict.suggested_format is None


def test_a_wrong_answer_suggests_a_different_format() -> None:
    verdict = _question(fmt="easy_read").judge("a")

    assert verdict.is_correct is False
    assert verdict.correct_option == "b"
    assert verdict.feedback == "Revisa capacitivos"
    assert verdict.suggested_format == "visual_map"


@pytest.mark.parametrize("fmt", ["visual_map", "real_example", "easy_read", "audio"])
def test_the_suggested_format_is_never_the_one_already_used(fmt: str) -> None:
    assert suggest_other_format(fmt) != fmt


def test_an_unknown_option_is_rejected() -> None:
    with pytest.raises(InvalidOption):
        _question().judge("z")


def test_transfer_answers_are_recorded_without_help() -> None:
    comprehension = Answer.to(_question(), "b", class_id=None, now=NOW)
    transfer = Answer.to(_question(QuestionKind.TRANSFER), "b", class_id=None, now=NOW)

    assert comprehension.used_help is True
    assert transfer.used_help is False


@pytest.mark.parametrize(
    "broken",
    [
        QuestionDraft("¿?", (Option("a", "x"),), "a", "", ""),
        QuestionDraft("¿?", (Option("a", "x"), Option("a", "y")), "a", "", ""),
        QuestionDraft("¿?", (Option("a", "x"), Option("b", "X")), "a", "", ""),
        QuestionDraft("¿?", (Option("a", "x"), Option("b", "y")), "c", "", ""),
        QuestionDraft("  ", (Option("a", "x"), Option("b", "y")), "a", "", ""),
    ],
    ids=["one-option", "repeated-id", "repeated-text", "correct-missing", "blank"],
)
def test_malformed_questions_are_refused(broken: QuestionDraft) -> None:
    with pytest.raises(InvalidQuestion):
        broken.validate()


NOTES = """## Termopares
El termopar mide temperatura mediante la unión de dos metales distintos.
## Presión
Un transmisor convierte la presión del fluido en una corriente eléctrica estable.
## Nivel
Los sensores capacitivos permiten medir el nivel de líquidos dentro de tanques plásticos."""


def test_cloze_blanks_a_topic_word_and_offers_two_others_from_the_material() -> None:
    questions = cloze_questions(NOTES, 3)

    assert len(questions) == 3
    for q in questions:
        assert q.statement.startswith("Completa según tu material: «")
        assert "_____" in q.statement
        correct = next(o.text for o in q.options if o.id == q.correct_option)
        assert correct not in q.statement
        assert len(q.options) == 3
        assert [o.text.lower() for o in q.options] == sorted(o.text.lower() for o in q.options)


def test_cloze_is_deterministic_and_skip_gives_other_questions() -> None:
    first = cloze_questions(NOTES, 1)
    again = cloze_questions(NOTES, 1)
    later = cloze_questions(NOTES, 1, skip=1)

    assert first == again
    assert later[0].statement != first[0].statement


def test_too_little_material_gives_no_questions() -> None:
    assert cloze_questions("Hola.", 3) == []
