"""create_boss_runs_tables

Revision ID: acc01afa1f90
Revises: 9b47e45407cd
Create Date: 2025-12-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'acc01afa1f90'
down_revision: Union[str, Sequence[str], None] = '9b47e45407cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create boss_runs and boss_run_drops tables."""

    # Boss runs table
    op.create_table(
        'boss_runs',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', UUID(as_uuid=True), nullable=False),
        sa.Column('boss_id', sa.Integer(), nullable=False),
        sa.Column('cleared_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('party_size', sa.Integer(), nullable=False, default=1),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('is_clear', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['boss_id'], ['bosses.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_boss_runs_character_id', 'boss_runs', ['character_id'])
    op.create_index('ix_boss_runs_boss_id', 'boss_runs', ['boss_id'])
    op.create_index('ix_boss_runs_week_start', 'boss_runs', ['week_start'])

    # Boss run drops table
    op.create_table(
        'boss_run_drops',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('boss_run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['boss_run_id'], ['boss_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_boss_run_drops_boss_run_id', 'boss_run_drops', ['boss_run_id'])
    op.create_index('ix_boss_run_drops_item_id', 'boss_run_drops', ['item_id'])


def downgrade() -> None:
    """Drop boss_runs and boss_run_drops tables."""
    op.drop_index('ix_boss_run_drops_item_id', table_name='boss_run_drops')
    op.drop_index('ix_boss_run_drops_boss_run_id', table_name='boss_run_drops')
    op.drop_table('boss_run_drops')
    op.drop_index('ix_boss_runs_week_start', table_name='boss_runs')
    op.drop_index('ix_boss_runs_boss_id', table_name='boss_runs')
    op.drop_index('ix_boss_runs_character_id', table_name='boss_runs')
    op.drop_table('boss_runs')
