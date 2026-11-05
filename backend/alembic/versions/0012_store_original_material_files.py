"""store original material files

Revision ID: 0012
Revises: 0011
Create Date: 2026-11-05 10:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("materials", sa.Column("file_key", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("materials", "file_key")
