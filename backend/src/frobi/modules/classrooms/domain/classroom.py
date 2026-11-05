"""A teacher's class (RF44) and the people in it (RF33, RF46, RF49)."""

import secrets
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .errors import InvalidClassData

# No 0/O, 1/I/L: codes are read aloud and typed by hand.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 6
MAX_TASKS = 20

# Seeded by migration 0010 («Sensores 2026-II», code SENSOR1). Its panel is always demo data.
DEMO_CLASS_ID = UUID("00000000-0000-4000-8000-0000000000c1")
DEMO_TEACHER_ID = UUID("00000000-0000-4000-8000-00000000d0c0")


def new_invite_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


def normalize_code(raw: str) -> str:
    return "".join(raw.split()).upper()


def normalize_alias(raw: str) -> str:
    return " ".join(raw.split())


def same_alias(a: str, b: str) -> bool:
    return normalize_alias(a).casefold() == normalize_alias(b).casefold()


def _clean(value: str, limit: int) -> str:
    cleaned = " ".join(value.split())
    if not 1 <= len(cleaned) <= limit:
        raise InvalidClassData()
    return cleaned


@dataclass(frozen=True, slots=True)
class Classroom:
    id: UUID
    teacher_id: UUID
    name: str
    subject: str
    tasks: tuple[str, ...]
    invite_code: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        teacher_id: UUID,
        name: str,
        subject: str,
        tasks: list[str],
        invite_code: str,
        now: datetime,
    ) -> "Classroom":
        cleaned = tuple(dict.fromkeys(t for t in (" ".join(t.split()) for t in tasks) if t))
        if len(cleaned) > MAX_TASKS or any(len(t) > 200 for t in cleaned):
            raise InvalidClassData()
        return cls(
            id=uuid4(),
            teacher_id=teacher_id,
            name=_clean(name, 80),
            subject=_clean(subject, 80),
            tasks=cleaned,
            invite_code=invite_code,
            created_at=now,
        )

    def taught_by(self, person_id: UUID) -> bool:
        return self.teacher_id == person_id


class MembershipStatus(StrEnum):
    INVITED = "invited"
    JOINED = "joined"
    LEFT = "left"


STATUS_LABELS = {
    MembershipStatus.INVITED: "Invitación pendiente",
    MembershipStatus.JOINED: "Se unió",
    MembershipStatus.LEFT: "Salió de la clase",
}


@dataclass(frozen=True, slots=True)
class Membership:
    id: UUID
    class_id: UUID
    person_id: UUID | None
    alias: str
    status: MembershipStatus
    created_at: datetime
    joined_at: datetime | None = None
    left_at: datetime | None = field(default=None)

    @classmethod
    def invite(cls, *, class_id: UUID, alias: str, now: datetime) -> "Membership":
        return cls(
            id=uuid4(),
            class_id=class_id,
            person_id=None,
            alias=_clean(alias, 40),
            status=MembershipStatus.INVITED,
            created_at=now,
        )

    @classmethod
    def join_new(
        cls, *, class_id: UUID, person_id: UUID, alias: str, now: datetime
    ) -> "Membership":
        return cls(
            id=uuid4(),
            class_id=class_id,
            person_id=person_id,
            alias=_clean(alias, 40),
            status=MembershipStatus.JOINED,
            created_at=now,
            joined_at=now,
        )

    def accept(self, person_id: UUID, now: datetime) -> "Membership":
        """An invitation (by alias) is taken by the person who enters with that alias."""
        return replace(
            self, person_id=person_id, status=MembershipStatus.JOINED, joined_at=now, left_at=None
        )

    def leave(self, now: datetime) -> "Membership":
        """Leaving keeps the history; activity afterwards has no class (RF49)."""
        return replace(self, status=MembershipStatus.LEFT, left_at=now)

    @property
    def status_label(self) -> str:
        return STATUS_LABELS[self.status]
