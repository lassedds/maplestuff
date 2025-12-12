"""
BossDropTable model for GMSTracker.
Maps which items can drop from which bosses.
"""

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BossDropTable(Base):
    """
    Mapping of boss to possible item drops.
    Seeded from drop table data.
    """

    __tablename__ = "boss_drop_table"
    __table_args__ = (
        UniqueConstraint("boss_id", "item_id", name="uq_boss_drop_table_boss_item"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    boss_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bosses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_guaranteed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    boss: Mapped["Boss"] = relationship("Boss", back_populates="drop_table")
    item: Mapped["Item"] = relationship("Item", back_populates="drop_sources")

    def __repr__(self) -> str:
        return f"<BossDropTable boss_id={self.boss_id} item_id={self.item_id}>"


# Import here to avoid circular imports
from app.models.boss import Boss
from app.models.item import Item
