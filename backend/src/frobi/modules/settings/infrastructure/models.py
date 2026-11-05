"""Tables owned by settings."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from frobi.shared.infrastructure import Base


class PersonSettingsModel(Base):
    __tablename__ = "person_settings"
    __table_args__ = (
        CheckConstraint("language IN ('es', 'qu', 'ay')", name="language"),
        CheckConstraint("intro_status IN ('seen', 'skipped', 'pending')", name="intro_status"),
    )

    person_id: Mapped[UUID] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True
    )
    profiles: Mapped[list[str]] = mapped_column(ARRAY(String(32)), server_default="{}")
    voice: Mapped[bool] = mapped_column(Boolean, server_default="false")
    high_contrast: Mapped[bool] = mapped_column(Boolean, server_default="false")
    large_text: Mapped[bool] = mapped_column(Boolean, server_default="false")
    short_texts: Mapped[bool] = mapped_column(Boolean, server_default="false")
    captions: Mapped[bool] = mapped_column(Boolean, server_default="false")
    large_buttons: Mapped[bool] = mapped_column(Boolean, server_default="false")
    keyboard_mode: Mapped[bool] = mapped_column(Boolean, server_default="false")
    language: Mapped[str] = mapped_column(String(2), server_default="es")
    intro_status: Mapped[str] = mapped_column(String(8), server_default="pending")
    onboarding_done: Mapped[bool] = mapped_column(Boolean, server_default="false")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
