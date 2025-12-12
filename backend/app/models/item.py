"""
Item model for GMSTracker.
Contains all MapleStory item definitions.
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    """
    MapleStory item definition.
    Seeded from item data, not user-created.
    """

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(String(100))  # equipment, scroll, nodestone, etc.
    subcategory: Mapped[str | None] = mapped_column(String(100))  # weapon, hat, gloves, etc.
    rarity: Mapped[str | None] = mapped_column(String(50))  # common, rare, epic, unique, legendary
    image_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    drop_sources: Mapped[list["BossDropTable"]] = relationship(
        "BossDropTable",
        back_populates="item",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Item {self.name}>"


# Import here to avoid circular imports
from app.models.boss_drop_table import BossDropTable
