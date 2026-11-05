"""Read or restart the person's conversation with the assistant."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.assistant.application.ports import AnswerLock, ConversationStore
from frobi.modules.assistant.domain import ChatLine, StillAnswering


@dataclass(frozen=True, slots=True)
class ConversationView:
    lines: tuple[ChatLine, ...]
    questions_left: int
    answering: bool


class ConversationHandler:
    def __init__(self, conversations: ConversationStore, lock: AnswerLock) -> None:
        self._conversations = conversations
        self._lock = lock

    async def read(self, person_id: UUID) -> ConversationView:
        conversation = await self._conversations.load(person_id)
        return ConversationView(
            conversation.lines, conversation.questions_left, await self._lock.held(person_id)
        )

    async def restart(self, person_id: UUID) -> None:
        if await self._lock.held(person_id):
            raise StillAnswering()
        await self._conversations.clear(person_id)
