"""Update boss crystal values to Heroic (Reboot x5) rates."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "8e3b9e0f4d12"
down_revision = "5a2c4f8f2c7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    updates = [
        ("Zakum", "Normal", 3062500),
        ("Zakum", "Chaos", 81000000),
        ("Magnus", "Easy", 3610000),
        ("Magnus", "Normal", 12960000),
        ("Magnus", "Hard", 95062500),
        ("Hilla", "Normal", 4000000),
        ("Hilla", "Hard", 56250000),
        ("Pink Bean", "Normal", 7022500),
        ("Pink Bean", "Chaos", 64000000),
        ("Cygnus", "Easy", 45562500),
        ("Cygnus", "Normal", 64000000),
        ("Cygnus", "Chaos", 203625000),
        ("Lotus", "Normal", 150062500),
        ("Lotus", "Hard", 370562500),
        ("Lotus", "Extreme", 1800000000 * 5 // 1),  # keep extreme aligned with heroic
        ("Damien", "Normal", 156250000),
        ("Damien", "Hard", 351562500),
        ("Lucid", "Easy", 175562500),
        ("Lucid", "Normal", 203062500),
        ("Lucid", "Hard", 400000000),
        ("Will", "Normal", 232562500),
        ("Will", "Hard", 441000000),
        ("Gloom", "Normal", 248062500),
        ("Gloom", "Chaos", 462250000),
        ("Darknell", "Normal", 264062500),
        ("Darknell", "Hard", 484000000),
        ("Guardian Angel Slime", "Normal", 171610000),
        ("Guardian Angel Slime", "Chaos", 451562500),
        ("Verus Hilla", "Normal", 535000000),
        ("Verus Hilla", "Hard", 800000000),
        ("Seren", "Normal", 668437500),
        ("Seren", "Hard", 756250000),
        ("Seren", "Extreme", 3025000000),
        ("Jin Hilla", "Normal", 447600000),
        ("Jin Hilla", "Hard", 552250000),
        ("Kalos", "Easy", 750000000),
        ("Kalos", "Normal", 1000000000),
        ("Kalos", "Chaos", 2000000000),
        ("Kalos", "Extreme", 4000000000),
        ("Kaling", "Easy", 750000000),
        ("Kaling", "Normal", 1150000000),
        ("Kaling", "Hard", 2300000000),
        ("Kaling", "Extreme", 4600000000),
        ("Black Mage", "Hard", 2500000000),
        ("Black Mage", "Extreme", 10000000000),
        ("Papulatus", "Chaos", 121000000),
        ("Akechi Mitsuhide", "Normal", 85202500),
        ("Omni-CLN", None, 6250000 * 5 // 1),
    ]

    for name, diff, value in updates:
        if diff:
            op.execute(
                f"UPDATE bosses SET crystal_meso = {value} WHERE name = '{name}' AND difficulty = '{diff}'"
            )
        else:
            op.execute(
                f"UPDATE bosses SET crystal_meso = {value} WHERE name = '{name}' AND difficulty IS NULL"
            )


def downgrade() -> None:
    # No reliable downgrade to previous values
    pass
