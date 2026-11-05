"""settings' ports over the public APIs of identity and classrooms."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import classrooms, identity
from frobi.modules.settings.application.ports import AccountView, CurrentClass


class AccountAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._rename = identity.rename_person_handler(session)

    async def rename(self, person_id: UUID, alias: str) -> AccountView:
        person = await self._rename.handle(person_id, alias)
        return AccountView(person.id, person.alias, person.career, person.role.value)


class ClassMembershipAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._active = classrooms.active_class_handler(session)
        self._leave = classrooms.leave_class_handler(session)

    async def current(self, person_id: UUID) -> CurrentClass | None:
        active = await self._active.handle(person_id)
        return None if active is None else CurrentClass(active.class_id, active.class_name)

    async def leave(self, person_id: UUID) -> None:
        await self._leave.handle(person_id)
