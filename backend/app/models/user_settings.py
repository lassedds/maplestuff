"""
User settings model for GMSTracker.
Stores user preferences like timezone, theme, etc.
"""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin


class UserSettings(Base, TimestampMixin):
    """
    User preferences and settings.
    One-to-one relationship with User.
    """

    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    theme: Mapped[str] = mapped_column(String(20), default="dark")
    default_world: Mapped[str | None] = mapped_column(String(100))
    settings_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings for user_id={self.user_id}>"


# Import here to avoid circular imports
from app.models.user import User
