from datetime import datetime, timedelta
from typing import Any

import structlog
from sqlalchemy import func, select

from src.core.models import EnglishCorrection
from src.infrastructure.database import async_session

logger = structlog.get_logger()


async def log_correction(
    original_text: str,
    corrected_text: str,
    explanation: str,
    category: str,
    subcategory: str | None = None,
    context: str | None = None,
) -> EnglishCorrection | None:
    """Log a new English correction."""
    try:
        async with async_session() as session:
            correction = EnglishCorrection(
                original_text=original_text,
                corrected_text=corrected_text,
                explanation=explanation,
                category=category,
                subcategory=subcategory,
                conversation_context=context,
            )
            session.add(correction)
            await session.commit()
            await session.refresh(correction)
            return correction
    except Exception as e:
        logger.error("failed_to_log_correction", error=str(e))
        return None


async def get_recent_corrections(days: int = 7, limit: int = 20) -> list[EnglishCorrection]:
    """Get recent corrections."""
    try:
        async with async_session() as session:
            since = datetime.utcnow() - timedelta(days=days)
            result = await session.execute(
                select(EnglishCorrection)
                .where(EnglishCorrection.created_at >= since)
                .order_by(EnglishCorrection.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
    except Exception as e:
        logger.error("failed_to_get_corrections", error=str(e))
        return []


async def get_corrections_by_category(
    category: str, limit: int = 20
) -> list[EnglishCorrection]:
    """Get corrections by category."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(EnglishCorrection)
                .where(EnglishCorrection.category == category)
                .order_by(EnglishCorrection.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
    except Exception as e:
        logger.error("failed_to_get_corrections_by_category", error=str(e))
        return []


async def get_error_stats() -> dict[str, Any]:
    """Get statistics about errors."""
    try:
        async with async_session() as session:
            # Total corrections
            total_result = await session.execute(
                select(func.count(EnglishCorrection.id))
            )
            total = total_result.scalar() or 0

            # By category
            category_result = await session.execute(
                select(EnglishCorrection.category, func.count(EnglishCorrection.id))
                .group_by(EnglishCorrection.category)
            )
            by_category = {row[0]: row[1] for row in category_result.all()}

            # Last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            week_result = await session.execute(
                select(func.count(EnglishCorrection.id))
                .where(EnglishCorrection.created_at >= week_ago)
            )
            last_week = week_result.scalar() or 0

            return {
                "total_corrections": total,
                "by_category": by_category,
                "last_7_days": last_week,
            }
    except Exception as e:
        logger.error("failed_to_get_error_stats", error=str(e))
        return {"total_corrections": 0, "by_category": {}, "last_7_days": 0}
