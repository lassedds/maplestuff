"""
XP Entry model for tracking daily XP gains.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import UUIDMixin, TimestampMixin


class XPEntry(Base, UUIDMixin, TimestampMixin):
    """
    Daily XP tracking entry.
    """

    __tablename__ = "xp_entries"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    old_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
    new_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )
    xp_gained_trillions: Mapped[Decimal] = mapped_column(
        Numeric(20, 6),
        nullable=False,
    )
    xp_gained_billions: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )
    epic_dungeon: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    epic_dungeon_xp_trillions: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 6),
        nullable=True,
    )
    epic_dungeon_xp_billions: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 2),
        nullable=True,
    )
    epic_dungeon_multiplier: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    total_daily_xp_trillions: Mapped[Decimal] = mapped_column(
        Numeric(20, 6),
        nullable=False,
    )
    total_daily_xp_billions: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="xp_entries",
    )

    def __repr__(self) -> str:
        return f"<XPEntry {self.entry_date} Lv{self.level} {self.old_percent}%->{self.new_percent}%>"


# Import here to avoid circular imports
from app.models.user import User
