"""class guides and their tasks

Revision ID: 0013
Revises: 0012
Create Date: 2026-11-05 15:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "class_guides",
        sa.Column("material_id", sa.Uuid(), nullable=False),
        sa.Column("class_id", sa.Uuid(), nullable=False),
        sa.Column("mode", sa.String(length=8), nullable=False),
        sa.CheckConstraint("mode IN ('study', 'tasks')", name=op.f("ck_class_guides_mode")),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["classes.id"],
            name=op.f("fk_class_guides_class_id_classes"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["materials.id"],
            name=op.f("fk_class_guides_material_id_materials"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("material_id", name=op.f("pk_class_guides")),
    )
    op.create_index("ix_class_guides_class_id", "class_guides", ["class_id"], unique=False)
    op.create_table(
        "class_guide_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("material_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["class_guides.material_id"],
            name=op.f("fk_class_guide_tasks_material_id_class_guides"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_class_guide_tasks")),
    )
    op.create_index(
        "ix_class_guide_tasks_material_id", "class_guide_tasks", ["material_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_class_guide_tasks_material_id", table_name="class_guide_tasks")
    op.drop_table("class_guide_tasks")
    op.drop_index("ix_class_guides_class_id", table_name="class_guides")
    op.drop_table("class_guides")
