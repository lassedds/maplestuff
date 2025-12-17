"""
Epic Dungeon XP service - provides Epic Dungeon XP values per level.
"""

from decimal import Decimal
from typing import Dict, Optional

# Epic Dungeon base XP values (in billions, from research)
# These should be imported from the official spreadsheet
EPIC_DUNGEON_XP: Dict[int, Decimal] = {
    260: Decimal('194.6'),
    261: Decimal('197.4'),
    262: Decimal('200.2'),
    263: Decimal('203.0'),
    264: Decimal('206.2'),
    265: Decimal('232.0'),
    266: Decimal('235.2'),
    267: Decimal('238.4'),
    270: Decimal('384.75'),
    271: Decimal('403.05'),
    272: Decimal('408.15'),
    273: Decimal('430.65'),
    274: Decimal('436.95'),
    275: Decimal('491.10'),
    276: Decimal('497.25'),
    277: Decimal('504.30'),
    278: Decimal('510.45'),
    279: Decimal('517.50'),
    280: Decimal('581.25'),
    281: Decimal('589.20'),
    282: Decimal('596.25'),
    283: Decimal('604.20'),
    284: Decimal('611.40'),
    285: Decimal('687.30'),
    286: Decimal('695.25'),
    287: Decimal('704.25'),
    288: Decimal('713.40'),
    289: Decimal('721.50'),
    290: Decimal('810.75'),
    291: Decimal('819.90'),
    292: Decimal('830.10'),
    293: Decimal('840.45'),
    294: Decimal('849.60'),
}


def get_epic_dungeon_xp(level: int, multiplier: int = 1) -> Optional[Dict[str, Decimal]]:
    """
    Get Epic Dungeon XP for a level.
    
    multiplier: 1 = base, 4 = 4x bonus (5x total), 8 = 8x bonus (9x total)
    """
    if level not in EPIC_DUNGEON_XP:
        return None
    
    base_xp_billions = EPIC_DUNGEON_XP[level]
    
    # Calculate total multiplier
    if multiplier == 4:
        total_multiplier = Decimal('5')  # base + 4x bonus
    elif multiplier == 8:
        total_multiplier = Decimal('9')  # base + 8x bonus
    else:
        total_multiplier = Decimal(str(multiplier))
    
    xp_billions = base_xp_billions * total_multiplier
    xp_trillions = xp_billions / Decimal('1000')
    xp_actual = xp_billions * Decimal('1000000000')
    
    return {
        'actual': xp_actual,
        'billions': xp_billions,
        'trillions': xp_trillions,
    }
