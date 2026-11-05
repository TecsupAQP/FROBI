"""ClassMembership (identity's port) over the public API of classrooms."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import classrooms
from frobi.modules.identity.application.ports import ActiveMembership, ClassRef


class ClassroomsMembershipAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._join = classrooms.join_class_handler(session)
        self._active = classrooms.active_class_handler(session)
        self._found: dict[UUID, classrooms.Classroom] = {}

    async def find_by_code(self, code: str) -> ClassRef | None:
        classroom = await self._join.find_by_code(code)
        if classroom is None:
            return None
        self._found[classroom.id] = classroom
        return ClassRef(id=classroom.id, name=classroom.name)

    async def join(self, person_id: UUID, alias: str, class_ref: ClassRef) -> ActiveMembership:
        classroom = self._found.get(class_ref.id)
        if classroom is None:
            raise LookupError("join() needs a class found with find_by_code() first")
        joined = await self._join.join(person_id, alias, classroom)
        return ActiveMembership(class_id=joined.class_id, class_name=joined.class_name)

    async def active_for(self, person_id: UUID) -> ActiveMembership | None:
        active = await self._active.handle(person_id)
        if active is None:
            return None
        return ActiveMembership(class_id=active.class_id, class_name=active.class_name)


class ClassroomsDemoDirectory:
    def __init__(self, session: AsyncSession) -> None:
        self._demo = classrooms.demo_people_handler(session)

    async def person_for(self, who: str) -> UUID | None:
        return await self._demo.person_for(who)
