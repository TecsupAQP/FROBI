"""Enter FROBI with alias, career and role; optionally join a class by code (RF28, RF32-33)."""

from frobi.modules.identity.application.ports import (
    ClassMembership,
    PersonRepository,
    SessionStore,
)
from frobi.modules.identity.domain import InvalidClassCode, Person
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock

from .command import StartSessionCommand, StartSessionResult


class StartSessionHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        persons: PersonRepository,
        sessions: SessionStore,
        memberships: ClassMembership,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._persons = persons
        self._sessions = sessions
        self._memberships = memberships
        self._clock = clock

    async def handle(self, command: StartSessionCommand) -> StartSessionResult:
        person = Person.register(
            alias=command.alias, career=command.career, role=command.role, now=self._clock.now()
        )

        # A wrong code rejects the whole entry so nothing half-created is left behind;
        # the front then offers to enter without a class.
        class_ref = None
        code = (command.class_code or "").strip()
        if code:
            class_ref = await self._memberships.find_by_code(code)
            if class_ref is None:
                raise InvalidClassCode()

        async with self._uow:
            await self._persons.add(person)
            await self._uow.commit()

        membership = None
        if class_ref is not None:
            membership = await self._memberships.join(person.id, class_ref)
        token = await self._sessions.create(person.id)
        return StartSessionResult(token=token, person=person, membership=membership)
