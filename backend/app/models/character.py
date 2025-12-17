"""
Character model for GMSTracker.
Users can link multiple MapleStory characters.
"""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import UUIDMixin, TimestampMixin


class Character(Base, UUIDMixin, TimestampMixin):
    """
    A MapleStory character linked to a user account.
    """

    __tablename__ = "characters"
    __table_args__ = (
        UniqueConstraint("user_id", "character_name", "world", name="uq_character_user_name_world"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    character_name: Mapped[str] = mapped_column(String(255), nullable=False)
    world: Mapped[str] = mapped_column(String(100), nullable=False)
    job: Mapped[str | None] = mapped_column(String(100))
    level: Mapped[int | None] = mapped_column(Integer)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Nexon API fields
    nexon_ocid: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    character_icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="characters")
    boss_runs: Mapped[list["BossRun"]] = relationship(
        "BossRun",
        back_populates="character",
        cascade="all, delete-orphan",
    )
    xp_snapshots: Mapped[list["CharacterXPSnapshot"]] = relationship(
        "CharacterXPSnapshot",
        back_populates="character",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Character {self.character_name} ({self.world})>"


# Import here to avoid circular imports
from app.models.user import User
from app.models.boss_run import BossRun
from app.models.character_xp_snapshot import CharacterXPSnapshot
