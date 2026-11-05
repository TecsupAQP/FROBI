"""Ask FROBI's assistant: check the question, then stream the answer and keep the conversation."""

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from frobi.modules.assistant.application.fallback import INTERRUPTED, unavailable_for
from frobi.modules.assistant.application.ports import (
    Answered,
    AnswerLock,
    AssistantModel,
    AssistantTool,
    AssistantUnavailable,
    ConversationStore,
    PersonContext,
    QuestionBudget,
    StudyData,
    TextChunk,
    ToolUsed,
)
from frobi.modules.assistant.application.tools import learner_tools, teacher_tools
from frobi.modules.assistant.domain import (
    Conversation,
    StillAnswering,
    TooManyQuestions,
    normalize_question,
)
from frobi.shared.application import Unauthenticated

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AskCommand:
    person_id: UUID
    question: str
    # The guide the person has open, so «¿qué dice este tema?» needs no id.
    open_guide: UUID | None = None


@dataclass(frozen=True, slots=True)
class Question:
    """A question that passed every check and holds the person's answer lock."""

    person_id: UUID
    text: str
    person: PersonContext
    conversation: Conversation
    tools: tuple[AssistantTool, ...]


@dataclass(frozen=True, slots=True)
class Finished:
    fallback: bool
    questions_left: int


AnswerEvent = TextChunk | ToolUsed | Finished


class AskAssistantHandler:
    def __init__(
        self,
        model: AssistantModel,
        conversations: ConversationStore,
        data: StudyData,
        budget: QuestionBudget,
        lock: AnswerLock,
    ) -> None:
        self._model = model
        self._conversations = conversations
        self._data = data
        self._budget = budget
        self._lock = lock

    async def prepare(self, command: AskCommand) -> Question:
        """Every check that can fail before the answer starts. Takes the answer lock."""
        text = normalize_question(command.question)
        person = await self._data.person(command.person_id)
        if person is None:
            raise Unauthenticated()
        conversation = await self._conversations.load(command.person_id)
        conversation.ensure_room()
        if not await self._lock.acquire(command.person_id):
            raise StillAnswering()
        try:
            if not await self._budget.allow(command.person_id):
                raise TooManyQuestions()
        except BaseException:
            await self._lock.release(command.person_id)
            raise
        build = teacher_tools if person.is_teacher else learner_tools
        tools = build(self._data, command.person_id, command.open_guide)
        return Question(command.person_id, text, person, conversation, tuple(tools))

    async def answer(self, question: Question) -> AsyncIterator[AnswerEvent]:
        """Streams the answer, then saves it. Always releases the lock and always ends with
        ``Finished``: when the AI fails the person still gets a useful reply (RNF03)."""
        parts: list[str] = []
        try:
            async for event in self._model.reply(
                person=question.person,
                history=question.conversation.model_state,
                question=question.text,
                tools=question.tools,
            ):
                if isinstance(event, Answered):
                    conversation = question.conversation.answered(
                        question.text, "".join(parts).strip(), event.model_state
                    )
                    await self._conversations.save(question.person_id, conversation)
                    yield Finished(fallback=False, questions_left=conversation.questions_left)
                    return
                if isinstance(event, TextChunk):
                    parts.append(event.text)
                yield event
            raise AssistantUnavailable("The model stopped without finishing its answer")
        except AssistantUnavailable:
            logger.warning("Assistant fallback for %s", question.person_id, exc_info=True)
            yield TextChunk(INTERRUPTED if parts else unavailable_for(question.person.is_teacher))
            yield Finished(fallback=True, questions_left=question.conversation.questions_left)
        finally:
            await self._lock.release(question.person_id)
