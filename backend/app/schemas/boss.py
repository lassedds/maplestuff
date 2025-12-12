"""
Pydantic schemas for Boss.
"""

from pydantic import BaseModel, ConfigDict


class BossBase(BaseModel):
    """Base boss fields."""
    name: str
    difficulty: str | None = None
    reset_type: str
    party_size: int = 1
    crystal_meso: int | None = None
    image_url: str | None = None
    sort_order: int = 0


class BossResponse(BossBase):
    """Boss response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool

    @property
    def full_name(self) -> str:
        """Get full boss name with difficulty."""
        if self.difficulty:
            return f"{self.difficulty} {self.name}"
        return self.name


class BossWithDropsResponse(BossResponse):
    """Boss response with drop table."""
    drops: list["ItemDropResponse"] = []


class ItemDropResponse(BaseModel):
    """Item in a boss drop table."""
    model_config = ConfigDict(from_attributes=True)

    item_id: int
    item_name: str
    is_guaranteed: bool


class BossListResponse(BaseModel):
    """List of bosses response."""
    bosses: list[BossResponse]
    total: int


# Update forward references
BossWithDropsResponse.model_rebuild()
