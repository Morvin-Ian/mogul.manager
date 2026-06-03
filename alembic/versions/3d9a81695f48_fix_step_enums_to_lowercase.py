"""fix_step_enums_to_lowercase

Revision ID: 3d9a81695f48
Revises: 94c41b1424a4
Create Date: 2026-06-03 15:17:54.231634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d9a81695f48'
down_revision: Union[str, Sequence[str], None] = '94c41b1424a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── stepstatus ──────────────────────────────────────────────────────────
    # Old enum: PENDING, RUNNING, COMPLETED, FAILED, SKIPPED
    # New enum: pending, in_progress, completed, skipped
    op.execute("ALTER TABLE plan_steps ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("""
        UPDATE plan_steps SET status = CASE
            WHEN UPPER(status) = 'PENDING'   THEN 'pending'
            WHEN UPPER(status) = 'RUNNING'   THEN 'in_progress'
            WHEN UPPER(status) = 'COMPLETED' THEN 'completed'
            WHEN UPPER(status) = 'FAILED'    THEN 'skipped'
            WHEN UPPER(status) = 'SKIPPED'   THEN 'skipped'
            ELSE 'pending'
        END
    """)
    op.execute("DROP TYPE IF EXISTS stepstatus")
    op.execute("CREATE TYPE stepstatus AS ENUM ('pending', 'in_progress', 'completed', 'skipped')")
    op.execute("ALTER TABLE plan_steps ALTER COLUMN status TYPE stepstatus USING status::stepstatus")

    # ── steppriority ────────────────────────────────────────────────────────
    # Old enum: LOW, MEDIUM, HIGH, URGENT  →  New: low, medium, high, urgent
    op.execute("ALTER TABLE plan_steps ALTER COLUMN priority TYPE VARCHAR(50)")
    op.execute("UPDATE plan_steps SET priority = LOWER(priority)")
    op.execute("DROP TYPE IF EXISTS steppriority")
    op.execute("CREATE TYPE steppriority AS ENUM ('low', 'medium', 'high', 'urgent')")
    op.execute("ALTER TABLE plan_steps ALTER COLUMN priority TYPE steppriority USING priority::steppriority")


def downgrade() -> None:
    op.execute("ALTER TABLE plan_steps ALTER COLUMN priority TYPE VARCHAR(50)")
    op.execute("UPDATE plan_steps SET priority = UPPER(priority)")
    op.execute("DROP TYPE IF EXISTS steppriority")
    op.execute("CREATE TYPE steppriority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT')")
    op.execute("ALTER TABLE plan_steps ALTER COLUMN priority TYPE steppriority USING priority::steppriority")

    op.execute("ALTER TABLE plan_steps ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE plan_steps SET status = UPPER(status)")
    op.execute("DROP TYPE IF EXISTS stepstatus")
    op.execute("CREATE TYPE stepstatus AS ENUM ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'SKIPPED')")
    op.execute("ALTER TABLE plan_steps ALTER COLUMN status TYPE stepstatus USING status::stepstatus")
