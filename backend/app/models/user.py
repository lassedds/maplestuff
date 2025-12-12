"""
User model for GMSTracker.
Users authenticate via Discord OAuth.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """
    User account linked to Discord.
    """

    __tablename__ = "users"

    discord_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    discord_username: Mapped[str | None] = mapped_column(String(255))
    discord_avatar: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    characters: Mapped[list["Character"]] = relationship(
        "Character",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    settings: Mapped["UserSettings | None"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    user_tasks: Mapped[list["UserTask"]] = relationship(
        "UserTask",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    created_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="created_by",
    )

    def __repr__(self) -> str:
        return f"<User {self.discord_username} ({self.discord_id})>"


# Import here to avoid circular imports
from app.models.character import Character
from app.models.user_settings import UserSettings
from app.models.task import Task, UserTask
