"""Tables owned by comprehension."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class QuestionModel(Base):
    __tablename__ = "questions"
    __table_args__ = (
        CheckConstraint("kind IN ('comprehension', 'transfer')", name="kind"),
        Index("ix_questions_adaptation_id_kind", "adaptation_id", "kind"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    person_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    adaptation_id: Mapped[UUID] = mapped_column(ForeignKey("adaptations.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(16))
    statement: Mapped[str] = mapped_column(Text)
    options: Mapped[list[Any]] = mapped_column(JSONB)
    correct_option: Mapped[str] = mapped_column(String(4))
    feedback: Mapped[dict[str, Any]] = mapped_column(JSONB)
    source_format: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AnswerModel(Base):
    __tablename__ = "answers"
    __table_args__ = (
        Index("ix_answers_class_id_person_id", "class_id", "person_id"),
        Index("ix_answers_person_id", "person_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    question_id: Mapped[UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    person_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    class_id: Mapped[UUID | None] = mapped_column(Uuid)
    chosen_option: Mapped[str] = mapped_column(String(4))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    used_help: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
