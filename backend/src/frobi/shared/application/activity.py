"""Read-only activity rows that modules expose to progress (M11) and the teacher panel (M12).

Each module answers two questions about its own activity, through its public API:
- of a person (all of it, for their own progress), and
- in a class: ``class_id`` is a mandatory argument with no default, so no query can forget the
  filter and leak what a student did outside the class (RNF16).
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class FormatUse:
    person_id: UUID
    format: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class HelpUse:
    person_id: UUID
    max_step: str
    own_answer: bool
    solved_without_ai: bool


@dataclass(frozen=True, slots=True)
class AnswerRow:
    person_id: UUID
    question_id: UUID
    statement: str
    format: str
    is_correct: bool
    used_help: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PromptScoreRow:
    person_id: UUID
    total: int
    autonomy_level: int
    created_at: datetime
