"""Focus session API routes."""

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.application.use_cases.focus_sessions import get_focus_session_service
from src.domain.entities.focus_session import FocusSession, FocusSessionType

logger = structlog.get_logger()
router = APIRouter(prefix="/focus", tags=["focus"])


# ============================================
# Request/Response Models
# ============================================


class StartSessionRequest(BaseModel):
    """Request to start a focus session."""

    task_id: str | None = None
    duration_minutes: int = 25
    session_type: str = "pomodoro"


class SessionActionRequest(BaseModel):
    """Request for session actions (complete, cancel)."""

    notes: str = ""


class FocusSessionResponse(BaseModel):
    """Focus session response."""

    session_id: str
    user_id: str
    task_id: str | None
    session_type: str
    status: str
    duration_minutes: int
    elapsed_seconds: int
    remaining_seconds: int
    started_at: str
    paused_at: str | None
    completed_at: str | None
    notes: str
    interruptions: int
    created_at: str


class SessionStatsResponse(BaseModel):
    """Session statistics response."""

    total_sessions: int
    completed_sessions: int
    total_focus_time_minutes: int
    average_interruptions: float


# ============================================
# ENDPOINTS
# ============================================


@router.post("/start")
async def start_focus_session(user_id: str, request: StartSessionRequest) -> FocusSessionResponse:
    """Start a new focus session.

    Args:
        user_id: User starting the session
        request: Session configuration

    Returns:
        Created focus session
    """
    try:
        service = get_focus_session_service()

        # Check if user already has an active session
        active_session = await service.get_active_session(user_id)
        if active_session:
            raise HTTPException(
                status_code=400,
                detail="You already have an active focus session. Complete or cancel it first.",
            )

        session_type = FocusSessionType(request.session_type)
        session = await service.start_session(
            user_id=user_id,
            task_id=request.task_id,
            duration_minutes=request.duration_minutes,
            session_type=session_type,
        )

        return _entity_to_response(session)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(
            "start_session_value_error",
            user_id=user_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback

        error_detail = f"{type(e).__name__}: {str(e)}"
        logger.error(
            "start_session_failed",
            user_id=user_id,
            error=error_detail,
            traceback=traceback.format_exc(),
        )
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/active")
async def get_active_session(user_id: str) -> FocusSessionResponse | None:
    """Get user's active session if any.

    Args:
        user_id: User ID

    Returns:
        Active session or null
    """
    try:
        service = get_focus_session_service()
        session = await service.get_active_session(user_id)

        if not session:
            return None

        return _entity_to_response(session)

    except Exception as e:
        logger.error("get_active_session_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/pause")
async def pause_session(session_id: str, user_id: str) -> FocusSessionResponse:
    """Pause an active session.

    Args:
        session_id: Session to pause
        user_id: User ID

    Returns:
        Updated session
    """
    try:
        service = get_focus_session_service()
        session = await service.pause_session(session_id, user_id)
        return _entity_to_response(session)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("pause_session_failed", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/resume")
async def resume_session(session_id: str, user_id: str) -> FocusSessionResponse:
    """Resume a paused session.

    Args:
        session_id: Session to resume
        user_id: User ID

    Returns:
        Updated session
    """
    try:
        service = get_focus_session_service()
        session = await service.resume_session(session_id, user_id)
        return _entity_to_response(session)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("resume_session_failed", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/complete")
async def complete_session(
    session_id: str,
    user_id: str,
    request: SessionActionRequest,
) -> FocusSessionResponse:
    """Complete a session.

    Args:
        session_id: Session to complete
        user_id: User ID
        request: Completion data (notes)

    Returns:
        Completed session
    """
    try:
        service = get_focus_session_service()
        session = await service.complete_session(session_id, user_id, request.notes)
        return _entity_to_response(session)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("complete_session_failed", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/cancel")
async def cancel_session(session_id: str, user_id: str) -> FocusSessionResponse:
    """Cancel a session.

    Args:
        session_id: Session to cancel
        user_id: User ID

    Returns:
        Cancelled session
    """
    try:
        service = get_focus_session_service()
        session = await service.cancel_session(session_id, user_id)
        return _entity_to_response(session)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("cancel_session_failed", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_session_history(user_id: str, limit: int = 10) -> list[FocusSessionResponse]:
    """Get user's session history.

    Args:
        user_id: User ID
        limit: Maximum number of sessions (default 10)

    Returns:
        List of recent sessions
    """
    try:
        service = get_focus_session_service()
        sessions = await service.get_recent_sessions(user_id, limit)
        return [_entity_to_response(s) for s in sessions]

    except Exception as e:
        logger.error("get_history_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_session_stats(user_id: str) -> SessionStatsResponse:
    """Get user's focus session statistics.

    Args:
        user_id: User ID

    Returns:
        Session statistics
    """
    try:
        service = get_focus_session_service()
        stats = await service.get_session_stats(user_id)
        return SessionStatsResponse(**stats)

    except Exception as e:
        logger.error("get_stats_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Helper Functions
# ============================================


def _entity_to_response(entity: FocusSession) -> FocusSessionResponse:
    """Convert entity to response model.

    Args:
        entity: FocusSession entity

    Returns:
        FocusSessionResponse
    """
    return FocusSessionResponse(
        session_id=str(entity.session_id),
        user_id=entity.user_id,
        task_id=entity.task_id,
        session_type=entity.session_type.value,
        status=entity.status.value,
        duration_minutes=entity.duration_minutes,
        elapsed_seconds=entity.elapsed_seconds,
        remaining_seconds=entity.get_remaining_seconds(),
        started_at=entity.started_at.isoformat(),
        paused_at=entity.paused_at.isoformat() if entity.paused_at else None,
        completed_at=entity.completed_at.isoformat() if entity.completed_at else None,
        notes=entity.notes,
        interruptions=entity.interruptions,
        created_at=entity.created_at.isoformat(),
    )
