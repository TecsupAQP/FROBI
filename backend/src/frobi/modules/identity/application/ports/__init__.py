"""Outbound ports of identity. Adapters live in identity/infrastructure."""

from dataclasses import dataclass
from typing import Literal, Protocol
from uuid import UUID

from frobi.modules.identity.domain import Person


class PersonRepository(Protocol):
    async def add(self, person: Person) -> None: ...

    async def get(self, person_id: UUID) -> Person | None: ...

    async def save(self, person: Person) -> None: ...


class SessionStore(Protocol):
    """Opaque tokens that expire (30 days). Implemented on Redis."""

    async def create(self, person_id: UUID) -> str: ...

    async def resolve(self, token: str) -> UUID | None: ...

    async def revoke(self, token: str) -> None: ...


@dataclass(frozen=True, slots=True)
class ClassRef:
    id: UUID
    name: str


@dataclass(frozen=True, slots=True)
class ActiveMembership:
    class_id: UUID
    class_name: str


class ClassMembership(Protocol):
    """What identity needs from classrooms: check a code when entering, and the active class."""

    async def find_by_code(self, code: str) -> ClassRef | None: ...

    async def join(self, person_id: UUID, alias: str, class_ref: ClassRef) -> ActiveMembership:
        """``alias`` lets a pending invitation for that alias be taken (RF46)."""
        ...

    async def active_for(self, person_id: UUID) -> ActiveMembership | None: ...


@dataclass(frozen=True, slots=True)
class OnboardingStatus:
    done: bool
    intro_status: Literal["seen", "skipped", "pending"]


class OnboardingStatusReader(Protocol):
    async def for_person(self, person_id: UUID) -> OnboardingStatus: ...


class DemoDirectory(Protocol):
    """Over the public API of classrooms: the person behind a demo name, or None."""

    async def person_for(self, who: str) -> UUID | None: ...


__all__ = [
    "ActiveMembership",
    "ClassMembership",
    "ClassRef",
    "DemoDirectory",
    "OnboardingStatus",
    "OnboardingStatusReader",
    "PersonRepository",
    "SessionStore",
]
