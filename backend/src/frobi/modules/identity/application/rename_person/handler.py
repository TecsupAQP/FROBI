"""Change the alias (RF52). Public API: the settings screen calls it."""

from dataclasses import replace
from uuid import UUID

from frobi.modules.identity.application.ports import PersonRepository
from frobi.modules.identity.domain import Person, normalize_alias
from frobi.shared.application import Unauthenticated, UnitOfWork


class RenamePersonHandler:
    def __init__(self, uow: UnitOfWork, persons: PersonRepository) -> None:
        self._uow = uow
        self._persons = persons

    async def handle(self, person_id: UUID, alias: str) -> Person:
        async with self._uow:
            person = await self._persons.get(person_id)
            if person is None:
                raise Unauthenticated()
            renamed = replace(person, alias=normalize_alias(alias))
            await self._persons.save(renamed)
            await self._uow.commit()
        return renamed
