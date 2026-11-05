from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.comprehension.domain import Answer, Option, Question, QuestionKind

from .models import AnswerModel, QuestionModel


class SqlAlchemyQuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_all(self, questions: list[Question]) -> None:
        self._session.add_all(
            QuestionModel(
                id=q.id,
                person_id=q.person_id,
                adaptation_id=q.adaptation_id,
                kind=q.kind.value,
                statement=q.statement,
                options=[[o.id, o.text] for o in q.options],
                correct_option=q.correct_option,
                feedback={"correct": q.feedback_correct, "wrong": q.feedback_wrong},
                source_format=q.source_format,
                created_at=q.created_at,
            )
            for q in questions
        )

    async def get(self, question_id: UUID) -> Question | None:
        row = await self._session.get(QuestionModel, question_id)
        if row is None:
            return None
        return Question(
            id=row.id,
            person_id=row.person_id,
            adaptation_id=row.adaptation_id,
            kind=QuestionKind(row.kind),
            statement=row.statement,
            options=tuple(Option(str(i), str(t)) for i, t in row.options),
            correct_option=row.correct_option,
            feedback_correct=row.feedback["correct"],
            feedback_wrong=row.feedback["wrong"],
            source_format=row.source_format,
            created_at=row.created_at,
        )

    async def count(self, adaptation_id: UUID, kind: QuestionKind) -> int:
        query = select(func.count()).where(
            QuestionModel.adaptation_id == adaptation_id, QuestionModel.kind == kind.value
        )
        return int(await self._session.scalar(query) or 0)


class SqlAlchemyAnswerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, answer: Answer) -> None:
        self._session.add(
            AnswerModel(
                id=answer.id,
                question_id=answer.question_id,
                person_id=answer.person_id,
                class_id=answer.class_id,
                chosen_option=answer.chosen_option,
                is_correct=answer.verdict.is_correct,
                used_help=answer.used_help,
                created_at=answer.created_at,
            )
        )
