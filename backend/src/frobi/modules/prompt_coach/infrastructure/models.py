"""Tables owned by prompt_coach."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, SmallInteger, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class PromptEvaluationModel(Base):
    __tablename__ = "prompt_evaluations"
    __table_args__ = (
        CheckConstraint("total BETWEEN 0 AND 16", name="total"),
        CheckConstraint("autonomy_level BETWEEN 1 AND 3", name="autonomy_level"),
        Index("ix_prompt_evaluations_class_id_person_id", "class_id", "person_id"),
        Index("ix_prompt_evaluations_person_id", "person_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    person_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    class_id: Mapped[UUID | None] = mapped_column(Uuid)
    text: Mapped[str] = mapped_column(Text)
    scores: Mapped[list[dict[str, Any]]] = mapped_column(JSONB)
    improved_text: Mapped[str] = mapped_column(Text)
    # Kept as columns so progress (M11) can chart the score without opening the JSON.
    total: Mapped[int] = mapped_column(SmallInteger)
    autonomy_level: Mapped[int] = mapped_column(SmallInteger)
    # No FK: may be a sample guide (not in the table) or a claim (M9, not built yet).
    material_id: Mapped[UUID | None] = mapped_column(Uuid)
    claim_id: Mapped[UUID | None] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
