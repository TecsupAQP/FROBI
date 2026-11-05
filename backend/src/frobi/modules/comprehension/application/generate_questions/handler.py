"""Questions about an adaptation's material: 3 to check comprehension (RF13), or one similar
question to answer without help (RF24). Each new request asks for questions not seen yet."""

from uuid import UUID

from frobi.modules.comprehension.application.ports import (
    QuestionGenerator,
    QuestionRepository,
    QuizContextReader,
)
from frobi.modules.comprehension.domain import (
    AdaptationNotAvailable,
    NotEnoughMaterial,
    Question,
    QuestionKind,
)
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock

HOW_MANY = {QuestionKind.COMPREHENSION: 3, QuestionKind.TRANSFER: 1}


class GenerateQuestionsHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        questions: QuestionRepository,
        contexts: QuizContextReader,
        generator: QuestionGenerator,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._questions = questions
        self._contexts = contexts
        self._generator = generator
        self._clock = clock

    async def handle(
        self, person_id: UUID, adaptation_id: UUID, kind: QuestionKind
    ) -> list[Question]:
        context = await self._contexts.get(person_id, adaptation_id)
        if context is None:
            raise AdaptationNotAvailable()
        already = await self._questions.count(adaptation_id, kind)
        drafts = await self._generator.generate(
            requested_by=person_id, context=context, kind=kind, n=HOW_MANY[kind], skip=already
        )
        if not drafts:
            raise NotEnoughMaterial()
        now = self._clock.now()
        questions = [
            Question.from_draft(
                draft,
                person_id=person_id,
                adaptation_id=adaptation_id,
                kind=kind,
                source_format=context.format,
                now=now,
            )
            for draft in drafts
        ]
        async with self._uow:
            await self._questions.add_all(questions)
            await self._uow.commit()
        return questions
