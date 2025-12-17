"""add_nexon_fields_to_characters

Revision ID: add_nexon_fields
Revises: bdf4578b665f
Create Date: 2025-12-13 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_nexon_fields'
down_revision: Union[str, Sequence[str], None] = 'bdf4578b665f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add nexon_ocid and character_icon_url fields to characters table."""
    op.add_column('characters', sa.Column('nexon_ocid', sa.String(255), nullable=True))
    op.add_column('characters', sa.Column('character_icon_url', sa.String(500), nullable=True))
    op.create_index('ix_characters_nexon_ocid', 'characters', ['nexon_ocid'])


def downgrade() -> None:
    """Remove nexon_ocid and character_icon_url fields from characters table."""
    op.drop_index('ix_characters_nexon_ocid', table_name='characters')
    op.drop_column('characters', 'character_icon_url')
    op.drop_column('characters', 'nexon_ocid')

