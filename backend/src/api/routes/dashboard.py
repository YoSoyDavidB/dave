"""Dashboard API routes - insights, summaries, and stats."""

from datetime import date, timedelta

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, desc, select

from src.application.use_cases.insights import get_insights_service
from src.core.models import DailySummaryModel
from src.infrastructure.database import async_session

logger = structlog.get_logger()
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ============================================
# Response Models
# ============================================


class DailySummaryResponse(BaseModel):
    """Daily summary response."""

    summary_id: str
    user_id: str
    date: str
    tasks_completed: int
    tasks_created: int
    tasks_pending: int
    goals_updated: list[str]
    goals_progress_delta: float
    conversations_count: int
    messages_sent: int
    english_corrections: int
    productivity_score: float
    top_topics: list[str]
    key_achievements: list[str]
    suggestions: list[str]
    summary_text: str
    created_at: str


class DashboardStatsResponse(BaseModel):
    """Comprehensive dashboard statistics."""

    # Today's summary
    today_summary: DailySummaryResponse | None

    # Week overview
    week_productivity_avg: float
    week_tasks_completed: int
    week_conversations: int

    # Trends
    productivity_trend: list[dict]  # [{date, score}, ...]
    tasks_trend: list[dict]  # [{date, completed, created}, ...]


# ============================================
# ENDPOINTS
# ============================================


@router.get("/summary/today")
async def get_today_summary(user_id: str) -> DailySummaryResponse | None:
    """Get today's daily summary for a user.

    If summary doesn't exist yet, it will be generated.
    """
    try:
        today = date.today()

        # Try to fetch existing summary
        async with async_session() as session:
            result = await session.execute(
                select(DailySummaryModel).where(
                    and_(
                        DailySummaryModel.user_id == user_id,
                        DailySummaryModel.date == today,
                    )
                )
            )
            summary_model = result.scalar_one_or_none()

            if summary_model:
                return _model_to_response(summary_model)

        # Generate new summary if doesn't exist
        insights_service = get_insights_service()
        summary = await insights_service.generate_daily_summary(user_id, today)

        # Save to database
        await _save_summary(summary)

        return _entity_to_response(summary)

    except Exception as e:
        logger.error("get_today_summary_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{date_str}")
async def get_summary_by_date(user_id: str, date_str: str) -> DailySummaryResponse | None:
    """Get daily summary for a specific date."""
    try:
        target_date = date.fromisoformat(date_str)

        async with async_session() as session:
            result = await session.execute(
                select(DailySummaryModel).where(
                    and_(
                        DailySummaryModel.user_id == user_id,
                        DailySummaryModel.date == target_date,
                    )
                )
            )
            summary_model = result.scalar_one_or_none()

            if not summary_model:
                raise HTTPException(status_code=404, detail="Summary not found")

            return _model_to_response(summary_model)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_summary_by_date_failed", date=date_str, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/week")
async def get_week_summaries(user_id: str) -> list[DailySummaryResponse]:
    """Get daily summaries for the past 7 days."""
    try:
        today = date.today()
        week_ago = today - timedelta(days=7)

        async with async_session() as session:
            result = await session.execute(
                select(DailySummaryModel)
                .where(
                    and_(
                        DailySummaryModel.user_id == user_id,
                        DailySummaryModel.date >= week_ago,
                        DailySummaryModel.date <= today,
                    )
                )
                .order_by(desc(DailySummaryModel.date))
            )
            summaries = result.scalars().all()

            return [_model_to_response(s) for s in summaries]

    except Exception as e:
        logger.error("get_week_summaries_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_dashboard_stats(user_id: str) -> DashboardStatsResponse:
    """Get comprehensive dashboard statistics."""
    try:
        today = date.today()
        week_ago = today - timedelta(days=7)

        async with async_session() as session:
            # Get today's summary
            today_result = await session.execute(
                select(DailySummaryModel).where(
                    and_(
                        DailySummaryModel.user_id == user_id,
                        DailySummaryModel.date == today,
                    )
                )
            )
            today_summary = today_result.scalar_one_or_none()

            # Get week summaries for trends
            week_result = await session.execute(
                select(DailySummaryModel)
                .where(
                    and_(
                        DailySummaryModel.user_id == user_id,
                        DailySummaryModel.date >= week_ago,
                        DailySummaryModel.date <= today,
                    )
                )
                .order_by(DailySummaryModel.date)
            )
            week_summaries = week_result.scalars().all()

            # Calculate week averages
            week_productivity_avg = 0.0
            week_tasks_completed = 0
            week_conversations = 0

            if week_summaries:
                week_productivity_avg = sum(s.productivity_score for s in week_summaries) / len(
                    week_summaries
                )
                week_tasks_completed = sum(s.tasks_completed for s in week_summaries)
                week_conversations = sum(s.conversations_count for s in week_summaries)

            # Build trends
            productivity_trend = [
                {"date": s.date.isoformat(), "score": s.productivity_score} for s in week_summaries
            ]

            tasks_trend = [
                {
                    "date": s.date.isoformat(),
                    "completed": s.tasks_completed,
                    "created": s.tasks_created,
                }
                for s in week_summaries
            ]

            return DashboardStatsResponse(
                today_summary=_model_to_response(today_summary) if today_summary else None,
                week_productivity_avg=round(week_productivity_avg, 1),
                week_tasks_completed=week_tasks_completed,
                week_conversations=week_conversations,
                productivity_trend=productivity_trend,
                tasks_trend=tasks_trend,
            )

    except Exception as e:
        logger.error("get_dashboard_stats_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary/generate")
async def generate_summary(user_id: str, date_str: str | None = None) -> DailySummaryResponse:
    """Manually trigger summary generation for a specific date."""
    try:
        target_date = date.fromisoformat(date_str) if date_str else date.today()

        insights_service = get_insights_service()
        summary = await insights_service.generate_daily_summary(user_id, target_date)

        # Save to database
        await _save_summary(summary)

        return _entity_to_response(summary)

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        logger.error("generate_summary_failed", date=date_str, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Helper Functions
# ============================================


def _model_to_response(model: DailySummaryModel) -> DailySummaryResponse:
    """Convert SQLAlchemy model to Pydantic response."""
    return DailySummaryResponse(
        summary_id=model.id,
        user_id=model.user_id,
        date=model.date.isoformat(),
        tasks_completed=model.tasks_completed,
        tasks_created=model.tasks_created,
        tasks_pending=model.tasks_pending,
        goals_updated=model.goals_updated,
        goals_progress_delta=model.goals_progress_delta,
        conversations_count=model.conversations_count,
        messages_sent=model.messages_sent,
        english_corrections=model.english_corrections,
        productivity_score=model.productivity_score,
        top_topics=model.top_topics,
        key_achievements=model.key_achievements,
        suggestions=model.suggestions,
        summary_text=model.summary_text,
        created_at=model.created_at.isoformat(),
    )


def _entity_to_response(entity) -> DailySummaryResponse:
    """Convert domain entity to Pydantic response."""
    return DailySummaryResponse(
        summary_id=str(entity.summary_id),
        user_id=entity.user_id,
        date=entity.date.isoformat(),
        tasks_completed=entity.tasks_completed,
        tasks_created=entity.tasks_created,
        tasks_pending=entity.tasks_pending,
        goals_updated=entity.goals_updated,
        goals_progress_delta=entity.goals_progress_delta,
        conversations_count=entity.conversations_count,
        messages_sent=entity.messages_sent,
        english_corrections=entity.english_corrections,
        productivity_score=entity.productivity_score,
        top_topics=entity.top_topics,
        key_achievements=entity.key_achievements,
        suggestions=entity.suggestions,
        summary_text=entity.summary_text,
        created_at=entity.created_at.isoformat(),
    )


async def _save_summary(summary) -> None:
    """Save daily summary entity to database."""
    async with async_session() as session:
        # Check if already exists
        result = await session.execute(
            select(DailySummaryModel).where(
                and_(
                    DailySummaryModel.user_id == summary.user_id,
                    DailySummaryModel.date == summary.date,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing
            existing.tasks_completed = summary.tasks_completed
            existing.tasks_created = summary.tasks_created
            existing.tasks_pending = summary.tasks_pending
            existing.goals_updated = summary.goals_updated
            existing.goals_progress_delta = summary.goals_progress_delta
            existing.conversations_count = summary.conversations_count
            existing.messages_sent = summary.messages_sent
            existing.english_corrections = summary.english_corrections
            existing.productivity_score = summary.productivity_score
            existing.top_topics = summary.top_topics
            existing.key_achievements = summary.key_achievements
            existing.suggestions = summary.suggestions
            existing.summary_text = summary.summary_text
        else:
            # Create new
            new_summary = DailySummaryModel(
                id=str(summary.summary_id),
                user_id=summary.user_id,
                date=summary.date,
                tasks_completed=summary.tasks_completed,
                tasks_created=summary.tasks_created,
                tasks_pending=summary.tasks_pending,
                goals_updated=summary.goals_updated,
                goals_progress_delta=summary.goals_progress_delta,
                conversations_count=summary.conversations_count,
                messages_sent=summary.messages_sent,
                english_corrections=summary.english_corrections,
                productivity_score=summary.productivity_score,
                top_topics=summary.top_topics,
                key_achievements=summary.key_achievements,
                suggestions=summary.suggestions,
                summary_text=summary.summary_text,
            )
            session.add(new_summary)

        await session.commit()
