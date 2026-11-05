"""Multiple-choice questions about a material, and answers to them (RF13, RF14, RF24)."""

import hashlib
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .errors import InvalidOption, InvalidQuestion

# The 4 adaptation formats, by name (comprehension does not import adaptations' domain).
FORMATS = ("visual_map", "real_example", "easy_read", "audio")
_NEXT_FORMAT = {
    "visual_map": "real_example",
    "real_example": "easy_read",
    "easy_read": "visual_map",
    "audio": "visual_map",
}


def suggest_other_format(current: str) -> str:
    """«Prueba con…»: a different way into the same material after a wrong answer (RF14)."""
    return _NEXT_FORMAT.get(current, "visual_map")


class QuestionKind(StrEnum):
    COMPREHENSION = "comprehension"
    TRANSFER = "transfer"


@dataclass(frozen=True, slots=True)
class Option:
    id: str
    text: str


@dataclass(frozen=True, slots=True)
class QuestionDraft:
    statement: str
    options: tuple[Option, ...]
    correct_option: str
    feedback_correct: str
    feedback_wrong: str

    def validate(self) -> "QuestionDraft":
        ids = [o.id for o in self.options]
        if not self.statement.strip():
            raise InvalidQuestion("empty statement")
        if not 2 <= len(ids) <= 5 or len(set(ids)) != len(ids):
            raise InvalidQuestion("2 to 5 options with unique ids")
        if len({o.text.strip().lower() for o in self.options}) != len(ids):
            raise InvalidQuestion("repeated option text")
        if self.correct_option not in ids:
            raise InvalidQuestion("correct option is not among the options")
        return self

    def shuffled(self) -> "QuestionDraft":
        """Reorder options by a hash of their text and relabel them a, b, c…

        Deterministic (same question, same order) but the right answer no longer sits at the
        same letter across questions, so it cannot be guessed from a pattern.
        """
        correct_text = next(o.text for o in self.options if o.id == self.correct_option)

        def key(option: Option) -> str:
            return hashlib.sha256(f"{self.statement}\x00{option.text}".encode()).hexdigest()

        ordered = sorted(self.options, key=key)
        letters = "abcde"
        options = tuple(Option(letters[i], o.text) for i, o in enumerate(ordered))
        correct = next(o.id for o in options if o.text == correct_text)
        return replace(self, options=options, correct_option=correct).validate()


@dataclass(frozen=True, slots=True)
class Verdict:
    is_correct: bool
    correct_option: str
    feedback: str
    suggested_format: str | None


@dataclass(frozen=True, slots=True)
class Question:
    id: UUID
    person_id: UUID
    adaptation_id: UUID
    kind: QuestionKind
    statement: str
    options: tuple[Option, ...]
    correct_option: str
    feedback_correct: str
    feedback_wrong: str
    source_format: str
    created_at: datetime

    @classmethod
    def from_draft(
        cls,
        draft: QuestionDraft,
        *,
        person_id: UUID,
        adaptation_id: UUID,
        kind: QuestionKind,
        source_format: str,
        now: datetime,
    ) -> "Question":
        draft.validate()
        return cls(
            id=uuid4(),
            person_id=person_id,
            adaptation_id=adaptation_id,
            kind=kind,
            statement=draft.statement.strip(),
            options=draft.options,
            correct_option=draft.correct_option,
            feedback_correct=draft.feedback_correct,
            feedback_wrong=draft.feedback_wrong,
            source_format=source_format,
            created_at=now,
        )

    @property
    def used_help(self) -> bool:
        """Comprehension questions are answered with the adaptation at hand; transfer ones not."""
        return self.kind is QuestionKind.COMPREHENSION

    def visible_to(self, person_id: UUID) -> bool:
        return self.person_id == person_id

    def judge(self, option: str) -> Verdict:
        if option not in {o.id for o in self.options}:
            raise InvalidOption()
        correct = option == self.correct_option
        return Verdict(
            is_correct=correct,
            correct_option=self.correct_option,
            feedback=self.feedback_correct if correct else self.feedback_wrong,
            suggested_format=None if correct else suggest_other_format(self.source_format),
        )


@dataclass(frozen=True, slots=True)
class Answer:
    id: UUID
    question_id: UUID
    person_id: UUID
    class_id: UUID | None
    chosen_option: str
    verdict: Verdict
    used_help: bool
    created_at: datetime

    @classmethod
    def to(
        cls, question: Question, option: str, *, class_id: UUID | None, now: datetime
    ) -> "Answer":
        return cls(
            id=uuid4(),
            question_id=question.id,
            person_id=question.person_id,
            class_id=class_id,
            chosen_option=option,
            verdict=question.judge(option),
            used_help=question.used_help,
            created_at=now,
        )
