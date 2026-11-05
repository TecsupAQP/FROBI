from collections.abc import AsyncIterator, Sequence
from uuid import UUID

from frobi.modules.assistant.application.ports import (
    Answered,
    AssistantEvent,
    AssistantTool,
    AssistantUnavailable,
    JsonObject,
    PersonContext,
    TextChunk,
    ToolUsed,
)
from frobi.modules.assistant.domain import Conversation

LEARNER = PersonContext(
    alias="Ana", is_teacher=False, career="Mecatrónica", class_name="SENSOR1", preferences=()
)
TEACHER = PersonContext(
    alias="Marisol", is_teacher=True, career="Mecatrónica", class_name=None, preferences=()
)


class ScriptedModel:
    """Streams ``chunks``, then answers; ``fail_after`` chunks it raises AssistantUnavailable."""

    def __init__(self, chunks: Sequence[str] = ("Hola", ", Ana."), fail_after: int | None = None):
        self.chunks = chunks
        self.fail_after = fail_after
        self.calls: list[dict[str, object]] = []

    async def reply(
        self,
        *,
        person: PersonContext,
        history: Sequence[JsonObject],
        question: str,
        tools: Sequence[AssistantTool],
    ) -> AsyncIterator[AssistantEvent]:
        self.calls.append(
            {
                "person": person,
                "history": list(history),
                "question": question,
                "tools": [t.name for t in tools],
            }
        )
        yield ToolUsed("Revisando tu progreso…")
        for index, chunk in enumerate(self.chunks):
            if self.fail_after is not None and index >= self.fail_after:
                raise AssistantUnavailable("down")
            yield TextChunk(chunk)
        if self.fail_after is not None:
            raise AssistantUnavailable("down")
        state = (
            *history,
            {"role": "user", "content": question},
            {"role": "assistant", "content": [{"type": "text", "text": "".join(self.chunks)}]},
        )
        yield Answered(model_state=state)


class InMemoryConversations:
    def __init__(self) -> None:
        self.items: dict[UUID, Conversation] = {}

    async def load(self, person_id: UUID) -> Conversation:
        return self.items.get(person_id, Conversation())

    async def save(self, person_id: UUID, conversation: Conversation) -> None:
        self.items[person_id] = conversation

    async def clear(self, person_id: UUID) -> None:
        self.items.pop(person_id, None)


class FixedBudget:
    def __init__(self, allow: bool = True) -> None:
        self.allowed = allow

    async def allow(self, person_id: UUID) -> bool:
        return self.allowed


class InMemoryLock:
    def __init__(self) -> None:
        self.held_by: set[UUID] = set()

    async def acquire(self, person_id: UUID) -> bool:
        if person_id in self.held_by:
            return False
        self.held_by.add(person_id)
        return True

    async def release(self, person_id: UUID) -> None:
        self.held_by.discard(person_id)

    async def held(self, person_id: UUID) -> bool:
        return person_id in self.held_by


class FakeStudyData:
    """One learner (Ana) with one guide; one teacher (Marisol) with one class."""

    def __init__(self, ana: UUID, marisol: UUID, guide_id: UUID, class_id: UUID) -> None:
        self.ana, self.marisol, self.guide_id, self.class_id = ana, marisol, guide_id, class_id
        self.guide_text = "Los sensores inductivos detectan metales."

    async def person(self, person_id: UUID) -> PersonContext | None:
        return {self.ana: LEARNER, self.marisol: TEACHER}.get(person_id)

    async def guides(self, person_id: UUID) -> list[JsonObject]:
        return [{"id": str(self.guide_id), "title": "Sensores"}] if person_id == self.ana else []

    async def guide(self, person_id: UUID, material_id: UUID) -> JsonObject | None:
        if person_id == self.ana and material_id == self.guide_id:
            return {"id": str(material_id), "title": "Sensores", "text": self.guide_text}
        return None

    async def progress(self, person_id: UUID) -> JsonObject:
        return {"owner": str(person_id), "solved_without_ai": 2}

    async def my_classes(self, teacher_id: UUID) -> list[JsonObject]:
        return [{"id": str(self.class_id)}] if teacher_id == self.marisol else []

    async def class_panel(self, teacher_id: UUID, class_id: UUID) -> JsonObject | None:
        if teacher_id == self.marisol and class_id == self.class_id:
            return {"students": [{"alias": "Ana"}]}
        return None

    async def student(
        self, teacher_id: UUID, class_id: UUID, student_id: UUID
    ) -> JsonObject | None:
        if teacher_id == self.marisol and class_id == self.class_id and student_id == self.ana:
            return {"alias": "Ana"}
        return None
