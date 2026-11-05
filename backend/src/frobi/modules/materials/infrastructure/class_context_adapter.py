"""The shared ``ClassContext`` over the public API of classrooms, inside the request's session."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import classrooms


class ClassroomsActiveClass:
    def __init__(self, session: AsyncSession) -> None:
        self._active = classrooms.active_class_handler(session)

    async def active_class(self, person_id: UUID) -> UUID | None:
        active = await self._active.handle(person_id)
        return None if active is None else active.class_id
