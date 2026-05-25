"""create_workspace_members_and_invitations

Revision ID: 16a2996acd9d
Revises: cca1193b467e
Create Date: 2026-05-25 13:36:43.396158

"""
from alembic import op
import sqlalchemy as sa

revision = "16a2996acd9d"
down_revision = "cca1193b467e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workspace_id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('role', sa.Enum('owner', 'admin', 'member', name='memberrole'), nullable=False),
    sa.Column('token', sa.String(length=128), nullable=False),
    sa.Column('invited_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.Enum('pending', 'accepted', 'expired', 'revoked', name='invitationstatus'), nullable=False),
    sa.ForeignKeyConstraint(['invited_by_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invitations_email'), 'invitations', ['email'], unique=False)
    op.create_index(op.f('ix_invitations_id'), 'invitations', ['id'], unique=False)
    op.create_index(op.f('ix_invitations_invited_by_id'), 'invitations', ['invited_by_id'], unique=False)
    op.create_index(op.f('ix_invitations_token'), 'invitations', ['token'], unique=True)
    op.create_index(op.f('ix_invitations_workspace_id'), 'invitations', ['workspace_id'], unique=False)
    op.create_table('workspace_members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workspace_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('owner', 'admin', 'member', name='memberrole'), nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workspace_members_id'), 'workspace_members', ['id'], unique=False)
    op.create_index(op.f('ix_workspace_members_user_id'), 'workspace_members', ['user_id'], unique=False)
    op.create_index(op.f('ix_workspace_members_workspace_id'), 'workspace_members', ['workspace_id'], unique=False)
    op.create_index('ix_workspace_members_workspace_user', 'workspace_members', ['workspace_id', 'user_id'], unique=True)
    op.execute(
        """
        INSERT INTO workspace_members (workspace_id, user_id, role, joined_at)
        SELECT id AS workspace_id, user_id, 'owner' AS role, created_at AS joined_at
        FROM workspaces
        ON CONFLICT (workspace_id, user_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute("DELETE FROM workspace_members")

    op.drop_index('ix_workspace_members_workspace_user', table_name='workspace_members')
    op.drop_index(op.f('ix_workspace_members_workspace_id'), table_name='workspace_members')
    op.drop_index(op.f('ix_workspace_members_user_id'), table_name='workspace_members')
    op.drop_index(op.f('ix_workspace_members_id'), table_name='workspace_members')
    op.drop_table('workspace_members')
    op.drop_index(op.f('ix_invitations_workspace_id'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_token'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_invited_by_id'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_id'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_email'), table_name='invitations')
    op.drop_table('invitations')
    op.execute("DROP TYPE IF EXISTS invitationstatus")
    op.execute("DROP TYPE IF EXISTS memberrole")
