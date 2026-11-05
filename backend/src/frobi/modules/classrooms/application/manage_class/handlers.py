"""The teacher side: create a class with its code, invite by alias, see who joined (RF44, RF46)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.classrooms.application.ports import (
    ClassRepository,
    CodeGenerator,
    MembershipRepository,
    PersonDirectory,
)
from frobi.modules.classrooms.domain import (
    ClassNotFound,
    Classroom,
    Membership,
    MembershipStatus,
    TeachersOnly,
    same_alias,
)
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock

MAX_CODE_TRIES = 10


@dataclass(frozen=True, slots=True)
class CreateClassCommand:
    teacher_id: UUID
    name: str
    subject: str
    tasks: list[str]


class CreateClassHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        classes: ClassRepository,
        people: PersonDirectory,
        codes: CodeGenerator,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._classes = classes
        self._people = people
        self._codes = codes
        self._clock = clock

    async def handle(self, command: CreateClassCommand) -> Classroom:
        if not await self._people.is_teacher(command.teacher_id):
            raise TeachersOnly()
        code = self._codes()
        for _ in range(MAX_CODE_TRIES):
            if not await self._classes.code_taken(code):
                break
            code = self._codes()
        classroom = Classroom.create(
            teacher_id=command.teacher_id,
            name=command.name,
            subject=command.subject,
            tasks=command.tasks,
            invite_code=code,
            now=self._clock.now(),
        )
        async with self._uow:
            await self._classes.add(classroom)
            await self._uow.commit()
        return classroom


async def own_class(classes: ClassRepository, teacher_id: UUID, class_id: UUID) -> Classroom:
    """The class if this person teaches it. Anyone else gets «not found»."""
    classroom = await classes.get(class_id)
    if classroom is None or not classroom.taught_by(teacher_id):
        raise ClassNotFound()
    return classroom


class ListMyClassesHandler:
    """The classes a teacher teaches, so the front never has to remember them (RF44)."""

    def __init__(self, classes: ClassRepository, people: PersonDirectory) -> None:
        self._classes = classes
        self._people = people

    async def handle(self, teacher_id: UUID) -> list[Classroom]:
        if not await self._people.is_teacher(teacher_id):
            raise TeachersOnly()
        return await self._classes.list_for_teacher(teacher_id)


class GetClassHandler:
    """The teacher of the class and its joined members can see it."""

    def __init__(self, classes: ClassRepository, memberships: MembershipRepository) -> None:
        self._classes = classes
        self._memberships = memberships

    async def handle(self, person_id: UUID, class_id: UUID) -> Classroom:
        classroom = await self._classes.get(class_id)
        if classroom is None:
            raise ClassNotFound()
        if classroom.taught_by(person_id):
            return classroom
        active = await self._memberships.active_for(person_id)
        if active is None or active.class_id != class_id:
            raise ClassNotFound()
        return classroom


class InviteStudentsHandler:
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

    async def handle(
        self, teacher_id: UUID, class_id: UUID, aliases: list[str]
    ) -> list[Membership]:
        await own_class(self._classes, teacher_id, class_id)
        existing = await self._memberships.for_class(class_id)
        now = self._clock.now()
        invited: list[Membership] = []
        async with self._uow:
            for alias in aliases:
                if not alias.strip():
                    continue
                known = next((m for m in [*existing, *invited] if same_alias(m.alias, alias)), None)
                if known is not None and known.status is not MembershipStatus.LEFT:
                    invited.append(known)
                    continue
                membership = Membership.invite(class_id=class_id, alias=alias, now=now)
                await self._memberships.add(membership)
                invited.append(membership)
            await self._uow.commit()
        return list(dict.fromkeys(invited))


@dataclass(frozen=True, slots=True)
class MembersView:
    invite_code: str
    members: list[Membership]


class ListMembersHandler:
    def __init__(self, classes: ClassRepository, memberships: MembershipRepository) -> None:
        self._classes = classes
        self._memberships = memberships

    async def handle(self, teacher_id: UUID, class_id: UUID) -> MembersView:
        classroom = await own_class(self._classes, teacher_id, class_id)
        return MembersView(classroom.invite_code, await self._memberships.for_class(class_id))
