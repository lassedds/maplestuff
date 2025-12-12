"""
Pydantic schemas for Item.
"""

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """Base item fields."""
    name: str
    category: str | None = None
    subcategory: str | None = None
    rarity: str | None = None
    image_url: str | None = None


class ItemResponse(ItemBase):
    """Item response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool


class ItemWithSourcesResponse(ItemResponse):
    """Item response with drop sources."""
    drop_sources: list["BossSourceResponse"] = []


class BossSourceResponse(BaseModel):
    """Boss that drops this item."""
    model_config = ConfigDict(from_attributes=True)

    boss_id: int
    boss_name: str
    boss_difficulty: str | None
    is_guaranteed: bool


class ItemListResponse(BaseModel):
    """List of items response."""
    items: list[ItemResponse]
    total: int


# Update forward references
ItemWithSourcesResponse.model_rebuild()
