"""add workspace_id and last_accessed_at to memories

Revision ID: a9b8c7d6e5f4
Revises: 8f62f1b0c7a0
Create Date: 2026-06-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a9b8c7d6e5f4'
down_revision: Union[str, Sequence[str], None] = '8f62f1b0c7a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'memories',
        sa.Column('workspace_id', sa.Integer(), nullable=True),
    )
    op.add_column(
        'memories',
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f('ix_memories_workspace_id'), 'memories', ['workspace_id'], unique=False
    )
    op.create_foreign_key(
        'fk_memories_workspace_id',
        'memories',
        'workspaces',
        ['workspace_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('fk_memories_workspace_id', 'memories', type_='foreignkey')
    op.drop_index(op.f('ix_memories_workspace_id'), table_name='memories')
    op.drop_column('memories', 'last_accessed_at')
    op.drop_column('memories', 'workspace_id')
