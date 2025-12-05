"""Focus session management use case."""

from datetime import datetime

import structlog
from sqlalchemy import and_, desc, select

from src.core.models import FocusSessionModel
from src.domain.entities.focus_session import FocusSession, FocusSessionStatus, FocusSessionType
from src.infrastructure.database import async_session

logger = structlog.get_logger()


class FocusSessionService:
    """Service for managing focus sessions."""

    async def start_session(
        self,
        user_id: str,
        task_id: str | None = None,
        duration_minutes: int = 25,
        session_type: FocusSessionType = FocusSessionType.POMODORO,
    ) -> FocusSession:
        """Start a new focus session.

        Args:
            user_id: User starting the session
            task_id: Optional task ID to focus on
            duration_minutes: Session duration
            session_type: Type of focus session

        Returns:
            Created FocusSession
        """
        logger.info(
            "starting_focus_session",
            user_id=user_id,
            task_id=task_id,
            duration=duration_minutes,
        )

        # Create session entity
        session = FocusSession(
            user_id=user_id,
            task_id=task_id,
            duration_minutes=duration_minutes,
            session_type=session_type,
        )

        # Save to database
        await self._save_session(session)

        return session

    async def get_active_session(self, user_id: str) -> FocusSession | None:
        """Get user's active session if any.

        Args:
            user_id: User to check

        Returns:
            Active FocusSession or None
        """
        async with async_session() as db_session:
            result = await db_session.execute(
                select(FocusSessionModel).where(
                    and_(
                        FocusSessionModel.user_id == user_id,
                        FocusSessionModel.status.in_(["active", "paused"]),
                    )
                )
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return self._model_to_entity(model)

    async def pause_session(self, session_id: str, user_id: str) -> FocusSession:
        """Pause an active session.

        Args:
            session_id: Session to pause
            user_id: User owning the session

        Returns:
            Updated FocusSession
        """
        session = await self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        session.pause()
        await self._save_session(session)

        logger.info("focus_session_paused", session_id=session_id)
        return session

    async def resume_session(self, session_id: str, user_id: str) -> FocusSession:
        """Resume a paused session.

        Args:
            session_id: Session to resume
            user_id: User owning the session

        Returns:
            Updated FocusSession
        """
        session = await self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        session.resume()
        await self._save_session(session)

        logger.info("focus_session_resumed", session_id=session_id)
        return session

    async def complete_session(
        self,
        session_id: str,
        user_id: str,
        notes: str = "",
    ) -> FocusSession:
        """Complete a session.

        Args:
            session_id: Session to complete
            user_id: User owning the session
            notes: Optional notes about the session

        Returns:
            Completed FocusSession
        """
        session = await self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        session.complete()
        if notes:
            session.notes = notes

        await self._save_session(session)

        logger.info(
            "focus_session_completed",
            session_id=session_id,
            duration=session.duration_minutes,
            interruptions=session.interruptions,
        )
        return session

    async def cancel_session(self, session_id: str, user_id: str) -> FocusSession:
        """Cancel a session.

        Args:
            session_id: Session to cancel
            user_id: User owning the session

        Returns:
            Cancelled FocusSession
        """
        session = await self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Session not found")

        session.cancel()
        await self._save_session(session)

        logger.info("focus_session_cancelled", session_id=session_id)
        return session

    async def get_session(self, session_id: str, user_id: str) -> FocusSession | None:
        """Get a specific session.

        Args:
            session_id: Session ID
            user_id: User owning the session

        Returns:
            FocusSession or None
        """
        async with async_session() as db_session:
            result = await db_session.execute(
                select(FocusSessionModel).where(
                    and_(
                        FocusSessionModel.id == session_id,
                        FocusSessionModel.user_id == user_id,
                    )
                )
            )
            model = result.scalar_one_or_none()

            if not model:
                return None

            return self._model_to_entity(model)

    async def get_recent_sessions(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[FocusSession]:
        """Get user's recent sessions.

        Args:
            user_id: User ID
            limit: Maximum number of sessions

        Returns:
            List of recent FocusSessions
        """
        async with async_session() as db_session:
            result = await db_session.execute(
                select(FocusSessionModel)
                .where(FocusSessionModel.user_id == user_id)
                .order_by(desc(FocusSessionModel.created_at))
                .limit(limit)
            )
            models = result.scalars().all()

            return [self._model_to_entity(m) for m in models]

    async def get_session_stats(self, user_id: str) -> dict:
        """Get user's focus session statistics.

        Args:
            user_id: User ID

        Returns:
            Dictionary with session stats
        """
        sessions = await self.get_recent_sessions(user_id, limit=100)

        completed_sessions = [s for s in sessions if s.status == FocusSessionStatus.COMPLETED]
        total_focus_time = sum(s.duration_minutes for s in completed_sessions)
        avg_interruptions = (
            sum(s.interruptions for s in completed_sessions) / len(completed_sessions)
            if completed_sessions
            else 0
        )

        return {
            "total_sessions": len(sessions),
            "completed_sessions": len(completed_sessions),
            "total_focus_time_minutes": total_focus_time,
            "average_interruptions": round(avg_interruptions, 1),
        }

    async def _save_session(self, session: FocusSession) -> None:
        """Save session to database.

        Args:
            session: FocusSession to save
        """
        async with async_session() as db_session:
            # Check if exists
            result = await db_session.execute(
                select(FocusSessionModel).where(FocusSessionModel.id == str(session.session_id))
            )
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing
                existing.status = session.status.value
                existing.duration_minutes = session.duration_minutes
                existing.elapsed_seconds = session.elapsed_seconds
                existing.paused_at = session.paused_at
                existing.completed_at = session.completed_at
                existing.notes = session.notes
                existing.interruptions = session.interruptions
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                new_session = FocusSessionModel(
                    id=str(session.session_id),
                    user_id=session.user_id,
                    task_id=session.task_id,
                    session_type=session.session_type.value,
                    status=session.status.value,
                    duration_minutes=session.duration_minutes,
                    elapsed_seconds=session.elapsed_seconds,
                    started_at=session.started_at,
                    paused_at=session.paused_at,
                    completed_at=session.completed_at,
                    notes=session.notes,
                    interruptions=session.interruptions,
                )
                db_session.add(new_session)

            await db_session.commit()

    def _model_to_entity(self, model: FocusSessionModel) -> FocusSession:
        """Convert database model to entity.

        Args:
            model: FocusSessionModel

        Returns:
            FocusSession entity
        """
        return FocusSession(
            session_id=model.id,
            user_id=model.user_id,
            task_id=model.task_id,
            session_type=FocusSessionType(model.session_type),
            status=FocusSessionStatus(model.status),
            duration_minutes=model.duration_minutes,
            elapsed_seconds=model.elapsed_seconds,
            started_at=model.started_at,
            paused_at=model.paused_at,
            completed_at=model.completed_at,
            notes=model.notes,
            interruptions=model.interruptions,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Singleton
_focus_session_service: FocusSessionService | None = None


def get_focus_session_service() -> FocusSessionService:
    """Get or create focus session service singleton."""
    global _focus_session_service
    if _focus_session_service is None:
        _focus_session_service = FocusSessionService()
    return _focus_session_service
