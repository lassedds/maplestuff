"""
XP Table service - loads and provides XP requirements per level.
"""

import csv
from pathlib import Path
from decimal import Decimal
from typing import Dict

# Load XP table data
# Priority:
# 1. Docker mounted volume: /app/xp_data/XP_Table.csv
# 2. Relative path from backend: ../../Xp/XP_Table.csv (for Xp folder setup)
# 3. Project root: project_root/Xp/XP_Table.csv (for main app setup)
if Path("/app/xp_data/XP_Table.csv").exists():
    # Docker environment (mounted volume)
    XP_TABLE_PATH = Path("/app/xp_data/XP_Table.csv")
elif (Path(__file__).parent.parent.parent.parent.parent / "Xp" / "XP_Table.csv").exists():
    # Xp folder standalone setup (go up: services -> app -> backend -> maplestuff -> Xp)
    XP_TABLE_PATH = Path(__file__).parent.parent.parent.parent.parent / "Xp" / "XP_Table.csv"
else:
    # Main app setup (go up: services -> app -> backend -> maplestuff)
    XP_TABLE_PATH = Path(__file__).parent.parent.parent.parent / "Xp" / "XP_Table.csv"

_xp_table_cache: Dict[int, Dict[str, Decimal]] = {}


def load_xp_table() -> Dict[int, Dict[str, Decimal]]:
    """Load XP table from CSV file."""
    global _xp_table_cache
    
    if _xp_table_cache:
        return _xp_table_cache
    
    if not XP_TABLE_PATH.exists():
        raise FileNotFoundError(f"XP table not found at {XP_TABLE_PATH}")
    
    with open(XP_TABLE_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            level = int(row['Level'])
            _xp_table_cache[level] = {
                'actual': Decimal(row['XP Required (Actual)']),
                'billions': Decimal(row['XP Required (Billions)']),
                'trillions': Decimal(row['XP Required (Trillions)']),
            }
    
    return _xp_table_cache


def get_xp_for_level(level: int) -> Dict[str, Decimal]:
    """Get XP requirements for a specific level."""
    table = load_xp_table()
    if level not in table:
        raise ValueError(f"Level {level} not found in XP table (200-299 supported)")
    return table[level]


def calculate_xp_gained(level: int, old_percent: Decimal, new_percent: Decimal) -> Dict[str, Decimal]:
    """Calculate XP gained from percentage difference."""
    xp_data = get_xp_for_level(level)
    xp_required = xp_data['actual']
    
    percent_diff = new_percent - old_percent
    xp_gained_actual = (xp_required * percent_diff) / Decimal('100')
    
    return {
        'actual': xp_gained_actual,
        'billions': xp_gained_actual / Decimal('1000000000'),
        'trillions': xp_gained_actual / Decimal('1000000000000'),
    }
