"""create_task_tables

Revision ID: bdf4578b665f
Revises: 7467bc514c4a
Create Date: 2025-12-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'bdf4578b665f'
down_revision: Union[str, Sequence[str], None] = '7467bc514c4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tasks, user_tasks, and task_completions tables."""

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('reset_type', sa.String(20), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_by_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
    )

    # User tasks table
    op.create_table(
        'user_tasks',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', UUID(as_uuid=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_user_tasks_user_id', 'user_tasks', ['user_id'])
    op.create_index('ix_user_tasks_task_id', 'user_tasks', ['task_id'])

    # Task completions table
    op.create_table(
        'task_completions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_task_id', UUID(as_uuid=True), nullable=False),
        sa.Column('completion_date', sa.Date(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_task_id'], ['user_tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_task_completions_user_task_id', 'task_completions', ['user_task_id'])
    op.create_index('ix_task_completions_completion_date', 'task_completions', ['completion_date'])


def downgrade() -> None:
    """Drop tasks, user_tasks, and task_completions tables."""
    op.drop_index('ix_task_completions_completion_date', table_name='task_completions')
    op.drop_index('ix_task_completions_user_task_id', table_name='task_completions')
    op.drop_table('task_completions')
    op.drop_index('ix_user_tasks_task_id', table_name='user_tasks')
    op.drop_index('ix_user_tasks_user_id', table_name='user_tasks')
    op.drop_table('user_tasks')
    op.drop_table('tasks')
