"""Tables owned by identity."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class PersonModel(Base):
    __tablename__ = "persons"
    __table_args__ = (
        CheckConstraint("role IN ('learner', 'teacher')", name="role"),
        CheckConstraint("configured_by IN ('self', 'companion')", name="configured_by"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(String(40))
    career: Mapped[str] = mapped_column(String(80))
    role: Mapped[str] = mapped_column(String(16))
    configured_by: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
