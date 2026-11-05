"""material topics

Revision ID: 0013
Revises: 0012
Create Date: 2026-11-05 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Older materials keep NULL: their topics are found from the headings in their text.
    op.add_column("materials", sa.Column("topics", postgresql.JSONB(), nullable=True))
    op.add_column("adaptations", sa.Column("topic", sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("adaptations", "topic")
    op.drop_column("materials", "topics")
