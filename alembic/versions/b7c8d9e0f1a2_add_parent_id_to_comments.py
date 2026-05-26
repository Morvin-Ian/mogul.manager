"""add_parent_id_to_comments

Revision ID: b7c8d9e0f1a2
Revises: f44909d8a863
Create Date: 2026-05-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "b7c8d9e0f1a2"
down_revision = "6a813518e8fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "comments",
        sa.Column("parent_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_comments_parent_id",
        "comments",
        "comments",
        ["parent_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_comments_parent_id", "comments", type_="foreignkey")
    op.drop_column("comments", "parent_id")
