"""
Character XP Snapshot model for tracking daily XP from Nexon rankings API.
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import UUIDMixin, TimestampMixin


class CharacterXPSnapshot(Base, UUIDMixin, TimestampMixin):
    """
    Daily XP snapshot for a character from Nexon rankings API.
    Stores the total XP value at a point in time.
    """

    __tablename__ = "character_xp_snapshots"
    __table_args__ = (
        UniqueConstraint("character_id", "snapshot_date", name="uq_character_xp_snapshot_date"),
    )

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )
    total_xp: Mapped[Decimal] = mapped_column(
        Numeric(30, 0),  # Large enough for total XP values
        nullable=False,
    )
    level: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    # Relationships
    character: Mapped["Character"] = relationship(
        "Character",
        back_populates="xp_snapshots",
    )

    def __repr__(self) -> str:
        return f"<CharacterXPSnapshot {self.character_id} {self.snapshot_date} XP={self.total_xp}>"


# Import here to avoid circular imports
from app.models.character import Character
