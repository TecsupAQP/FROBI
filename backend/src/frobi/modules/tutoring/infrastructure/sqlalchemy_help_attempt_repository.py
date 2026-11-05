from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.tutoring.domain import HelpAttempt, ReachedStep

from .models import HelpAttemptModel


def _to_domain(row: HelpAttemptModel) -> HelpAttempt:
    return HelpAttempt(
        id=row.id,
        person_id=row.person_id,
        class_id=row.class_id,
        adaptation_id=row.adaptation_id,
        task_ref=row.task_ref,
        max_step=ReachedStep(row.max_step),
        own_answer=row.own_answer,
        self_check=tuple(str(item) for item in row.self_check),
        solved_without_ai=row.solved_without_ai,
        created_at=row.created_at,
    )


class SqlAlchemyHelpAttemptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, attempt: HelpAttempt) -> None:
        self._session.add(
            HelpAttemptModel(
                id=attempt.id,
                person_id=attempt.person_id,
                class_id=attempt.class_id,
                adaptation_id=attempt.adaptation_id,
                task_ref=attempt.task_ref,
                max_step=attempt.max_step.value,
                own_answer=attempt.own_answer,
                self_check=list(attempt.self_check),
                solved_without_ai=attempt.solved_without_ai,
                created_at=attempt.created_at,
            )
        )

    async def get(self, attempt_id: UUID, *, for_update: bool = False) -> HelpAttempt | None:
        query = select(HelpAttemptModel).where(HelpAttemptModel.id == attempt_id)
        if for_update:
            query = query.with_for_update().execution_options(populate_existing=True)
        row = (await self._session.execute(query)).scalar_one_or_none()
        return None if row is None else _to_domain(row)

    async def save(self, attempt: HelpAttempt) -> None:
        row = await self._session.get(HelpAttemptModel, attempt.id)
        if row is None:
            await self.add(attempt)
            return
        row.max_step = attempt.max_step.value
        row.own_answer = attempt.own_answer
        row.self_check = list(attempt.self_check)
        row.solved_without_ai = attempt.solved_without_ai
