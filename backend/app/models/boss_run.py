"""
BossRun model for GMSTracker.
Tracks individual boss clears for characters.
"""

import uuid
from datetime import datetime, date

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import UUIDMixin, TimestampMixin


class BossRun(Base, UUIDMixin, TimestampMixin):
    """
    A record of a character clearing a boss.
    Used for tracking weekly progress and community drop statistics.
    """

    __tablename__ = "boss_runs"

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    boss_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bosses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # When the boss was cleared
    cleared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Week start date for grouping (Thursday reset for GMS)
    # Stored as the Thursday that started the week
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Party size at time of clear (for meso split calculation)
    party_size: Mapped[int] = mapped_column(Integer, default=1)

    # Optional notes from user
    notes: Mapped[str | None] = mapped_column(String(500))

    # Was this run successful? (for tracking attempts vs clears)
    is_clear: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    character: Mapped["Character"] = relationship("Character", back_populates="boss_runs")
    boss: Mapped["Boss"] = relationship("Boss", back_populates="runs")
    drops: Mapped[list["BossRunDrop"]] = relationship(
        "BossRunDrop",
        back_populates="boss_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<BossRun {self.character_id} cleared {self.boss_id} on {self.cleared_at}>"


class BossRunDrop(Base):
    """
    Items that dropped from a boss run.
    Separate table to track multiple drops per run and enable community stats.
    """

    __tablename__ = "boss_run_drops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    boss_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boss_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Quantity dropped (usually 1, but some items stack)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Relationships
    boss_run: Mapped["BossRun"] = relationship("BossRun", back_populates="drops")
    item: Mapped["Item"] = relationship("Item")

    def __repr__(self) -> str:
        return f"<BossRunDrop {self.item_id} x{self.quantity}>"


# Import here to avoid circular imports
from app.models.character import Character
from app.models.boss import Boss
from app.models.item import Item
