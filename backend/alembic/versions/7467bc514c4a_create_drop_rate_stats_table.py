"""create_drop_rate_stats_table

Revision ID: 7467bc514c4a
Revises: acc01afa1f90
Create Date: 2025-12-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7467bc514c4a'
down_revision: Union[str, Sequence[str], None] = 'acc01afa1f90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create drop_rate_stats table for community statistics."""

    op.create_table(
        'drop_rate_stats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('boss_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=False, default=0),
        sa.Column('drop_count', sa.Integer(), nullable=False, default=0),
        sa.Column('drop_rate', sa.Float(), nullable=False, default=0.0),
        sa.Column('last_computed', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['boss_id'], ['bosses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('boss_id', 'item_id', name='uq_drop_rate_stats_boss_item'),
    )
    op.create_index('ix_drop_rate_stats_boss_id', 'drop_rate_stats', ['boss_id'])
    op.create_index('ix_drop_rate_stats_item_id', 'drop_rate_stats', ['item_id'])


def downgrade() -> None:
    """Drop drop_rate_stats table."""
    op.drop_index('ix_drop_rate_stats_item_id', table_name='drop_rate_stats')
    op.drop_index('ix_drop_rate_stats_boss_id', table_name='drop_rate_stats')
    op.drop_table('drop_rate_stats')
