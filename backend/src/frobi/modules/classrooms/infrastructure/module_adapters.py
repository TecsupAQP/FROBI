"""classrooms' ports over the public API of identity, and the shared ClassContext."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from frobi.modules import identity

from .sqlalchemy_repositories import SqlAlchemyMembershipRepository


class PersonDirectoryAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._people = identity.read_person_handler(session)

    async def is_teacher(self, person_id: UUID) -> bool:
        person = await self._people.find(person_id)
        return person is not None and person.role is identity.Role.TEACHER

    async def alias_of(self, person_id: UUID) -> str | None:
        person = await self._people.find(person_id)
        return None if person is None else person.alias


class ClassroomsClassContext:
    """Shared ``ClassContext``: the class of the person's ``joined`` membership (RNF16).

    Lives on ``app.state``, outside any request, so it opens its own short session.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def active_class(self, person_id: UUID) -> UUID | None:
        async with self._session_factory() as session:
            membership = await SqlAlchemyMembershipRepository(session).active_for(person_id)
        return None if membership is None else membership.class_id
