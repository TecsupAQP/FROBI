"""seed demo class

The demo class «Sensores 2026-II» with code SENSOR1 and its teacher, so a student can enter with
that code from the first run (PLAN_BACKEND fase 3: seed de demo). Fixed ids so the front and
the scripted demo can reference them.

Revision ID: 0010
Revises: 0009
Create Date: 2026-11-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEMO_TEACHER_ID = "00000000-0000-4000-8000-00000000d0c0"
DEMO_CLASS_ID = "00000000-0000-4000-8000-0000000000c1"


def upgrade() -> None:
    op.execute(
        sa.text(
            "INSERT INTO persons (id, alias, career, role, configured_by, created_at) "
            "VALUES (CAST(:id AS uuid), 'Docente demo', 'Instrumentación', 'teacher', 'self', "
            "now()) ON CONFLICT (id) DO NOTHING"
        ).bindparams(id=DEMO_TEACHER_ID)
    )
    op.execute(
        sa.text(
            "INSERT INTO classes (id, teacher_id, name, subject, tasks, invite_code, created_at) "
            "VALUES (CAST(:id AS uuid), CAST(:teacher AS uuid), 'Sensores 2026-II', "
            "'Instrumentación', CAST(:tasks AS jsonb), 'SENSOR1', now()) "
            "ON CONFLICT (id) DO NOTHING"
        ).bindparams(
            id=DEMO_CLASS_ID,
            teacher=DEMO_TEACHER_ID,
            tasks='["Leer la guía de sensores", "Entregar el informe"]',
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM classes WHERE id = CAST(:id AS uuid)").bindparams(id=DEMO_CLASS_ID)
    )
    op.execute(
        sa.text("DELETE FROM persons WHERE id = CAST(:id AS uuid)").bindparams(id=DEMO_TEACHER_ID)
    )
