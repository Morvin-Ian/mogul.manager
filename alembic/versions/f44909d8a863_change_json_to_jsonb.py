"""change_json_to_jsonb

Revision ID: f44909d8a863
Revises: 16a2996acd9d
Create Date: 2026-05-25 13:41:06.763049

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f44909d8a863"
down_revision = "16a2996acd9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "workspaces",
        "settings",
        existing_type=postgresql.JSON(astext_type=sa.Text()),
        type_=postgresql.JSONB(astext_type=sa.Text()),
        existing_nullable=True,
        postgresql_using="settings::jsonb",
    )


def downgrade() -> None:
    op.alter_column(
        "workspaces",
        "settings",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        type_=postgresql.JSON(astext_type=sa.Text()),
        existing_nullable=True,
        postgresql_using="settings::json",
    )
