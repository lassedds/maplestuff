"""Add sort_order to characters for manual reordering."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "7c8fa4c2f6b1"
down_revision = "create_xp_snapshots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "characters",
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )

    # Initialize sort_order based on creation time so existing users keep a stable order.
    op.execute(
        """
        WITH ordered AS (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) - 1 AS rn
            FROM characters
        )
        UPDATE characters SET sort_order = ordered.rn
        FROM ordered
        WHERE characters.id = ordered.id;
        """
    )

    # Remove server default after backfill
    op.alter_column("characters", "sort_order", server_default=None)


def downgrade() -> None:
    op.drop_column("characters", "sort_order")
