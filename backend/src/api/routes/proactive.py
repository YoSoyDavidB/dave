"""Proactive features API routes - reminders, goals, suggestions."""

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.api.routes.auth import get_current_user
from src.application.use_cases.proactive import get_proactive_service
from src.application.use_cases.vault_memory_extraction import get_vault_memory_extraction
from src.core.models import User

logger = structlog.get_logger()
router = APIRouter(tags=["proactive"])


class ReminderResponse(BaseModel):
    """Response model for a task reminder."""

    memory_id: str
    task_text: str
    due_date: datetime
    is_overdue: bool
    hours_until_due: float


class GoalResponse(BaseModel):
    """Response model for a goal with progress."""

    memory_id: str
    goal_text: str
    progress: float
    last_referenced: datetime
    created_at: datetime


class TaskResponse(BaseModel):
    """Response model for a pending task."""

    memory_id: str
    task_text: str
    due_date: datetime | None
    created_at: datetime
    source: str


class MarkCompletedRequest(BaseModel):
    """Request to mark a task as completed."""

    memory_id: str


@router.get("/reminders")
async def get_reminders(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get pending task reminders for the current user.

    Returns reminders for tasks that are:
    - Due within 24 hours
    - Overdue
    - Not yet reminded

    Returns:
        Dict with list of reminders
    """
    try:
        proactive = get_proactive_service()
        reminders = await proactive.get_pending_reminders(current_user.id)

        return {
            "reminders": [
                ReminderResponse(
                    memory_id=r.memory_id,
                    task_text=r.task_text,
                    due_date=r.due_date,
                    is_overdue=r.is_overdue,
                    hours_until_due=r.hours_until_due,
                )
                for r in reminders
            ],
            "count": len(reminders),
        }

    except Exception as e:
        logger.error("get_reminders_failed", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get reminders")


@router.post("/tasks/complete")
async def mark_task_completed(
    request: MarkCompletedRequest,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Mark a task as completed.

    Args:
        request: Request with memory_id of task to complete
        current_user: Current authenticated user

    Returns:
        Success status
    """
    try:
        proactive = get_proactive_service()
        success = await proactive.mark_task_completed(
            request.memory_id,
            current_user.id,
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Task not found or not owned by user",
            )

        return {"success": True, "message": "Task marked as completed"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "mark_completed_failed",
            memory_id=request.memory_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail="Failed to mark task completed")


@router.get("/goals")
async def get_active_goals(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get active goals with progress tracking.

    Returns goals that are not yet completed (progress < 100%).

    Returns:
        Dict with list of active goals
    """
    try:
        proactive = get_proactive_service()
        goals = await proactive.get_active_goals(current_user.id)

        return {
            "goals": [
                GoalResponse(
                    memory_id=str(g.memory_id),
                    goal_text=g.short_text,
                    progress=g.progress,
                    last_referenced=g.last_referenced_at,
                    created_at=g.timestamp,
                )
                for g in goals
            ],
            "count": len(goals),
        }

    except Exception as e:
        logger.error("get_goals_failed", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get goals")


@router.get("/tasks")
async def get_pending_tasks(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get all pending tasks regardless of due date.

    Returns all tasks that are not completed (completed=False).

    Returns:
        Dict with list of pending tasks
    """
    try:
        proactive = get_proactive_service()
        tasks = await proactive.get_all_pending_tasks(current_user.id)

        return {
            "tasks": [
                TaskResponse(
                    memory_id=str(t.memory_id),
                    task_text=t.short_text,
                    due_date=t.due_date,
                    created_at=t.timestamp,
                    source=t.source,
                )
                for t in tasks
            ],
            "count": len(tasks),
        }

    except Exception as e:
        logger.error("get_tasks_failed", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get tasks")


@router.post("/sync-vault-tasks")
async def sync_vault_tasks(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Sync tasks from vault daily notes.

    Extracts tasks and goals from recent daily notes (last 7 days)
    and stores them as memories.

    Returns:
        Status message with count of extracted tasks
    """
    print(f"[DEBUG] sync_vault_tasks called for user: {current_user.id}")
    try:
        logger.info("sync_vault_tasks_started", user_id=current_user.id)
        print("[DEBUG] Getting vault_extraction service...")
        vault_extraction = get_vault_memory_extraction()

        print("[DEBUG] Starting process_recent_daily_notes...")
        # Run extraction synchronously to ensure it completes
        memories = await vault_extraction.process_recent_daily_notes(
            current_user.id,
        )

        print(f"[DEBUG] Extraction complete. Found {len(memories)} memories")
        logger.info(
            "sync_vault_tasks_completed",
            user_id=current_user.id,
            memories_count=len(memories),
        )

        return {
            "status": "completed",
            "message": f"Synced {len(memories)} tasks/goals from vault",
            "count": len(memories),
        }

    except Exception as e:
        print(f"[DEBUG] ERROR in sync_vault_tasks: {e}")
        import traceback

        traceback.print_exc()
        logger.error("sync_vault_tasks_failed", user_id=current_user.id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to sync vault tasks: {str(e)}")
