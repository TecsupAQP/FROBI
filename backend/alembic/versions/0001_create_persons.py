"""create persons

Revision ID: 0001
Revises:
Create Date: 2026-11-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "persons",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alias", sa.String(length=40), nullable=False),
        sa.Column("career", sa.String(length=80), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("configured_by", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('learner', 'teacher')", name=op.f("ck_persons_role")),
        sa.CheckConstraint(
            "configured_by IN ('self', 'companion')", name=op.f("ck_persons_configured_by")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_persons")),
    )


def downgrade() -> None:
    op.drop_table("persons")
