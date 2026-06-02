"""add task position for within-column ordering

Revision ID: a1b2c3d4e5f7
Revises: f44909d8a863
Create Date: 2026-06-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f7"
down_revision = ("f44909d8a863", "3ae184b367ec")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("position", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "position")
