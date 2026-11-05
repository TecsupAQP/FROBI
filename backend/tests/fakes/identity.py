"""In-memory doubles of identity's ports, shared by unit and e2e tests."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import TracebackType
from typing import Self
from uuid import UUID

from frobi.modules.identity.application import EndSessionHandler, GetMeHandler, StartSessionHandler
from frobi.modules.identity.application.ports import ActiveMembership, ClassRef, OnboardingStatus
from frobi.modules.identity.domain import Person

EXAMPLE_CLASS = ClassRef(id=UUID("00000000-0000-4000-8000-0000000000c1"), name="Sensores 2026-II")


class FixedClock:
    def __init__(self, now: datetime = datetime(2026, 11, 5, 9, 0, tzinfo=UTC)) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        self.rollbacks += 1


class InMemoryPersons:
    def __init__(self) -> None:
        self.items: dict[UUID, Person] = {}

    async def add(self, person: Person) -> None:
        self.items[person.id] = person

    async def get(self, person_id: UUID) -> Person | None:
        return self.items.get(person_id)


class InMemorySessions:
    def __init__(self) -> None:
        self.tokens: dict[str, UUID] = {}

    async def create(self, person_id: UUID) -> str:
        token = f"token-{len(self.tokens) + 1}"
        self.tokens[token] = person_id
        return token

    async def resolve(self, token: str) -> UUID | None:
        return self.tokens.get(token)

    async def revoke(self, token: str) -> None:
        self.tokens.pop(token, None)


class FakeClassMembership:
    def __init__(self, code: str = "SENSOR1") -> None:
        self._code = code
        self.joined: dict[UUID, ClassRef] = {}

    async def find_by_code(self, code: str) -> ClassRef | None:
        return EXAMPLE_CLASS if code.upper() == self._code else None

    async def join(self, person_id: UUID, class_ref: ClassRef) -> ActiveMembership:
        self.joined[person_id] = class_ref
        return ActiveMembership(class_id=class_ref.id, class_name=class_ref.name)

    async def active_for(self, person_id: UUID) -> ActiveMembership | None:
        ref = self.joined.get(person_id)
        return None if ref is None else ActiveMembership(class_id=ref.id, class_name=ref.name)


class FakeOnboarding:
    async def for_person(self, person_id: UUID) -> OnboardingStatus:
        return OnboardingStatus(done=False, intro_status="pending")


@dataclass
class IdentityFakes:
    uow: FakeUnitOfWork = field(default_factory=FakeUnitOfWork)
    persons: InMemoryPersons = field(default_factory=InMemoryPersons)
    sessions: InMemorySessions = field(default_factory=InMemorySessions)
    memberships: FakeClassMembership = field(default_factory=FakeClassMembership)
    onboarding: FakeOnboarding = field(default_factory=FakeOnboarding)
    clock: FixedClock = field(default_factory=FixedClock)

    def start_session(self) -> StartSessionHandler:
        return StartSessionHandler(
            self.uow, self.persons, self.sessions, self.memberships, self.clock
        )

    def end_session(self) -> EndSessionHandler:
        return EndSessionHandler(self.sessions)

    def get_me(self) -> GetMeHandler:
        return GetMeHandler(self.persons, self.memberships, self.onboarding)
