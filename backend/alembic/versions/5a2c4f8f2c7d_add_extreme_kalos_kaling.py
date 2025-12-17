"""Add Extreme (X) variants for Kalos and Kaling bosses."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5a2c4f8f2c7d"
down_revision = "7c8fa4c2f6b1"
branch_labels = None
depends_on = None


def _insert_boss(name: str, difficulty: str, reset_type: str, party_size: int, crystal_meso: int, sort_order: int) -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO bosses (name, difficulty, reset_type, party_size, crystal_meso, sort_order, is_active)
            SELECT :name, :difficulty, :reset_type, :party_size, :crystal_meso, :sort_order, TRUE
            WHERE NOT EXISTS (
                SELECT 1 FROM bosses WHERE name = :name AND difficulty = :difficulty
            );
            """
        ).bindparams(
            name=name,
            difficulty=difficulty,
            reset_type=reset_type,
            party_size=party_size,
            crystal_meso=crystal_meso,
            sort_order=sort_order,
        )
    )


def upgrade() -> None:
    # Add Extreme variants so users can track XKalos / XKaling
    _insert_boss(
        name="Kalos",
        difficulty="Extreme",
        reset_type="weekly",
        party_size=6,
        crystal_meso=2500000000,
        sort_order=74,
    )
    _insert_boss(
        name="Kaling",
        difficulty="Extreme",
        reset_type="weekly",
        party_size=6,
        crystal_meso=3000000000,
        sort_order=75,
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM bosses WHERE name = 'Kalos' AND difficulty = 'Extreme'"))
    op.execute(sa.text("DELETE FROM bosses WHERE name = 'Kaling' AND difficulty = 'Extreme'"))
