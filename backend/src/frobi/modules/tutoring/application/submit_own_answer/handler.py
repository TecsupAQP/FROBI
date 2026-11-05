"""«Inténtalo sin IA»: compare the own answer with the guide by text search (RF41, RF42)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.tutoring.application.ports import HelpAttemptRepository, TutoringContextReader
from frobi.modules.tutoring.domain import (
    AdaptationNotAvailable,
    AttemptNotFound,
    HelpAttempt,
    Passage,
    find_passages,
)
from frobi.shared.application import UnitOfWork


@dataclass(frozen=True, slots=True)
class SubmitOwnAnswerCommand:
    person_id: UUID
    attempt_id: UUID
    answer: str
    self_check: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class OwnAnswerResult:
    attempt: HelpAttempt
    matching_passages: list[Passage]


class SubmitOwnAnswerHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        attempts: HelpAttemptRepository,
        contexts: TutoringContextReader,
    ) -> None:
        self._uow = uow
        self._attempts = attempts
        self._contexts = contexts

    async def handle(self, command: SubmitOwnAnswerCommand) -> OwnAnswerResult:
        async with self._uow:
            attempt = await self._attempts.get(command.attempt_id, for_update=True)
            if attempt is None or not attempt.visible_to(command.person_id):
                raise AttemptNotFound()
            context = await self._contexts.get(command.person_id, attempt.adaptation_id)
            if context is None:
                raise AdaptationNotAvailable()
            passages = find_passages(command.answer, context.material_title, context.material_text)
            updated = attempt.submit_own_answer(
                command.answer, command.self_check, matches_guide=bool(passages)
            )
            await self._attempts.save(updated)
            await self._uow.commit()
        return OwnAnswerResult(attempt=updated, matching_passages=passages)
