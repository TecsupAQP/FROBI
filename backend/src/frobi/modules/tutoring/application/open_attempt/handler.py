"""Open an attempt on a task of an adaptation (RF39)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.tutoring.application.ports import HelpAttemptRepository, TutoringContextReader
from frobi.modules.tutoring.domain import AdaptationNotAvailable, HelpAttempt
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock


@dataclass(frozen=True, slots=True)
class OpenAttemptCommand:
    person_id: UUID
    class_id: UUID | None
    adaptation_id: UUID
    task_ref: str


class OpenAttemptHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        attempts: HelpAttemptRepository,
        contexts: TutoringContextReader,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._attempts = attempts
        self._contexts = contexts
        self._clock = clock

    async def handle(self, command: OpenAttemptCommand) -> HelpAttempt:
        if await self._contexts.get(command.person_id, command.adaptation_id) is None:
            raise AdaptationNotAvailable()
        attempt = HelpAttempt.open(
            person_id=command.person_id,
            class_id=command.class_id,
            adaptation_id=command.adaptation_id,
            task_ref=command.task_ref,
            now=self._clock.now(),
        )
        async with self._uow:
            await self._attempts.add(attempt)
            await self._uow.commit()
        return attempt
