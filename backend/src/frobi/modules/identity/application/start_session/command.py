from dataclasses import dataclass

from frobi.modules.identity.application.ports import ActiveMembership
from frobi.modules.identity.domain import Person, Role


@dataclass(frozen=True, slots=True)
class StartSessionCommand:
    alias: str
    career: str
    role: Role
    class_code: str | None = None


@dataclass(frozen=True, slots=True)
class StartSessionResult:
    token: str
    person: Person
    membership: ActiveMembership | None
