"""add_assigned_to_id_to_tasks

Revision ID: 6a813518e8fb
Revises: f44909d8a863
Create Date: 2026-05-25 13:48:07.026830

"""
from alembic import op
import sqlalchemy as sa

revision = "6a813518e8fb"
down_revision = "f44909d8a863"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("assigned_to_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tasks_assigned_to_id",
        "tasks",
        "users",
        ["assigned_to_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_tasks_assigned_to_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "assigned_to_id")
