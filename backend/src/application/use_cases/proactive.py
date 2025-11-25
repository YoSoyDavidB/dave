"""Proactive features use case - reminders, suggestions, progress tracking."""

from dataclasses import dataclass
from datetime import UTC, datetime

import structlog

from src.domain.entities.memory import Memory, MemoryType
from src.infrastructure.vector_store.memory_repository import get_memory_repository

logger = structlog.get_logger()


@dataclass
class Reminder:
    """A reminder for a pending task."""

    memory_id: str
    user_id: str
    task_text: str
    due_date: datetime
    is_overdue: bool
    hours_until_due: float


class ProactiveService:
    """Service for proactive features like reminders and suggestions."""

    def __init__(self):
        self._memory_repo = get_memory_repository()

    async def get_pending_reminders(self, user_id: str) -> list[Reminder]:
        """Get all pending task reminders for a user.

        Args:
            user_id: User to get reminders for

        Returns:
            List of reminders for tasks due soon or overdue
        """
        try:
            # Get all TASK memories for user
            tasks = await self._memory_repo.get_by_type(
                user_id=user_id,
                memory_type=MemoryType.TASK,
            )

            reminders: list[Reminder] = []
            now = datetime.now(UTC)

            for task in tasks:
                if task.needs_reminder():
                    time_diff = task.due_date - now if task.due_date else None
                    hours_until = time_diff.total_seconds() / 3600 if time_diff else 0

                    reminders.append(
                        Reminder(
                            memory_id=str(task.memory_id),
                            user_id=task.user_id,
                            task_text=task.short_text,
                            due_date=task.due_date,  # type: ignore
                            is_overdue=hours_until < 0,
                            hours_until_due=hours_until,
                        )
                    )

                    # Mark as reminded so we don't send again
                    task.mark_reminded()
                    await self._memory_repo.update(task)

            logger.info(
                "reminders_generated",
                user_id=user_id,
                count=len(reminders),
            )

            return reminders

        except Exception as e:
            logger.error("get_reminders_failed", user_id=user_id, error=str(e))
            return []

    async def mark_task_completed(self, memory_id: str, user_id: str) -> bool:
        """Mark a task as completed.

        Args:
            memory_id: Memory ID of the task
            user_id: User who owns the task

        Returns:
            True if task was marked completed
        """
        try:
            memory = await self._memory_repo.get_by_id(memory_id)
            if not memory or memory.user_id != user_id:
                return False

            if memory.memory_type != MemoryType.TASK:
                return False

            memory.mark_completed()
            await self._memory_repo.update(memory)

            logger.info(
                "task_marked_completed",
                memory_id=memory_id,
                user_id=user_id,
            )

            return True

        except Exception as e:
            logger.error(
                "mark_completed_failed",
                memory_id=memory_id,
                error=str(e),
            )
            return False

    async def get_active_goals(self, user_id: str) -> list[Memory]:
        """Get all active goals with progress tracking.

        Args:
            user_id: User to get goals for

        Returns:
            List of goal memories with progress
        """
        try:
            goals = await self._memory_repo.get_by_type(
                user_id=user_id,
                memory_type=MemoryType.GOAL,
            )

            # Filter to only active goals (not completed)
            active_goals = [g for g in goals if g.progress < 100.0]

            return active_goals

        except Exception as e:
            logger.error("get_goals_failed", user_id=user_id, error=str(e))
            return []

    async def get_all_pending_tasks(self, user_id: str) -> list[Memory]:
        """Get all pending tasks (completed=False) regardless of due date.

        Args:
            user_id: User to get tasks for

        Returns:
            List of all pending task memories
        """
        try:
            tasks = await self._memory_repo.get_by_type(
                user_id=user_id,
                memory_type=MemoryType.TASK,
            )

            # Filter to only non-completed tasks
            pending_tasks = [t for t in tasks if not t.completed]

            logger.info(
                "pending_tasks_retrieved",
                user_id=user_id,
                count=len(pending_tasks),
            )

            return pending_tasks

        except Exception as e:
            logger.error("get_pending_tasks_failed", user_id=user_id, error=str(e))
            return []


# Singleton instance
_proactive_service: ProactiveService | None = None


def get_proactive_service() -> ProactiveService:
    """Get the singleton proactive service."""
    global _proactive_service
    if _proactive_service is None:
        _proactive_service = ProactiveService()
    return _proactive_service
