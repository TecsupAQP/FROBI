"""Tables owned by materials."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class MaterialModel(Base):
    __tablename__ = "materials"
    __table_args__ = (
        CheckConstraint("kind IN ('guide', 'brief', 'draft', 'class_content')", name="kind"),
        CheckConstraint("source IN ('sample', 'upload', 'paste')", name="source"),
        Index("ix_materials_owner_id", "owner_id"),
        Index("ix_materials_class_id", "class_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    class_id: Mapped[UUID | None] = mapped_column(ForeignKey("classes.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(16))
    source: Mapped[str] = mapped_column(String(8))
    extracted_text: Mapped[str] = mapped_column(Text)
    file_key: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WorkModel(Base):
    __tablename__ = "works"
    __table_args__ = (Index("ix_works_person_id", "person_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    person_id: Mapped[UUID] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"))
    class_id: Mapped[UUID | None] = mapped_column(Uuid)
    brief_material_id: Mapped[UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"))
    draft_material_id: Mapped[UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"))
    organized: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
