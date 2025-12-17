"""create character xp snapshots table

Revision ID: create_xp_snapshots
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'create_xp_snapshots'
down_revision: Union[str, None] = 'add_nexon_fields'  # Latest migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create character_xp_snapshots table
    op.create_table(
        'character_xp_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('total_xp', sa.Numeric(30, 0), nullable=False),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('character_id', 'snapshot_date', name='uq_character_xp_snapshot_date')
    )
    op.create_index(op.f('ix_character_xp_snapshots_character_id'), 'character_xp_snapshots', ['character_id'], unique=False)
    op.create_index(op.f('ix_character_xp_snapshots_snapshot_date'), 'character_xp_snapshots', ['snapshot_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_character_xp_snapshots_snapshot_date'), table_name='character_xp_snapshots')
    op.drop_index(op.f('ix_character_xp_snapshots_character_id'), table_name='character_xp_snapshots')
    op.drop_table('character_xp_snapshots')
