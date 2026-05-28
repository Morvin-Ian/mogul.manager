"""add created_by_id to projects

Revision ID: c3d4e5f6a7b8
Revises: b7c8d9e0f1a2
Create Date: 2026-05-27

"""
from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("created_by_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_projects_created_by_id_users",
        "projects",
        "users",
        ["created_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_created_by_id_users", "projects", type_="foreignkey")
    op.drop_column("projects", "created_by_id")
