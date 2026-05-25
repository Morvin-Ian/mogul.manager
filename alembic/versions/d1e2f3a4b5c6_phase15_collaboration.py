"""Phase 15 — Multi-user collaboration and Google OAuth

Revision ID: d1e2f3a4b5c6
Revises: a1b2c3d4e5f6
Create Date: 2026-05-25

Steps:
1. ALTER TABLE users: make password_hash nullable, add google_id (nullable, unique).
2. CREATE TYPE memberrole, invitationstatus enums.
3. CREATE TABLE workspace_members with unique constraint on (workspace_id, user_id).
4. CREATE TABLE invitations.
5. Data migration: backfill workspace_members for existing workspaces (owner role).
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "d1e2f3a4b5c6"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- 1. Alter users table ---
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(200),
        nullable=True,
    )
    op.add_column(
        "users",
        sa.Column("google_id", sa.String(200), nullable=True),
    )
    op.create_unique_constraint("uq_users_google_id", "users", ["google_id"])
    op.create_index("ix_users_google_id", "users", ["google_id"])

    # --- 2. Create enum types ---
    memberrole_enum = postgresql.ENUM(
        "owner", "admin", "member", name="memberrole", create_type=True
    )
    memberrole_enum.create(op.get_bind(), checkfirst=True)

    invitationstatus_enum = postgresql.ENUM(
        "pending", "accepted", "expired", "revoked", name="invitationstatus", create_type=True
    )
    invitationstatus_enum.create(op.get_bind(), checkfirst=True)

    # --- 3. Create workspace_members table ---
    op.create_table(
        "workspace_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("owner", "admin", "member", name="memberrole", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "workspace_id", "user_id", name="ix_workspace_members_workspace_user"
        ),
    )
    op.create_index(
        op.f("ix_workspace_members_id"), "workspace_members", ["id"]
    )
    op.create_index(
        op.f("ix_workspace_members_workspace_id"),
        "workspace_members",
        ["workspace_id"],
    )
    op.create_index(
        op.f("ix_workspace_members_user_id"), "workspace_members", ["user_id"]
    )

    # --- 4. Create invitations table ---
    op.create_table(
        "invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(120), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM("owner", "admin", "member", name="memberrole", create_type=False),
            nullable=False,
        ),
        sa.Column("token", sa.String(128), nullable=False),
        sa.Column("invited_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending", "accepted", "expired", "revoked",
                name="invitationstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.ForeignKeyConstraint(
            ["workspace_id"], ["workspaces.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["invited_by_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token", name="uq_invitations_token"),
    )
    op.create_index(op.f("ix_invitations_id"), "invitations", ["id"])
    op.create_index(
        op.f("ix_invitations_workspace_id"), "invitations", ["workspace_id"]
    )
    op.create_index(op.f("ix_invitations_email"), "invitations", ["email"])
    op.create_index(op.f("ix_invitations_token"), "invitations", ["token"])

    # --- 5. Backfill workspace_members for existing workspaces ---
    op.execute(
        """
        INSERT INTO workspace_members (workspace_id, user_id, role, joined_at)
        SELECT id AS workspace_id, user_id, 'owner' AS role, created_at AS joined_at
        FROM workspaces
        ON CONFLICT (workspace_id, user_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_invitations_token"), table_name="invitations")
    op.drop_index(op.f("ix_invitations_email"), table_name="invitations")
    op.drop_index(op.f("ix_invitations_workspace_id"), table_name="invitations")
    op.drop_index(op.f("ix_invitations_id"), table_name="invitations")
    op.drop_table("invitations")

    op.drop_index(op.f("ix_workspace_members_user_id"), table_name="workspace_members")
    op.drop_index(
        op.f("ix_workspace_members_workspace_id"), table_name="workspace_members"
    )
    op.drop_index(op.f("ix_workspace_members_id"), table_name="workspace_members")
    op.drop_table("workspace_members")

    op.execute("DROP TYPE IF EXISTS invitationstatus")
    op.execute("DROP TYPE IF EXISTS memberrole")

    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_constraint("uq_users_google_id", "users", type_="unique")
    op.drop_column("users", "google_id")
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(200),
        nullable=False,
    )
