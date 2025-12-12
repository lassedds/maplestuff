"""
Drop Rate Statistics model for GMSTracker.
Stores aggregated community drop rate data.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DropRateStats(Base):
    """
    Aggregated drop rate statistics from community data.
    Computed from BossRunDrop records across all users.
    """

    __tablename__ = "drop_rate_stats"
    __table_args__ = (
        UniqueConstraint("boss_id", "item_id", name="uq_drop_rate_stats_boss_item"),
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

    # Sample size - total number of boss runs for this boss
    sample_size: Mapped[int] = mapped_column(Integer, default=0)

    # Number of times this item dropped
    drop_count: Mapped[int] = mapped_column(Integer, default=0)

    # Computed drop rate (0.0 to 1.0)
    drop_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # When stats were last computed
    last_computed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    boss: Mapped["Boss"] = relationship("Boss")
    item: Mapped["Item"] = relationship("Item")

    def __repr__(self) -> str:
        return f"<DropRateStats boss={self.boss_id} item={self.item_id} rate={self.drop_rate:.2%}>"


# Import here to avoid circular imports
from app.models.boss import Boss
from app.models.item import Item
