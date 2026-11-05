"""What classrooms needs, in its own words. Adapters live in classrooms/infrastructure."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.modules.classrooms.domain import Classroom, Membership
from frobi.shared.application import AnswerRow, FormatUse, HelpUse, PromptScoreRow


class ClassRepository(Protocol):
    async def add(self, classroom: Classroom) -> None: ...

    async def get(self, class_id: UUID) -> Classroom | None: ...

    async def get_by_code(self, code: str) -> Classroom | None: ...

    async def code_taken(self, code: str) -> bool: ...


class MembershipRepository(Protocol):
    async def add(self, membership: Membership) -> None: ...

    async def save(self, membership: Membership) -> None: ...

    async def active_for(self, person_id: UUID) -> Membership | None:
        """The person's ``joined`` membership; there is at most one."""
        ...

    async def for_class(self, class_id: UUID) -> list[Membership]: ...


class PersonDirectory(Protocol):
    """Over the public API of identity."""

    async def is_teacher(self, person_id: UUID) -> bool: ...

    async def alias_of(self, person_id: UUID) -> str | None: ...


class CodeGenerator(Protocol):
    def __call__(self) -> str: ...


@dataclass(frozen=True, slots=True)
class ClassActivity:
    formats: list[FormatUse]
    help: list[HelpUse]
    answers: list[AnswerRow]
    prompt_scores: list[PromptScoreRow]

    @property
    def empty(self) -> bool:
        return not (self.formats or self.help or self.answers or self.prompt_scores)


class ClassActivityReader(Protocol):
    """Activity recorded with this ``class_id`` — the argument is mandatory, there is no
    «all activity» read for the panel (RNF16)."""

    async def read(self, class_id: UUID) -> ClassActivity: ...


__all__ = [
    "ClassActivity",
    "ClassActivityReader",
    "ClassRepository",
    "CodeGenerator",
    "MembershipRepository",
    "PersonDirectory",
]
