"""Tables owned by adaptations."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class AdaptationModel(Base):
    __tablename__ = "adaptations"
    __table_args__ = (
        CheckConstraint(
            "format IN ('visual_map', 'real_example', 'easy_read', 'audio')", name="format"
        ),
        # Teacher panel reads always filter by class (RNF16).
        Index("ix_adaptations_class_id_person_id", "class_id", "person_id"),
        Index("ix_adaptations_person_id", "person_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    # No FK: the material may be a sample guide, which lives in the package, not in the table.
    material_id: Mapped[UUID] = mapped_column(Uuid)
    person_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    class_id: Mapped[UUID | None] = mapped_column(Uuid)
    format: Mapped[str] = mapped_column(String(16))
    content: Mapped[dict[str, Any]] = mapped_column(JSONB)
    recipe: Mapped[dict[str, Any]] = mapped_column(JSONB)
    fallback: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Topic of the material it adapts (from 1); NULL for adaptations of the whole material.
    topic: Mapped[int | None] = mapped_column(SmallInteger)
