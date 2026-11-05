from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.identity.domain import ConfiguredBy, Person, Role

from .models import PersonModel


class SqlAlchemyPersonRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, person: Person) -> None:
        self._session.add(
            PersonModel(
                id=person.id,
                alias=person.alias,
                career=person.career,
                role=person.role.value,
                configured_by=person.configured_by.value,
                created_at=person.created_at,
            )
        )

    async def save(self, person: Person) -> None:
        row = await self._session.get(PersonModel, person.id)
        if row is None:
            await self.add(person)
            return
        row.alias = person.alias
        row.career = person.career
        row.role = person.role.value
        row.configured_by = person.configured_by.value

    async def get(self, person_id: UUID) -> Person | None:
        row = await self._session.get(PersonModel, person_id)
        if row is None:
            return None
        return Person(
            id=row.id,
            alias=row.alias,
            career=row.career,
            role=Role(row.role),
            configured_by=ConfiguredBy(row.configured_by),
            created_at=row.created_at,
        )
