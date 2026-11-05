"""A conversation with FROBI's assistant: what the person sees and what the model needs."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from .errors import MAX_QUESTION_CHARS, ConversationFull, EmptyQuestion, QuestionTooLong

# Every question resends the whole conversation; past this many it gets slow and costly, so the
# person starts a new one (the model's history is append-only, it is never trimmed).
MAX_QUESTIONS = 30


class Speaker(StrEnum):
    PERSON = "person"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class ChatLine:
    speaker: Speaker
    text: str


def normalize_question(raw: str) -> str:
    question = raw.strip()
    if not question:
        raise EmptyQuestion()
    if len(question) > MAX_QUESTION_CHARS:
        raise QuestionTooLong()
    return question


@dataclass(frozen=True, slots=True)
class Conversation:
    """``lines`` is what the person sees; ``model_state`` is the provider's own history, opaque
    here and only appended to (it carries tool calls and reasoning the screen never shows)."""

    lines: tuple[ChatLine, ...] = ()
    model_state: tuple[dict[str, Any], ...] = field(default=())

    @property
    def questions(self) -> int:
        return sum(1 for line in self.lines if line.speaker is Speaker.PERSON)

    @property
    def questions_left(self) -> int:
        return max(0, MAX_QUESTIONS - self.questions)

    def ensure_room(self) -> None:
        if self.questions >= MAX_QUESTIONS:
            raise ConversationFull()

    def answered(
        self, question: str, answer: str, model_state: tuple[dict[str, Any], ...]
    ) -> "Conversation":
        return Conversation(
            lines=(
                *self.lines,
                ChatLine(Speaker.PERSON, question),
                ChatLine(Speaker.ASSISTANT, answer),
            ),
            model_state=model_state,
        )
