"""A person who uses FROBI. No email, no password, no personal data beyond an alias (RNF08)."""

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .errors import InvalidAlias, InvalidCareer

ALIAS_MAX = 40
CAREER_MAX = 80


class Role(StrEnum):
    LEARNER = "learner"
    TEACHER = "teacher"


class ConfiguredBy(StrEnum):
    SELF = "self"
    COMPANION = "companion"


def _clean(raw: str) -> str:
    return " ".join(raw.split())


def normalize_alias(raw: str) -> str:
    alias = _clean(raw)
    if not 1 <= len(alias) <= ALIAS_MAX:
        raise InvalidAlias()
    return alias


def normalize_career(raw: str) -> str:
    career = _clean(raw)
    if not 1 <= len(career) <= CAREER_MAX:
        raise InvalidCareer()
    return career


@dataclass(frozen=True, slots=True)
class Person:
    id: UUID
    alias: str
    career: str
    role: Role
    configured_by: ConfiguredBy
    created_at: datetime

    @classmethod
    def register(cls, *, alias: str, career: str, role: Role, now: datetime) -> "Person":
        """New person entering FROBI. The onboarding wizard may later say a companion set it up."""
        return cls(
            id=uuid4(),
            alias=normalize_alias(alias),
            career=normalize_career(career),
            role=role,
            configured_by=ConfiguredBy.SELF,
            created_at=now,
        )

    def configured(self, by: ConfiguredBy) -> "Person":
        """The wizard says who set FROBI up: the person or a companion (RF36)."""
        return replace(self, configured_by=by)
