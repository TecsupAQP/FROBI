"""Tables owned by tutoring."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class HelpAttemptModel(Base):
    __tablename__ = "help_attempts"
    __table_args__ = (
        CheckConstraint(
            "max_step IN ('none', 'hint_1', 'hint_2', 'step_by_step', 'final')", name="max_step"
        ),
        # The final answer is only reachable after an own attempt, also at the database level.
        CheckConstraint("max_step <> 'final' OR own_answer IS NOT NULL", name="final_after_own"),
        Index("ix_help_attempts_class_id_person_id", "class_id", "person_id"),
        Index("ix_help_attempts_person_id", "person_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    person_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    class_id: Mapped[UUID | None] = mapped_column(Uuid)
    adaptation_id: Mapped[UUID] = mapped_column(ForeignKey("adaptations.id", ondelete="CASCADE"))
    task_ref: Mapped[str] = mapped_column(String(120))
    max_step: Mapped[str] = mapped_column(String(16))
    own_answer: Mapped[str | None] = mapped_column(Text)
    self_check: Mapped[list[Any]] = mapped_column(JSONB)
    solved_without_ai: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
