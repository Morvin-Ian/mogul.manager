"""add budget, duration, resource fields to plans and plan_steps

Revision ID: a9b8c7d6e5f5
Revises: a9b8c7d6e5f4
Create Date: 2026-06-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'a9b8c7d6e5f5'
down_revision: Union[str, Sequence[str], None] = 'a9b8c7d6e5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Plan table additions
    op.add_column('plans', sa.Column('estimated_budget', sa.Float(), nullable=True))
    op.add_column('plans', sa.Column('actual_budget', sa.Float(), nullable=True))
    op.add_column('plans', sa.Column('start_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('plans', sa.Column('target_completion_date', sa.DateTime(timezone=True), nullable=True))

    # PlanStep table additions
    op.add_column('plan_steps', sa.Column('estimated_hours', sa.Float(), nullable=True))
    op.add_column('plan_steps', sa.Column('actual_hours', sa.Float(), nullable=True))
    op.add_column('plan_steps', sa.Column('assigned_to_id', sa.Integer(), nullable=True))
    op.add_column('plan_steps', sa.Column('cost_estimate', sa.Float(), nullable=True))
    op.create_foreign_key(
        'fk_plan_steps_assigned_to_id',
        'plan_steps', 'users',
        ['assigned_to_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_plan_steps_assigned_to_id', 'plan_steps', type_='foreignkey')
    op.drop_column('plan_steps', 'cost_estimate')
    op.drop_column('plan_steps', 'assigned_to_id')
    op.drop_column('plan_steps', 'actual_hours')
    op.drop_column('plan_steps', 'estimated_hours')
    op.drop_column('plans', 'target_completion_date')
    op.drop_column('plans', 'start_date')
    op.drop_column('plans', 'actual_budget')
    op.drop_column('plans', 'estimated_budget')
