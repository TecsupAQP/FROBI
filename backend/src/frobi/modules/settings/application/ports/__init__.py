from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from frobi.modules.settings.domain import PersonSettings


class SettingsRepository(Protocol):
    async def get(self, person_id: UUID) -> PersonSettings | None: ...

    async def save(self, settings: PersonSettings) -> None: ...


@dataclass(frozen=True, slots=True)
class AccountView:
    id: UUID
    alias: str
    career: str
    role: str


class Account(Protocol):
    """Over the public API of identity."""

    async def rename(self, person_id: UUID, alias: str) -> AccountView: ...


@dataclass(frozen=True, slots=True)
class CurrentClass:
    class_id: UUID
    class_name: str


class ClassMembership(Protocol):
    """Over the public API of classrooms."""

    async def current(self, person_id: UUID) -> CurrentClass | None: ...

    async def leave(self, person_id: UUID) -> None: ...


__all__ = [
    "Account",
    "AccountView",
    "ClassMembership",
    "CurrentClass",
    "SettingsRepository",
]
