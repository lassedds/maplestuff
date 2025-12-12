"""
Pydantic schemas for task management.
"""

from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Task schemas
class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    reset_type: str = Field(..., pattern="^(daily|weekly|monthly)$")
    sort_order: int = 0


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(None, max_length=100)
    sort_order: int | None = None
    is_active: bool | None = None


class TaskResponse(BaseModel):
    """Response schema for a task."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    category: str | None
    reset_type: str
    is_system: bool
    is_active: bool
    sort_order: int
    created_by_id: UUID | None = None


class TaskListResponse(BaseModel):
    """List of tasks."""

    tasks: list[TaskResponse]
    total: int


# UserTask schemas
class UserTaskCreate(BaseModel):
    """Schema for adding a task to user's checklist."""

    task_id: UUID
    character_id: UUID | None = None
    sort_order: int = 0


class UserTaskUpdate(BaseModel):
    """Schema for updating a user task."""

    character_id: UUID | None = None
    sort_order: int | None = None
    is_enabled: bool | None = None


class UserTaskResponse(BaseModel):
    """Response schema for a user task."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    task_id: UUID
    character_id: UUID | None
    sort_order: int
    is_enabled: bool
    created_at: datetime

    # Task details
    task_name: str | None = None
    task_description: str | None = None
    task_category: str | None = None
    task_reset_type: str | None = None


class UserTaskWithCompletionResponse(UserTaskResponse):
    """User task with completion status for current period."""

    is_completed: bool = False
    completed_at: datetime | None = None


class UserTaskListResponse(BaseModel):
    """List of user tasks."""

    tasks: list[UserTaskWithCompletionResponse]
    total: int


# TaskCompletion schemas
class TaskCompletionCreate(BaseModel):
    """Schema for completing a task."""

    user_task_id: UUID
    completion_date: date | None = None  # Defaults to today


class TaskCompletionResponse(BaseModel):
    """Response schema for a task completion."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_task_id: UUID
    completion_date: date
    completed_at: datetime


# Daily checklist schemas
class DailyChecklistResponse(BaseModel):
    """Daily checklist showing all tasks and their completion status."""

    date: date
    tasks: list[UserTaskWithCompletionResponse]
    completed_count: int
    total_count: int
    completion_percent: float


class WeeklyChecklistResponse(BaseModel):
    """Weekly checklist for weekly tasks."""

    week_start: date
    week_end: date
    tasks: list[UserTaskWithCompletionResponse]
    completed_count: int
    total_count: int
    completion_percent: float
