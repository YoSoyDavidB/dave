"""Task management use case."""

from datetime import datetime

import structlog
from sqlalchemy import and_, desc, select

from src.core.models import TaskModel
from src.domain.entities.task import Task, TaskPriority, TaskStatus
from src.infrastructure.database import async_session

logger = structlog.get_logger()


class TaskService:
    """Service for managing tasks."""

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Create a new task.

        Args:
            user_id: User creating the task
            title: Task title
            description: Task description
            priority: Task priority
            due_date: Optional due date
            tags: Optional tags for categorization

        Returns:
            Created Task
        """
        logger.info(
            "creating_task",
            user_id=user_id,
            title=title,
            priority=priority.value,
        )

        # Create task entity
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags or [],
        )

        # Save to database
        await self._save_task(task)

        return task

    async def get_task(self, task_id: str, user_id: str) -> Task | None:
        """Get a specific task.

        Args:
            task_id: Task ID
            user_id: User owning the task

        Returns:
            Task or None
        """
        async with async_session() as db_session:
            result = await db_session.execute(
                select(TaskModel).where(
                    and_(
                        TaskModel.id == task_id,
                        TaskModel.user_id == user_id,
                    )
                )
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return self._model_to_entity(model)

    async def get_all_tasks(
        self,
        user_id: str,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        limit: int = 100,
    ) -> list[Task]:
        """Get user's tasks with optional filtering.

        Args:
            user_id: User ID
            status: Optional status filter
            priority: Optional priority filter
            limit: Maximum number of tasks

        Returns:
            List of Tasks
        """
        async with async_session() as db_session:
            query = select(TaskModel).where(TaskModel.user_id == user_id)

            if status:
                query = query.where(TaskModel.status == status.value)

            if priority:
                query = query.where(TaskModel.priority == priority.value)

            query = query.order_by(desc(TaskModel.created_at)).limit(limit)

            result = await db_session.execute(query)
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

    async def get_pending_tasks(self, user_id: str) -> list[Task]:
        """Get user's pending and in-progress tasks.

        Args:
            user_id: User ID

        Returns:
            List of pending Tasks
        """
        async with async_session() as db_session:
            result = await db_session.execute(
                select(TaskModel)
                .where(
                    and_(
                        TaskModel.user_id == user_id,
                        TaskModel.status.in_(["pending", "in_progress"]),
                    )
                )
                .order_by(TaskModel.priority.desc(), TaskModel.due_date)
            )
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

    async def get_overdue_tasks(self, user_id: str) -> list[Task]:
        """Get user's overdue tasks.

        Args:
            user_id: User ID

        Returns:
            List of overdue Tasks
        """
        now = datetime.now()
        async with async_session() as db_session:
            result = await db_session.execute(
                select(TaskModel).where(
                    and_(
                        TaskModel.user_id == user_id,
                        TaskModel.status != "completed",
                        TaskModel.due_date < now,
                    )
                )
            )
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> Task:
        """Update a task.

        Args:
            task_id: Task to update
            user_id: User owning the task
            title: Optional new title
            description: Optional new description
            status: Optional new status
            priority: Optional new priority
            due_date: Optional new due date
            tags: Optional new tags

        Returns:
            Updated Task
        """
        task = await self.get_task(task_id, user_id)
        if not task:
            raise ValueError("Task not found")

        # Update fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
        if priority is not None:
            task.priority = priority
        if due_date is not None:
            task.due_date = due_date
        if tags is not None:
            task.tags = tags

        task.updated_at = datetime.now()

        await self._save_task(task)

        logger.info("task_updated", task_id=task_id, user_id=user_id)
        return task

    async def complete_task(self, task_id: str, user_id: str) -> Task:
        """Mark task as completed.

        Args:
            task_id: Task to complete
            user_id: User owning the task

        Returns:
            Completed Task
        """
        task = await self.get_task(task_id, user_id)
        if not task:
            raise ValueError("Task not found")

        task.complete()
        await self._save_task(task)

        logger.info("task_completed", task_id=task_id, user_id=user_id)
        return task

    async def cancel_task(self, task_id: str, user_id: str) -> Task:
        """Cancel a task.

        Args:
            task_id: Task to cancel
            user_id: User owning the task

        Returns:
            Cancelled Task
        """
        task = await self.get_task(task_id, user_id)
        if not task:
            raise ValueError("Task not found")

        task.cancel()
        await self._save_task(task)

        logger.info("task_cancelled", task_id=task_id, user_id=user_id)
        return task

    async def delete_task(self, task_id: str, user_id: str) -> None:
        """Delete a task permanently.

        Args:
            task_id: Task to delete
            user_id: User owning the task
        """
        async with async_session() as db_session:
            result = await db_session.execute(
                select(TaskModel).where(
                    and_(
                        TaskModel.id == task_id,
                        TaskModel.user_id == user_id,
                    )
                )
            )
            model = result.scalar_one_or_none()

            if model:
                await db_session.delete(model)
                await db_session.commit()
                logger.info("task_deleted", task_id=task_id, user_id=user_id)

    async def link_focus_session(
        self,
        task_id: str,
        user_id: str,
        focus_session_id: str,
    ) -> Task:
        """Link a focus session to a task.

        Args:
            task_id: Task ID
            user_id: User ID
            focus_session_id: Focus session ID to link

        Returns:
            Updated Task
        """
        task = await self.get_task(task_id, user_id)
        if not task:
            raise ValueError("Task not found")

        task.focus_session_id = focus_session_id
        task.updated_at = datetime.now()

        await self._save_task(task)

        logger.info(
            "task_focus_session_linked",
            task_id=task_id,
            focus_session_id=focus_session_id,
        )
        return task

    async def get_task_stats(self, user_id: str) -> dict:
        """Get user's task statistics.

        Args:
            user_id: User ID

        Returns:
            Dictionary with task stats
        """
        all_tasks = await self.get_all_tasks(user_id)

        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        pending_tasks = [t for t in all_tasks if t.status == TaskStatus.PENDING]
        in_progress_tasks = [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
        overdue = [t for t in all_tasks if t.is_overdue()]

        return {
            "total_tasks": len(all_tasks),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "in_progress_tasks": len(in_progress_tasks),
            "overdue_tasks": len(overdue),
            "completion_rate": (
                round((len(completed_tasks) / len(all_tasks)) * 100, 1) if all_tasks else 0
            ),
        }

    async def _save_task(self, task: Task) -> None:
        """Save task to database.

        Args:
            task: Task to save
        """
        async with async_session() as db_session:
            # Check if exists
            result = await db_session.execute(
                select(TaskModel).where(TaskModel.id == str(task.task_id))
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing
                existing.title = task.title
                existing.description = task.description
                existing.status = task.status.value
                existing.priority = task.priority.value
                existing.due_date = task.due_date
                existing.completed_at = task.completed_at
                existing.focus_session_id = task.focus_session_id
                existing.tags = task.tags
                existing.updated_at = datetime.now()
            else:
                # Create new
                new_task = TaskModel(
                    id=str(task.task_id),
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    status=task.status.value,
                    priority=task.priority.value,
                    due_date=task.due_date,
                    completed_at=task.completed_at,
                    focus_session_id=task.focus_session_id,
                    tags=task.tags,
                )
                db_session.add(new_task)

            await db_session.commit()

    def _model_to_entity(self, model: TaskModel) -> Task:
        """Convert database model to entity.

        Args:
            model: TaskModel

        Returns:
            Task entity
        """
        return Task(
            task_id=model.id,
            user_id=model.user_id,
            title=model.title,
            description=model.description,
            status=TaskStatus(model.status),
            priority=TaskPriority(model.priority),
            due_date=model.due_date,
            completed_at=model.completed_at,
            focus_session_id=model.focus_session_id,
            tags=model.tags,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Singleton
_task_service: TaskService | None = None


def get_task_service() -> TaskService:
    """Get or create task service singleton."""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
