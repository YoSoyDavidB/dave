"""Background scheduler for proactive features."""

from datetime import date

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from src.application.use_cases.insights import get_insights_service
from src.application.use_cases.proactive import get_proactive_service
from src.core.models import User
from src.infrastructure.database import async_session

logger = structlog.get_logger()


class BackgroundScheduler:
    """Background scheduler for periodic tasks."""

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._proactive = get_proactive_service()
        self._insights = get_insights_service()

    async def check_reminders(self) -> None:
        """Check and log pending reminders for all users.

        This is a periodic task that runs every hour to check for
        tasks that need reminders.

        Note: For now, reminders are checked on-demand via the API endpoint.
        This background task is a placeholder for future push notifications.
        """
        try:
            logger.debug("reminder_check_job_executed")

            # Future implementation will:
            # - Query all users from database
            # - Check pending reminders for each user
            # - Send email/push notifications
            # - Store notifications in database for UI

        except Exception as e:
            logger.error("reminder_check_failed", error=str(e))

    async def generate_daily_summaries(self) -> None:
        """Generate daily summaries for all users.

        This runs every night at 23:00 to generate summaries for the current day.
        Users can then see their daily insights first thing in the morning.
        """
        try:
            logger.info("daily_summary_job_started")

            # Get all active users
            async with async_session() as session:
                result = await session.execute(select(User).where(User.is_active.is_(True)))
                users = result.scalars().all()

            if not users:
                logger.info("no_active_users_found")
                return

            # Generate summary for each user
            today = date.today()
            successful = 0
            failed = 0

            for user in users:
                try:
                    summary = await self._insights.generate_daily_summary(user.id, today)

                    # Save to database
                    from src.api.routes.dashboard import _save_summary

                    await _save_summary(summary)

                    successful += 1
                    logger.info(
                        "daily_summary_generated",
                        user_id=user.id,
                        date=today.isoformat(),
                        productivity_score=summary.productivity_score,
                    )

                except Exception as e:
                    failed += 1
                    logger.error("daily_summary_failed_for_user", user_id=user.id, error=str(e))

            logger.info(
                "daily_summary_job_completed",
                successful=successful,
                failed=failed,
                total_users=len(users),
            )

        except Exception as e:
            logger.error("daily_summary_job_failed", error=str(e))

    def start(self) -> None:
        """Start the background scheduler."""
        # Check reminders every hour
        self._scheduler.add_job(
            self.check_reminders,
            trigger=IntervalTrigger(hours=1),
            id="check_reminders",
            name="Check pending task reminders",
            replace_existing=True,
        )

        # Generate daily summaries every night at 23:00 (11 PM)
        self._scheduler.add_job(
            self.generate_daily_summaries,
            trigger=CronTrigger(hour=23, minute=0),
            id="generate_daily_summaries",
            name="Generate daily summaries for all users",
            replace_existing=True,
        )

        self._scheduler.start()
        logger.info("scheduler_started", jobs=["check_reminders", "generate_daily_summaries"])

    def shutdown(self) -> None:
        """Shutdown the scheduler."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("scheduler_stopped")


# Singleton instance
_scheduler: BackgroundScheduler | None = None


def get_scheduler() -> BackgroundScheduler:
    """Get the singleton scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler
