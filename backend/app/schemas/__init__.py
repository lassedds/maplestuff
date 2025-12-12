"""
Pydantic schemas for GMSTracker API.
"""

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserSettingsCreate,
    UserSettingsUpdate,
    UserSettingsResponse,
)
from app.schemas.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListResponse,
)
from app.schemas.boss import (
    BossResponse,
    BossWithDropsResponse,
    BossListResponse,
    ItemDropResponse,
)
from app.schemas.item import (
    ItemResponse,
    ItemWithSourcesResponse,
    ItemListResponse,
    BossSourceResponse,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserSettingsCreate",
    "UserSettingsUpdate",
    "UserSettingsResponse",
    "CharacterCreate",
    "CharacterUpdate",
    "CharacterResponse",
    "CharacterListResponse",
    "BossResponse",
    "BossWithDropsResponse",
    "BossListResponse",
    "ItemDropResponse",
    "ItemResponse",
    "ItemWithSourcesResponse",
    "ItemListResponse",
    "BossSourceResponse",
]
