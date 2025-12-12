"""
Task management API endpoints for GMSTracker.
Authenticated endpoints for managing daily/weekly task checklists.
"""

from datetime import date, timedelta, timezone, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession, CurrentUser
from app.models import Task, UserTask, TaskCompletion
from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    UserTaskCreate,
    UserTaskUpdate,
    UserTaskResponse,
    UserTaskWithCompletionResponse,
    UserTaskListResponse,
    TaskCompletionCreate,
    TaskCompletionResponse,
    DailyChecklistResponse,
    WeeklyChecklistResponse,
    get_current_week_start,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# Task definition endpoints
@router.get("", response_model=TaskListResponse)
async def list_tasks(
    db: DBSession,
    category: str | None = Query(None, description="Filter by category"),
    reset_type: str | None = Query(None, description="Filter by reset type"),
    system_only: bool = Query(False, description="Only return system tasks"),
) -> TaskListResponse:
    """
    List all available tasks.
    Includes both system-defined and user-created tasks.
    """
    query = select(Task).where(Task.is_active == True).order_by(Task.sort_order, Task.name)

    if category:
        query = query.where(Task.category == category)

    if reset_type:
        query = query.where(Task.reset_type == reset_type)

    if system_only:
        query = query.where(Task.is_system == True)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=len(tasks),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> TaskResponse:
    """
    Create a custom task.
    """
    task = Task(
        name=task_data.name,
        description=task_data.description,
        category=task_data.category,
        reset_type=task_data.reset_type,
        sort_order=task_data.sort_order,
        is_system=False,
        created_by_id=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """
    Delete a user-created task.
    System tasks cannot be deleted.
    """
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System tasks cannot be deleted",
        )

    if task.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete tasks you created",
        )

    await db.delete(task)
    await db.commit()


# User task (checklist) endpoints
@router.get("/my", response_model=UserTaskListResponse)
async def get_my_tasks(
    db: DBSession,
    current_user: CurrentUser,
    reset_type: str | None = Query(None, description="Filter by reset type"),
) -> UserTaskListResponse:
    """
    Get the current user's task checklist with completion status.
    """
    today = date.today()
    week_start = get_current_week_start()

    query = (
        select(UserTask)
        .where(UserTask.user_id == current_user.id, UserTask.is_enabled == True)
        .options(
            selectinload(UserTask.task),
            selectinload(UserTask.completions),
        )
        .order_by(UserTask.sort_order)
    )

    if reset_type:
        query = query.join(Task).where(Task.reset_type == reset_type)

    result = await db.execute(query)
    user_tasks = result.scalars().all()

    tasks_with_completion = []
    for ut in user_tasks:
        # Check completion based on reset type
        is_completed = False
        completed_at = None

        if ut.task.reset_type == "daily":
            completion = next(
                (c for c in ut.completions if c.completion_date == today), None
            )
        elif ut.task.reset_type == "weekly":
            completion = next(
                (c for c in ut.completions if c.completion_date >= week_start), None
            )
        else:  # monthly
            month_start = today.replace(day=1)
            completion = next(
                (c for c in ut.completions if c.completion_date >= month_start), None
            )

        if completion:
            is_completed = True
            completed_at = completion.completed_at

        tasks_with_completion.append(
            UserTaskWithCompletionResponse(
                id=ut.id,
                user_id=ut.user_id,
                task_id=ut.task_id,
                character_id=ut.character_id,
                sort_order=ut.sort_order,
                is_enabled=ut.is_enabled,
                created_at=ut.created_at,
                task_name=ut.task.name,
                task_description=ut.task.description,
                task_category=ut.task.category,
                task_reset_type=ut.task.reset_type,
                is_completed=is_completed,
                completed_at=completed_at,
            )
        )

    return UserTaskListResponse(
        tasks=tasks_with_completion,
        total=len(tasks_with_completion),
    )


@router.post("/my", response_model=UserTaskResponse, status_code=status.HTTP_201_CREATED)
async def add_task_to_checklist(
    user_task_data: UserTaskCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> UserTaskResponse:
    """
    Add a task to the user's checklist.
    """
    # Verify task exists
    task_result = await db.execute(select(Task).where(Task.id == user_task_data.task_id))
    task = task_result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Check if already added
    existing = await db.execute(
        select(UserTask).where(
            UserTask.user_id == current_user.id,
            UserTask.task_id == user_task_data.task_id,
            UserTask.character_id == user_task_data.character_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task already in checklist",
        )

    user_task = UserTask(
        user_id=current_user.id,
        task_id=user_task_data.task_id,
        character_id=user_task_data.character_id,
        sort_order=user_task_data.sort_order,
    )
    db.add(user_task)
    await db.commit()
    await db.refresh(user_task)

    # Load task details
    result = await db.execute(
        select(UserTask)
        .where(UserTask.id == user_task.id)
        .options(selectinload(UserTask.task))
    )
    user_task = result.scalar_one()

    return UserTaskResponse(
        id=user_task.id,
        user_id=user_task.user_id,
        task_id=user_task.task_id,
        character_id=user_task.character_id,
        sort_order=user_task.sort_order,
        is_enabled=user_task.is_enabled,
        created_at=user_task.created_at,
        task_name=user_task.task.name,
        task_description=user_task.task.description,
        task_category=user_task.task.category,
        task_reset_type=user_task.task.reset_type,
    )


@router.delete("/my/{user_task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task_from_checklist(
    user_task_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """
    Remove a task from the user's checklist.
    """
    result = await db.execute(
        select(UserTask).where(
            UserTask.id == user_task_id,
            UserTask.user_id == current_user.id,
        )
    )
    user_task = result.scalar_one_or_none()

    if not user_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not in your checklist",
        )

    await db.delete(user_task)
    await db.commit()


# Task completion endpoints
@router.post("/my/{user_task_id}/complete", response_model=TaskCompletionResponse)
async def complete_task(
    user_task_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    completion_date: date | None = Query(None, description="Date to mark complete (defaults to today)"),
) -> TaskCompletionResponse:
    """
    Mark a task as complete for the current period.
    """
    result = await db.execute(
        select(UserTask)
        .where(
            UserTask.id == user_task_id,
            UserTask.user_id == current_user.id,
        )
        .options(selectinload(UserTask.task))
    )
    user_task = result.scalar_one_or_none()

    if not user_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not in your checklist",
        )

    target_date = completion_date or date.today()

    # Check if already completed for this period
    if user_task.task.reset_type == "daily":
        check_date = target_date
    elif user_task.task.reset_type == "weekly":
        check_date = get_current_week_start()
    else:  # monthly
        check_date = target_date.replace(day=1)

    existing = await db.execute(
        select(TaskCompletion).where(
            TaskCompletion.user_task_id == user_task_id,
            TaskCompletion.completion_date >= check_date,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task already completed for this period",
        )

    completion = TaskCompletion(
        user_task_id=user_task_id,
        completion_date=target_date,
    )
    db.add(completion)
    await db.commit()
    await db.refresh(completion)

    return TaskCompletionResponse.model_validate(completion)


@router.delete("/my/{user_task_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def uncomplete_task(
    user_task_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
    completion_date: date | None = Query(None, description="Date to uncomplete (defaults to today)"),
) -> None:
    """
    Remove a task completion for the current period.
    """
    result = await db.execute(
        select(UserTask)
        .where(
            UserTask.id == user_task_id,
            UserTask.user_id == current_user.id,
        )
        .options(selectinload(UserTask.task))
    )
    user_task = result.scalar_one_or_none()

    if not user_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not in your checklist",
        )

    target_date = completion_date or date.today()

    # Find and delete completion for this period
    if user_task.task.reset_type == "daily":
        completion_result = await db.execute(
            select(TaskCompletion).where(
                TaskCompletion.user_task_id == user_task_id,
                TaskCompletion.completion_date == target_date,
            )
        )
    elif user_task.task.reset_type == "weekly":
        week_start = get_current_week_start()
        completion_result = await db.execute(
            select(TaskCompletion).where(
                TaskCompletion.user_task_id == user_task_id,
                TaskCompletion.completion_date >= week_start,
            )
        )
    else:  # monthly
        month_start = target_date.replace(day=1)
        completion_result = await db.execute(
            select(TaskCompletion).where(
                TaskCompletion.user_task_id == user_task_id,
                TaskCompletion.completion_date >= month_start,
            )
        )

    completion = completion_result.scalar_one_or_none()
    if not completion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No completion found for this period",
        )

    await db.delete(completion)
    await db.commit()


# Checklist view endpoints
@router.get("/checklist/daily", response_model=DailyChecklistResponse)
async def get_daily_checklist(
    db: DBSession,
    current_user: CurrentUser,
    target_date: date | None = Query(None, description="Date to view (defaults to today)"),
) -> DailyChecklistResponse:
    """
    Get the daily task checklist with completion status.
    """
    check_date = target_date or date.today()

    result = await db.execute(
        select(UserTask)
        .where(UserTask.user_id == current_user.id, UserTask.is_enabled == True)
        .join(Task)
        .where(Task.reset_type == "daily")
        .options(
            selectinload(UserTask.task),
            selectinload(UserTask.completions),
        )
        .order_by(UserTask.sort_order)
    )
    user_tasks = result.scalars().all()

    tasks_with_completion = []
    completed_count = 0

    for ut in user_tasks:
        completion = next(
            (c for c in ut.completions if c.completion_date == check_date), None
        )
        is_completed = completion is not None
        if is_completed:
            completed_count += 1

        tasks_with_completion.append(
            UserTaskWithCompletionResponse(
                id=ut.id,
                user_id=ut.user_id,
                task_id=ut.task_id,
                character_id=ut.character_id,
                sort_order=ut.sort_order,
                is_enabled=ut.is_enabled,
                created_at=ut.created_at,
                task_name=ut.task.name,
                task_description=ut.task.description,
                task_category=ut.task.category,
                task_reset_type=ut.task.reset_type,
                is_completed=is_completed,
                completed_at=completion.completed_at if completion else None,
            )
        )

    total = len(tasks_with_completion)
    return DailyChecklistResponse(
        date=check_date,
        tasks=tasks_with_completion,
        completed_count=completed_count,
        total_count=total,
        completion_percent=(completed_count / total * 100) if total > 0 else 0,
    )


@router.get("/checklist/weekly", response_model=WeeklyChecklistResponse)
async def get_weekly_checklist(
    db: DBSession,
    current_user: CurrentUser,
) -> WeeklyChecklistResponse:
    """
    Get the weekly task checklist with completion status.
    """
    week_start = get_current_week_start()
    week_end = week_start + timedelta(days=6)

    result = await db.execute(
        select(UserTask)
        .where(UserTask.user_id == current_user.id, UserTask.is_enabled == True)
        .join(Task)
        .where(Task.reset_type == "weekly")
        .options(
            selectinload(UserTask.task),
            selectinload(UserTask.completions),
        )
        .order_by(UserTask.sort_order)
    )
    user_tasks = result.scalars().all()

    tasks_with_completion = []
    completed_count = 0

    for ut in user_tasks:
        completion = next(
            (c for c in ut.completions if c.completion_date >= week_start), None
        )
        is_completed = completion is not None
        if is_completed:
            completed_count += 1

        tasks_with_completion.append(
            UserTaskWithCompletionResponse(
                id=ut.id,
                user_id=ut.user_id,
                task_id=ut.task_id,
                character_id=ut.character_id,
                sort_order=ut.sort_order,
                is_enabled=ut.is_enabled,
                created_at=ut.created_at,
                task_name=ut.task.name,
                task_description=ut.task.description,
                task_category=ut.task.category,
                task_reset_type=ut.task.reset_type,
                is_completed=is_completed,
                completed_at=completion.completed_at if completion else None,
            )
        )

    total = len(tasks_with_completion)
    return WeeklyChecklistResponse(
        week_start=week_start,
        week_end=week_end,
        tasks=tasks_with_completion,
        completed_count=completed_count,
        total_count=total,
        completion_percent=(completed_count / total * 100) if total > 0 else 0,
    )
