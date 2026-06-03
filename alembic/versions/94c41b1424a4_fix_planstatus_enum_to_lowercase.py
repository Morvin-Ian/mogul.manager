"""fix_planstatus_enum_to_lowercase

Revision ID: 94c41b1424a4
Revises: a7972d379712
Create Date: 2026-06-03 15:17:07.420397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94c41b1424a4'
down_revision: Union[str, Sequence[str], None] = 'a7972d379712'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert to VARCHAR so we can freely update values and swap enum type
    op.execute("ALTER TABLE plans ALTER COLUMN status TYPE VARCHAR(50)")
    # Lowercase any existing uppercase values (ACTIVE → active, etc.)
    op.execute("UPDATE plans SET status = LOWER(status)")
    # Drop the old enum type that had uppercase labels
    op.execute("DROP TYPE IF EXISTS planstatus")
    # Recreate with lowercase values to match the Python enum
    op.execute("CREATE TYPE planstatus AS ENUM ('draft', 'active', 'completed', 'cancelled')")
    # Cast the column back to the new enum type
    op.execute("ALTER TABLE plans ALTER COLUMN status TYPE planstatus USING status::planstatus")


def downgrade() -> None:
    op.execute("ALTER TABLE plans ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE plans SET status = UPPER(status)")
    op.execute("DROP TYPE IF EXISTS planstatus")
    op.execute("CREATE TYPE planstatus AS ENUM ('DRAFT', 'ACTIVE', 'COMPLETED', 'CANCELLED')")
    op.execute("ALTER TABLE plans ALTER COLUMN status TYPE planstatus USING status::planstatus")
