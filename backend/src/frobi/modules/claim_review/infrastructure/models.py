"""Tables owned by claim_review."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class ClaimModel(Base):
    __tablename__ = "claims"
    __table_args__ = (
        # Closed vocabulary (RNF11, RNF14): no «false», no percentage.
        CheckConstraint("status IN ('supported', 'unverifiable', 'contradicts')", name="status"),
        CheckConstraint(
            "status <> 'unverifiable' OR backing_passage IS NULL", name="unverifiable_no_backing"
        ),
        Index("ix_claims_work_id_position", "work_id", "position"),
        Index("ix_claims_class_id_person_id", "class_id", "person_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    work_id: Mapped[UUID] = mapped_column(ForeignKey("works.id", ondelete="CASCADE"))
    person_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    class_id: Mapped[UUID | None] = mapped_column(Uuid)
    position: Mapped[int] = mapped_column(SmallInteger)
    section: Mapped[str] = mapped_column(String(200))
    fragment: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16))
    reason: Mapped[str] = mapped_column(Text)
    backing_passage: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
