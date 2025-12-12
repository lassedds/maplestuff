"""
Task models for GMSTracker.
Tracks daily/weekly tasks and their completions.
"""

import uuid
from datetime import datetime, date

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import UUIDMixin, TimestampMixin


class Task(Base, UUIDMixin, TimestampMixin):
    """
    A task definition (e.g., "Arcane River Dailies", "Ursus").
    Can be system-defined (is_system=True) or user-created.
    """

    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))  # dailies, weeklies, events
    reset_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily, weekly, monthly
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # System-defined vs user-created
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # For user-created tasks, this is the owner
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    created_by: Mapped["User | None"] = relationship("User", back_populates="created_tasks")
    user_tasks: Mapped[list["UserTask"]] = relationship(
        "UserTask",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Task {self.name} ({self.reset_type})>"


class UserTask(Base, UUIDMixin, TimestampMixin):
    """
    A task that a user has added to their checklist.
    Links users to tasks they want to track.
    """

    __tablename__ = "user_tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional character association for character-specific tasks
    character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
    )

    # User's custom sort order
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_tasks")
    task: Mapped["Task"] = relationship("Task", back_populates="user_tasks")
    character: Mapped["Character | None"] = relationship("Character")
    completions: Mapped[list["TaskCompletion"]] = relationship(
        "TaskCompletion",
        back_populates="user_task",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<UserTask user={self.user_id} task={self.task_id}>"


class TaskCompletion(Base):
    """
    Record of a task being completed.
    Stores the date for tracking daily/weekly completions.
    """

    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The date/period this completion is for
    completion_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # When the completion was actually recorded
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user_task: Mapped["UserTask"] = relationship("UserTask", back_populates="completions")

    def __repr__(self) -> str:
        return f"<TaskCompletion {self.user_task_id} on {self.completion_date}>"


# Import here to avoid circular imports
from app.models.user import User
from app.models.character import Character
