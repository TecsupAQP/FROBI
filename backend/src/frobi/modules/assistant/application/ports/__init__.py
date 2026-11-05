from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from frobi.modules.assistant.domain import Conversation

JsonObject = dict[str, Any]


@dataclass(frozen=True, slots=True)
class PersonContext:
    """Who is asking, so the assistant answers for their role and the way they read best."""

    alias: str
    is_teacher: bool
    career: str
    class_name: str | None
    preferences: tuple[str, ...]


class ToolFailed(Exception):
    """A tool could not answer (bad input, nothing found). The message goes back to the model."""


@dataclass(frozen=True, slots=True)
class AssistantTool:
    """One thing the assistant may look up. ``run`` already knows who is asking: the model never
    chooses whose data it reads (RNF08)."""

    name: str
    description: str
    input_schema: JsonObject
    status: str  # Shown while it runs: «Revisando tu progreso…»
    run: Callable[[JsonObject], Awaitable[JsonObject]]


@dataclass(frozen=True, slots=True)
class TextChunk:
    text: str


@dataclass(frozen=True, slots=True)
class ToolUsed:
    status: str


@dataclass(frozen=True, slots=True)
class Answered:
    """End of a reply. ``model_state`` is the provider history to resend next time."""

    model_state: tuple[JsonObject, ...]


AssistantEvent = TextChunk | ToolUsed | Answered


class AssistantUnavailable(Exception):
    """No provider, a provider error or a declined request: the person gets a fallback reply."""


class AssistantModel(Protocol):
    def reply(
        self,
        *,
        person: PersonContext,
        history: Sequence[JsonObject],
        question: str,
        tools: Sequence[AssistantTool],
    ) -> AsyncIterator[AssistantEvent]:
        """Streams the answer and ends with ``Answered``, or raises ``AssistantUnavailable``."""
        ...


class ConversationStore(Protocol):
    async def load(self, person_id: UUID) -> Conversation: ...

    async def save(self, person_id: UUID, conversation: Conversation) -> None: ...

    async def clear(self, person_id: UUID) -> None: ...


class QuestionBudget(Protocol):
    async def allow(self, person_id: UUID) -> bool: ...


class AnswerLock(Protocol):
    """One answer at a time per person, across every API instance and open tab."""

    async def acquire(self, person_id: UUID) -> bool: ...

    async def release(self, person_id: UUID) -> None: ...

    async def held(self, person_id: UUID) -> bool: ...


class StudyData(Protocol):
    """What the assistant can read, always through the rules of the module that owns it."""

    async def person(self, person_id: UUID) -> PersonContext | None: ...

    async def guides(self, person_id: UUID) -> list[JsonObject]: ...

    async def guide(self, person_id: UUID, material_id: UUID) -> JsonObject | None:
        """Title and text of a guide the person may see; None otherwise."""
        ...

    async def progress(self, person_id: UUID) -> JsonObject: ...

    async def my_classes(self, teacher_id: UUID) -> list[JsonObject]: ...

    async def class_panel(self, teacher_id: UUID, class_id: UUID) -> JsonObject | None:
        """Panel of a class this teacher teaches; None for any other class."""
        ...

    async def student(
        self, teacher_id: UUID, class_id: UUID, student_id: UUID
    ) -> JsonObject | None: ...


__all__ = [
    "AnswerLock",
    "Answered",
    "AssistantEvent",
    "AssistantModel",
    "AssistantTool",
    "AssistantUnavailable",
    "ConversationStore",
    "JsonObject",
    "PersonContext",
    "QuestionBudget",
    "StudyData",
    "TextChunk",
    "ToolFailed",
    "ToolUsed",
]
