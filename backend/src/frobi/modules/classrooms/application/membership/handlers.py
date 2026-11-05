"""The student side: join with a code, the active class, leave the class (RF33, RF49).

A person has at most one active (``joined``) class. Joining another one leaves the previous one.
"""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.classrooms.application.ports import (
    ClassRepository,
    MembershipRepository,
    PersonDirectory,
)
from frobi.modules.classrooms.domain import (
    Classroom,
    InvalidClassCode,
    Membership,
    MembershipStatus,
    NotInAClass,
    normalize_code,
    same_alias,
)
from frobi.shared.application import Unauthenticated, UnitOfWork
from frobi.shared.domain import Clock


@dataclass(frozen=True, slots=True)
class ActiveClass:
    class_id: UUID
    class_name: str


class JoinClassHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        classes: ClassRepository,
        memberships: MembershipRepository,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._classes = classes
        self._memberships = memberships
        self._clock = clock

    async def find_by_code(self, code: str) -> Classroom | None:
        return await self._classes.get_by_code(normalize_code(code))

    async def handle(self, person_id: UUID, alias: str, code: str) -> ActiveClass:
        classroom = await self.find_by_code(code)
        if classroom is None:
            raise InvalidClassCode()
        return await self.join(person_id, alias, classroom)

    async def join(self, person_id: UUID, alias: str, classroom: Classroom) -> ActiveClass:
        now = self._clock.now()
        async with self._uow:
            current = await self._memberships.active_for(person_id)
            if current is not None and current.class_id == classroom.id:
                return ActiveClass(classroom.id, classroom.name)
            if current is not None:
                await self._memberships.save(current.leave(now))
            members = await self._memberships.for_class(classroom.id)
            invitation = next(
                (
                    m
                    for m in members
                    if m.status is MembershipStatus.INVITED
                    and m.person_id is None
                    and same_alias(m.alias, alias)
                ),
                None,
            )
            if invitation is not None:
                await self._memberships.save(invitation.accept(person_id, now))
            else:
                await self._memberships.add(
                    Membership.join_new(
                        class_id=classroom.id, person_id=person_id, alias=alias, now=now
                    )
                )
            await self._uow.commit()
        return ActiveClass(classroom.id, classroom.name)


class JoinWithCodeHandler:
    """POST /classes/join: the logged-in person joins with a code, under their own alias."""

    def __init__(self, join: JoinClassHandler, people: PersonDirectory) -> None:
        self._join = join
        self._people = people

    async def handle(self, person_id: UUID, code: str) -> ActiveClass:
        alias = await self._people.alias_of(person_id)
        if alias is None:
            raise Unauthenticated()
        return await self._join.handle(person_id, alias, code)


class ActiveClassHandler:
    def __init__(self, classes: ClassRepository, memberships: MembershipRepository) -> None:
        self._classes = classes
        self._memberships = memberships

    async def handle(self, person_id: UUID) -> ActiveClass | None:
        membership = await self._memberships.active_for(person_id)
        if membership is None:
            return None
        classroom = await self._classes.get(membership.class_id)
        return None if classroom is None else ActiveClass(classroom.id, classroom.name)


class LeaveClassHandler:
    def __init__(self, uow: UnitOfWork, memberships: MembershipRepository, clock: Clock) -> None:
        self._uow = uow
        self._memberships = memberships
        self._clock = clock

    async def handle(self, person_id: UUID) -> None:
        async with self._uow:
            current = await self._memberships.active_for(person_id)
            if current is None:
                raise NotInAClass()
            await self._memberships.save(current.leave(self._clock.now()))
            await self._uow.commit()
