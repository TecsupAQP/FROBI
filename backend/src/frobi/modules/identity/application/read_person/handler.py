"""Read a person (alias, role). Public API for other modules (classrooms, progress)."""

from uuid import UUID

from frobi.modules.identity.application.ports import PersonRepository
from frobi.modules.identity.domain import Person


class ReadPersonHandler:
    def __init__(self, persons: PersonRepository) -> None:
        self._persons = persons

    async def find(self, person_id: UUID) -> Person | None:
        return await self._persons.get(person_id)
