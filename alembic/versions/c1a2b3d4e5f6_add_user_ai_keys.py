"""add user_ai_keys

Revision ID: c1a2b3d4e5f6
Revises: a9b8c7d6e5f5
Create Date: 2026-08-30

"""
from alembic import op
import sqlalchemy as sa

revision = "c1a2b3d4e5f6"
down_revision = "a9b8c7d6e5f5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_ai_keys",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("api_key_encrypted", sa.Text(), nullable=False),
        sa.Column("key_hint", sa.String(length=8), nullable=False, server_default=""),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "uuid",
            sa.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "provider", name="uq_user_ai_keys_user_provider"
        ),
    )
    op.create_index(op.f("ix_user_ai_keys_id"), "user_ai_keys", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_ai_keys_user_id"), "user_ai_keys", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_user_ai_keys_uuid"), "user_ai_keys", ["uuid"], unique=True
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_ai_keys_uuid"), table_name="user_ai_keys")
    op.drop_index(op.f("ix_user_ai_keys_user_id"), table_name="user_ai_keys")
    op.drop_index(op.f("ix_user_ai_keys_id"), table_name="user_ai_keys")
    op.drop_table("user_ai_keys")
