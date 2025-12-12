"""create_bosses_items_drop_table

Revision ID: 9b47e45407cd
Revises: 27cf8c48f897
Create Date: 2025-12-12 20:20:30.214918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b47e45407cd'
down_revision: Union[str, Sequence[str], None] = '27cf8c48f897'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create bosses, items, and boss_drop_table tables."""

    # Bosses table
    op.create_table(
        'bosses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('difficulty', sa.String(50), nullable=True),
        sa.Column('reset_type', sa.String(20), nullable=False),
        sa.Column('party_size', sa.Integer(), nullable=False, default=1),
        sa.Column('crystal_meso', sa.BigInteger(), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'difficulty', name='uq_boss_name_difficulty'),
    )

    # Items table
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('rarity', sa.String(50), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # Boss drop table (many-to-many)
    op.create_table(
        'boss_drop_table',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('boss_id', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('is_guaranteed', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['boss_id'], ['bosses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('boss_id', 'item_id', name='uq_boss_drop_table_boss_item'),
    )
    op.create_index('ix_boss_drop_table_boss_id', 'boss_drop_table', ['boss_id'])
    op.create_index('ix_boss_drop_table_item_id', 'boss_drop_table', ['item_id'])


def downgrade() -> None:
    """Drop bosses, items, and boss_drop_table tables."""
    op.drop_index('ix_boss_drop_table_item_id', table_name='boss_drop_table')
    op.drop_index('ix_boss_drop_table_boss_id', table_name='boss_drop_table')
    op.drop_table('boss_drop_table')
    op.drop_table('items')
    op.drop_table('bosses')
