"""Current step and help level of an attempt («Nivel 2, con pistas», RF43)."""

from uuid import UUID

from frobi.modules.tutoring.application.ports import HelpAttemptRepository
from frobi.modules.tutoring.domain import AttemptNotFound, HelpAttempt


class GetAttemptHandler:
    def __init__(self, attempts: HelpAttemptRepository) -> None:
        self._attempts = attempts

    async def handle(self, person_id: UUID, attempt_id: UUID) -> HelpAttempt:
        attempt = await self._attempts.get(attempt_id)
        if attempt is None or not attempt.visible_to(person_id):
            raise AttemptNotFound()
        return attempt
