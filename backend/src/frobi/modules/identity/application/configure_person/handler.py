"""Read or record who configured FROBI for a person. Used by onboarding (public API)."""

from uuid import UUID

from frobi.modules.identity.application.ports import PersonRepository
from frobi.modules.identity.domain import ConfiguredBy
from frobi.shared.application import Unauthenticated, UnitOfWork


class ConfigurePersonHandler:
    def __init__(self, uow: UnitOfWork, persons: PersonRepository) -> None:
        self._uow = uow
        self._persons = persons

    async def configured_by(self, person_id: UUID) -> ConfiguredBy:
        person = await self._persons.get(person_id)
        if person is None:
            raise Unauthenticated()
        return person.configured_by

    async def set_configured_by(self, person_id: UUID, by: ConfiguredBy) -> None:
        async with self._uow:
            person = await self._persons.get(person_id)
            if person is None:
                raise Unauthenticated()
            await self._persons.save(person.configured(by))
            await self._uow.commit()
