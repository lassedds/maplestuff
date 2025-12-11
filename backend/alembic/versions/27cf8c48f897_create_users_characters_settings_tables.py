"""create_users_characters_settings_tables

Revision ID: 27cf8c48f897
Revises:
Create Date: 2025-12-11 21:59:10.841859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '27cf8c48f897'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users, characters, and user_settings tables."""

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discord_id', sa.String(255), nullable=False),
        sa.Column('discord_username', sa.String(255), nullable=True),
        sa.Column('discord_avatar', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discord_id'),
    )
    op.create_index('ix_users_discord_id', 'users', ['discord_id'])

    # Characters table
    op.create_table(
        'characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('character_name', sa.String(255), nullable=False),
        sa.Column('world', sa.String(100), nullable=False),
        sa.Column('job', sa.String(100), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('is_main', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'character_name', 'world', name='uq_character_user_name_world'),
    )
    op.create_index('ix_characters_user_id', 'characters', ['user_id'])

    # User settings table
    op.create_table(
        'user_settings',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timezone', sa.String(100), nullable=False, default='UTC'),
        sa.Column('theme', sa.String(20), nullable=False, default='dark'),
        sa.Column('default_world', sa.String(100), nullable=True),
        sa.Column('settings_json', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    """Drop users, characters, and user_settings tables."""
    op.drop_table('user_settings')
    op.drop_index('ix_characters_user_id', table_name='characters')
    op.drop_table('characters')
    op.drop_index('ix_users_discord_id', table_name='users')
    op.drop_table('users')
