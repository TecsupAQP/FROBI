"""link class content to its class

Revision ID: 0011
Revises: 0010
Create Date: 2026-11-04 21:50:05.547233
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_materials_class_id", "materials", ["class_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_materials_class_id_classes"),
        "materials",
        "classes",
        ["class_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk_materials_class_id_classes"), "materials", type_="foreignkey")
    op.drop_index("ix_materials_class_id", table_name="materials")
