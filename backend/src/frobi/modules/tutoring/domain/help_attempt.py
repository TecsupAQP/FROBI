"""The help ladder (RF39-RF43): hint 1 → hint 2 → step by step → final answer.

Rules, all enforced here:
- Only the next step can be opened; skipping one is ``StepOutOfOrder``.
- The final answer stays locked until the person submits their own attempt (``FinalLocked``).
- Asking again for a step already opened just shows it again (a double click does not advance).
- «Resuelto sin IA» means the own attempt matched the guide before any hint was opened.
"""

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .errors import FinalLocked, StepOutOfOrder


class HelpStep(StrEnum):
    HINT_1 = "hint_1"
    HINT_2 = "hint_2"
    STEP_BY_STEP = "step_by_step"
    FINAL = "final"


class ReachedStep(StrEnum):
    NONE = "none"
    HINT_1 = "hint_1"
    HINT_2 = "hint_2"
    STEP_BY_STEP = "step_by_step"
    FINAL = "final"


LADDER: tuple[HelpStep, ...] = tuple(HelpStep)
LEVEL_LABELS: dict[ReachedStep, str] = {
    ReachedStep.NONE: "Nivel 0, sin ayuda",
    ReachedStep.HINT_1: "Nivel 1, con una pista",
    ReachedStep.HINT_2: "Nivel 2, con pistas",
    ReachedStep.STEP_BY_STEP: "Nivel 3, paso a paso",
    ReachedStep.FINAL: "Nivel 4, con la respuesta",
}


def _level(reached: ReachedStep) -> int:
    return list(ReachedStep).index(reached)


@dataclass(frozen=True, slots=True)
class HelpAttempt:
    id: UUID
    person_id: UUID
    class_id: UUID | None
    adaptation_id: UUID
    task_ref: str
    max_step: ReachedStep
    own_answer: str | None
    self_check: tuple[str, ...] = field(default_factory=tuple)
    solved_without_ai: bool = False
    created_at: datetime | None = None

    @classmethod
    def open(
        cls,
        *,
        person_id: UUID,
        class_id: UUID | None,
        adaptation_id: UUID,
        task_ref: str,
        now: datetime,
    ) -> "HelpAttempt":
        return cls(
            id=uuid4(),
            person_id=person_id,
            class_id=class_id,
            adaptation_id=adaptation_id,
            task_ref=" ".join(task_ref.split())[:120],
            max_step=ReachedStep.NONE,
            own_answer=None,
            created_at=now,
        )

    @property
    def help_level(self) -> int:
        return _level(self.max_step)

    @property
    def help_label(self) -> str:
        return LEVEL_LABELS[self.max_step]

    @property
    def next_step(self) -> HelpStep | None:
        level = self.help_level
        return LADDER[level] if level < len(LADDER) else None

    @property
    def final_unlocked(self) -> bool:
        return self.own_answer is not None

    def visible_to(self, person_id: UUID) -> bool:
        return self.person_id == person_id

    def request(self, step: HelpStep) -> "HelpAttempt":
        """Open ``step``; returns the attempt unchanged when the step was already open."""
        if step is HelpStep.FINAL and not self.final_unlocked:
            raise FinalLocked()
        wanted = _level(ReachedStep(step.value))
        if wanted <= self.help_level:
            return self
        if step is not self.next_step:
            raise StepOutOfOrder()
        return replace(self, max_step=ReachedStep(step.value))

    def submit_own_answer(
        self, answer: str, self_check: tuple[str, ...], *, matches_guide: bool
    ) -> "HelpAttempt":
        """«Inténtalo sin IA». Unlocks the final answer; may count as solved without AI."""
        solved = self.solved_without_ai or (matches_guide and self.max_step is ReachedStep.NONE)
        return replace(
            self,
            own_answer=answer.strip(),
            self_check=tuple(dict.fromkeys(c.strip() for c in self_check if c.strip())),
            solved_without_ai=solved,
        )
