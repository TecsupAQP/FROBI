"""Open the next step of the ladder and get its help (RF39, RF40)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.tutoring.application.ports import (
    HelpAttemptRepository,
    HintGenerator,
    TutoringContextReader,
)
from frobi.modules.tutoring.domain import (
    AdaptationNotAvailable,
    AttemptNotFound,
    HelpAttempt,
    HelpStep,
)
from frobi.shared.application import UnitOfWork


@dataclass(frozen=True, slots=True)
class RequestStepCommand:
    person_id: UUID
    attempt_id: UUID
    step: HelpStep


@dataclass(frozen=True, slots=True)
class StepResult:
    attempt: HelpAttempt
    step: HelpStep
    content: str
    fallback: bool


class RequestStepHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        attempts: HelpAttemptRepository,
        contexts: TutoringContextReader,
        hints: HintGenerator,
    ) -> None:
        self._uow = uow
        self._attempts = attempts
        self._contexts = contexts
        self._hints = hints

    async def handle(self, command: RequestStepCommand) -> StepResult:
        async with self._uow:
            attempt = await self._attempts.get(command.attempt_id, for_update=True)
            if attempt is None or not attempt.visible_to(command.person_id):
                raise AttemptNotFound()
            advanced = attempt.request(command.step)
            if advanced is not attempt:
                await self._attempts.save(advanced)
            await self._uow.commit()

        context = await self._contexts.get(command.person_id, advanced.adaptation_id)
        if context is None:
            raise AdaptationNotAvailable()
        hint = await self._hints.hint(
            requested_by=command.person_id,
            context=context,
            task_ref=advanced.task_ref,
            step=command.step,
        )
        return StepResult(
            attempt=advanced, step=command.step, content=hint.text, fallback=hint.fallback
        )
