"""fix workspace FK constraints: plans SET NULL, projects CASCADE

Revision ID: e5f6a7b8c9d0
Revises: c3d4e5f6a7b8
Create Date: 2026-05-28

"""
from alembic import op

revision = 'e5f6a7b8c9d0'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # plans.workspace_id: drop old FK, add with ON DELETE SET NULL
    op.drop_constraint('plans_workspace_id_fkey', 'plans', type_='foreignkey')
    op.create_foreign_key(
        'plans_workspace_id_fkey',
        'plans', 'workspaces',
        ['workspace_id'], ['id'],
        ondelete='SET NULL',
    )

    # projects.workspace_id: drop old FK, add with ON DELETE CASCADE
    op.drop_constraint('projects_workspace_id_fkey', 'projects', type_='foreignkey')
    op.create_foreign_key(
        'projects_workspace_id_fkey',
        'projects', 'workspaces',
        ['workspace_id'], ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    op.drop_constraint('projects_workspace_id_fkey', 'projects', type_='foreignkey')
    op.create_foreign_key(
        'projects_workspace_id_fkey',
        'projects', 'workspaces',
        ['workspace_id'], ['id'],
    )

    op.drop_constraint('plans_workspace_id_fkey', 'plans', type_='foreignkey')
    op.create_foreign_key(
        'plans_workspace_id_fkey',
        'plans', 'workspaces',
        ['workspace_id'], ['id'],
    )
