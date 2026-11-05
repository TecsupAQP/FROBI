from uuid import uuid4

import pytest

from fakes.assistant import (
    FakeStudyData,
    FixedBudget,
    InMemoryConversations,
    InMemoryLock,
    ScriptedModel,
)
from frobi.modules.assistant.application import (
    AskAssistantHandler,
    AskCommand,
    ConversationHandler,
    Finished,
)
from frobi.modules.assistant.application.fallback import INTERRUPTED, UNAVAILABLE
from frobi.modules.assistant.application.ports import TextChunk, ToolUsed
from frobi.modules.assistant.domain import (
    MAX_QUESTIONS,
    Conversation,
    ConversationFull,
    Speaker,
    StillAnswering,
    TooManyQuestions,
)
from frobi.shared.application import Unauthenticated

ANA, MARISOL, GUIDE, CLASS = uuid4(), uuid4(), uuid4(), uuid4()


class Setup:
    def __init__(self, model: ScriptedModel | None = None, budget: bool = True) -> None:
        self.model = model or ScriptedModel()
        self.conversations = InMemoryConversations()
        self.lock = InMemoryLock()
        self.handler = AskAssistantHandler(
            self.model,
            self.conversations,
            FakeStudyData(ANA, MARISOL, GUIDE, CLASS),
            FixedBudget(budget),
            self.lock,
        )

    async def ask(self, question: str = "¿Cómo voy?", person=ANA) -> list[object]:  # type: ignore[no-untyped-def]
        prepared = await self.handler.prepare(AskCommand(person_id=person, question=question))
        return [event async for event in self.handler.answer(prepared)]


async def test_answer_streams_and_is_saved() -> None:
    setup = Setup()

    events = await setup.ask()

    assert events == [
        ToolUsed("Revisando tu progreso…"),
        TextChunk("Hola"),
        TextChunk(", Ana."),
        Finished(fallback=False, questions_left=MAX_QUESTIONS - 1),
    ]
    saved = setup.conversations.items[ANA]
    assert [line.text for line in saved.lines] == ["¿Cómo voy?", "Hola, Ana."]
    assert saved.model_state[-1]["role"] == "assistant"
    assert not setup.lock.held_by


async def test_next_question_resends_the_saved_history() -> None:
    setup = Setup()
    await setup.ask("Hola")

    await setup.ask("¿Y ahora?")

    assert setup.model.calls[1]["history"] == list(setup.conversations.items[ANA].model_state[:2])


async def test_each_role_gets_its_tools() -> None:
    setup = Setup()

    await setup.ask(person=ANA)
    await setup.ask(person=MARISOL)

    assert "my_progress" in setup.model.calls[0]["tools"]  # type: ignore[operator]
    assert "class_dashboard" in setup.model.calls[1]["tools"]  # type: ignore[operator]
    assert "my_progress" not in setup.model.calls[1]["tools"]  # type: ignore[operator]


async def test_without_ai_the_person_still_gets_help_and_nothing_is_saved() -> None:
    setup = Setup(ScriptedModel(fail_after=0))

    events = await setup.ask()

    assert TextChunk(UNAVAILABLE) in events
    assert events[-1] == Finished(fallback=True, questions_left=MAX_QUESTIONS)
    assert ANA not in setup.conversations.items
    assert not setup.lock.held_by


async def test_an_answer_cut_halfway_says_so() -> None:
    setup = Setup(ScriptedModel(fail_after=1))

    events = await setup.ask()

    assert events[1:3] == [TextChunk("Hola"), TextChunk(INTERRUPTED)]


async def test_one_answer_at_a_time() -> None:
    setup = Setup()
    await setup.handler.prepare(AskCommand(person_id=ANA, question="Primera"))

    with pytest.raises(StillAnswering):
        await setup.handler.prepare(AskCommand(person_id=ANA, question="Segunda"))


async def test_over_the_budget_the_lock_is_freed() -> None:
    setup = Setup(budget=False)

    with pytest.raises(TooManyQuestions):
        await setup.ask()
    assert not setup.lock.held_by


async def test_full_conversation_must_restart() -> None:
    setup = Setup()
    full = Conversation()
    for n in range(MAX_QUESTIONS):
        full = full.answered(f"p{n}", "r", ())
    setup.conversations.items[ANA] = full

    with pytest.raises(ConversationFull):
        await setup.ask()


async def test_unknown_person_is_rejected() -> None:
    with pytest.raises(Unauthenticated):
        await Setup().ask(person=uuid4())


async def test_conversation_can_be_read_and_restarted() -> None:
    setup = Setup()
    await setup.ask()
    handler = ConversationHandler(setup.conversations, setup.lock)

    view = await handler.read(ANA)
    assert [line.speaker for line in view.lines] == [Speaker.PERSON, Speaker.ASSISTANT]
    assert view.answering is False

    await handler.restart(ANA)
    assert (await handler.read(ANA)).lines == ()


async def test_cannot_restart_while_answering() -> None:
    setup = Setup()
    await setup.handler.prepare(AskCommand(person_id=ANA, question="Hola"))

    with pytest.raises(StillAnswering):
        await ConversationHandler(setup.conversations, setup.lock).restart(ANA)
