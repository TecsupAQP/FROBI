"""Answer a question: right or wrong, feedback, and «Prueba con…» another format (RF13, RF14)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.comprehension.application.ports import AnswerRepository, QuestionRepository
from frobi.modules.comprehension.domain import Answer, QuestionNotFound
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock


@dataclass(frozen=True, slots=True)
class AnswerQuestionCommand:
    person_id: UUID
    class_id: UUID | None
    question_id: UUID
    option: str


class AnswerQuestionHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        questions: QuestionRepository,
        answers: AnswerRepository,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._questions = questions
        self._answers = answers
        self._clock = clock

    async def handle(self, command: AnswerQuestionCommand) -> Answer:
        question = await self._questions.get(command.question_id)
        if question is None or not question.visible_to(command.person_id):
            raise QuestionNotFound()
        answer = Answer.to(
            question,
            command.option.strip().lower(),
            class_id=command.class_id,
            now=self._clock.now(),
        )
        async with self._uow:
            await self._answers.add(answer)
            await self._uow.commit()
        return answer
