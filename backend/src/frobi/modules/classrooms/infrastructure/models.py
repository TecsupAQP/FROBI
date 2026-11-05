"""Tables owned by classrooms."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class ClassModel(Base):
    __tablename__ = "classes"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(80))
    subject: Mapped[str] = mapped_column(String(80))
    tasks: Mapped[list[Any]] = mapped_column(JSONB)
    invite_code: Mapped[str] = mapped_column(String(16), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MembershipModel(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        CheckConstraint("status IN ('invited', 'joined', 'left')", name="status"),
        CheckConstraint("status = 'invited' OR person_id IS NOT NULL", name="person_after_invite"),
        Index("ix_memberships_class_id_status", "class_id", "status"),
        # A person has at most one active class (PLAN_BACKEND §4).
        Index(
            "uq_memberships_one_joined_per_person",
            "person_id",
            unique=True,
            postgresql_where=text("status = 'joined'"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    class_id: Mapped[UUID] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"))
    person_id: Mapped[UUID | None] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
