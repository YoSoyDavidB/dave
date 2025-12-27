"""Task management API routes."""

from datetime import datetime

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.application.use_cases.tasks import get_task_service
from src.domain.entities.task import Task, TaskPriority, TaskStatus

logger = structlog.get_logger()
router = APIRouter(prefix="/tasks", tags=["tasks"])


# ============================================
# Request/Response Models
# ============================================


class CreateTaskRequest(BaseModel):
    """Request to create a task."""

    title: str
    description: str = ""
    priority: str = "medium"
    due_date: datetime | None = None
    tags: list[str] = []


class UpdateTaskRequest(BaseModel):
    """Request to update a task."""

    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
    tags: list[str] | None = None


class TaskResponse(BaseModel):
    """Task response."""

    task_id: str
    user_id: str
    title: str
    description: str
    status: str
    priority: str
    due_date: datetime | None
    completed_at: datetime | None
    focus_session_id: str | None
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    is_overdue: bool


class TaskStatsResponse(BaseModel):
    """Task statistics response."""

    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    overdue_tasks: int
    completion_rate: float


# ============================================
# ENDPOINTS
# ============================================


@router.post("/create")
async def create_task(user_id: str, request: CreateTaskRequest) -> TaskResponse:
    """Create a new task.

    Args:
        user_id: User creating the task
        request: Task data

    Returns:
        Created task
    """
    try:
        service = get_task_service()

        # Validate priority
        try:
            priority = TaskPriority(request.priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")

        task = await service.create_task(
            user_id=user_id,
            title=request.title,
            description=request.description,
            priority=priority,
            due_date=request.due_date,
            tags=request.tags,
        )

        return _entity_to_response(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_task_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_tasks(
    user_id: str,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 100,
) -> list[TaskResponse]:
    """Get all user tasks with optional filtering.

    Args:
        user_id: User ID
        status: Optional status filter
        priority: Optional priority filter
        limit: Maximum number of tasks

    Returns:
        List of tasks
    """
    try:
        service = get_task_service()

        # Validate filters
        status_filter = None
        if status:
            try:
                status_filter = TaskStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        priority_filter = None
        if priority:
            try:
                priority_filter = TaskPriority(priority)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")

        tasks = await service.get_all_tasks(
            user_id=user_id,
            status=status_filter,
            priority=priority_filter,
            limit=limit,
        )

        return [_entity_to_response(t) for t in tasks]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_all_tasks_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending_tasks(user_id: str) -> list[TaskResponse]:
    """Get user's pending and in-progress tasks.

    Args:
        user_id: User ID

    Returns:
        List of pending tasks
    """
    try:
        service = get_task_service()
        tasks = await service.get_pending_tasks(user_id)
        return [_entity_to_response(t) for t in tasks]

    except Exception as e:
        logger.error("get_pending_tasks_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overdue")
async def get_overdue_tasks(user_id: str) -> list[TaskResponse]:
    """Get user's overdue tasks.

    Args:
        user_id: User ID

    Returns:
        List of overdue tasks
    """
    try:
        service = get_task_service()
        tasks = await service.get_overdue_tasks(user_id)
        return [_entity_to_response(t) for t in tasks]

    except Exception as e:
        logger.error("get_overdue_tasks_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}")
async def get_task(task_id: str, user_id: str) -> TaskResponse:
    """Get a specific task.

    Args:
        task_id: Task ID
        user_id: User ID

    Returns:
        Task details
    """
    try:
        service = get_task_service()
        task = await service.get_task(task_id, user_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return _entity_to_response(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_task_failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}")
async def update_task(task_id: str, user_id: str, request: UpdateTaskRequest) -> TaskResponse:
    """Update a task.

    Args:
        task_id: Task to update
        user_id: User ID
        request: Update data

    Returns:
        Updated task
    """
    try:
        service = get_task_service()

        # Validate enums
        status = None
        if request.status:
            try:
                status = TaskStatus(request.status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {request.status}")

        priority = None
        if request.priority:
            try:
                priority = TaskPriority(request.priority)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid priority: {request.priority}",
                )

        task = await service.update_task(
            task_id=task_id,
            user_id=user_id,
            title=request.title,
            description=request.description,
            status=status,
            priority=priority,
            due_date=request.due_date,
            tags=request.tags,
        )

        return _entity_to_response(task)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_task_failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/complete")
async def complete_task(task_id: str, user_id: str) -> TaskResponse:
    """Mark a task as completed.

    Args:
        task_id: Task to complete
        user_id: User ID

    Returns:
        Completed task
    """
    try:
        service = get_task_service()
        task = await service.complete_task(task_id, user_id)
        return _entity_to_response(task)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("complete_task_failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str, user_id: str) -> TaskResponse:
    """Cancel a task.

    Args:
        task_id: Task to cancel
        user_id: User ID

    Returns:
        Cancelled task
    """
    try:
        service = get_task_service()
        task = await service.cancel_task(task_id, user_id)
        return _entity_to_response(task)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("cancel_task_failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(task_id: str, user_id: str) -> dict:
    """Delete a task permanently.

    Args:
        task_id: Task to delete
        user_id: User ID

    Returns:
        Success message
    """
    try:
        service = get_task_service()
        await service.delete_task(task_id, user_id)
        return {"message": "Task deleted successfully"}

    except Exception as e:
        logger.error("delete_task_failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/link-session")
async def link_focus_session(task_id: str, user_id: str, focus_session_id: str) -> TaskResponse:
    """Link a focus session to a task.

    Args:
        task_id: Task ID
        user_id: User ID
        focus_session_id: Focus session ID

    Returns:
        Updated task
    """
    try:
        service = get_task_service()
        task = await service.link_focus_session(task_id, user_id, focus_session_id)
        return _entity_to_response(task)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("link_session_failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_task_stats(user_id: str) -> TaskStatsResponse:
    """Get user's task statistics.

    Args:
        user_id: User ID

    Returns:
        Task statistics
    """
    try:
        service = get_task_service()
        stats = await service.get_task_stats(user_id)
        return TaskStatsResponse(**stats)

    except Exception as e:
        logger.error("get_stats_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Helper Functions
# ============================================


def _entity_to_response(entity: Task) -> TaskResponse:
    """Convert entity to response model.

    Args:
        entity: Task entity

    Returns:
        TaskResponse
    """
    return TaskResponse(
        task_id=str(entity.task_id),
        user_id=entity.user_id,
        title=entity.title,
        description=entity.description,
        status=entity.status.value,
        priority=entity.priority.value,
        due_date=entity.due_date,
        completed_at=entity.completed_at,
        focus_session_id=entity.focus_session_id,
        tags=entity.tags,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        is_overdue=entity.is_overdue(),
    )
