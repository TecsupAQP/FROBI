import pytest

from frobi.modules.assistant.domain import (
    MAX_QUESTION_CHARS,
    MAX_QUESTIONS,
    ChatLine,
    Conversation,
    ConversationFull,
    EmptyQuestion,
    QuestionTooLong,
    Speaker,
    normalize_question,
)


def test_question_is_trimmed() -> None:
    assert normalize_question("  ¿Cómo voy?  ") == "¿Cómo voy?"


@pytest.mark.parametrize("raw", ["", "   \n "])
def test_empty_question_is_rejected(raw: str) -> None:
    with pytest.raises(EmptyQuestion):
        normalize_question(raw)


def test_long_question_is_rejected() -> None:
    with pytest.raises(QuestionTooLong):
        normalize_question("a" * (MAX_QUESTION_CHARS + 1))


def test_an_answer_adds_both_lines_and_replaces_the_model_state() -> None:
    state = ({"role": "user", "content": "Hola"},)

    conversation = Conversation().answered("Hola", "¡Hola!", state)

    assert conversation.lines == (
        ChatLine(Speaker.PERSON, "Hola"),
        ChatLine(Speaker.ASSISTANT, "¡Hola!"),
    )
    assert conversation.model_state == state
    assert conversation.questions_left == MAX_QUESTIONS - 1


def test_a_full_conversation_asks_for_a_new_one() -> None:
    conversation = Conversation()
    for n in range(MAX_QUESTIONS):
        conversation = conversation.answered(f"p{n}", "r", ())

    with pytest.raises(ConversationFull):
        conversation.ensure_room()
