"""Background scheduler for proactive features."""


import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.application.use_cases.proactive import get_proactive_service

logger = structlog.get_logger()


class BackgroundScheduler:
    """Background scheduler for periodic tasks."""

    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._proactive = get_proactive_service()

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

        self._scheduler.start()
        logger.info("scheduler_started")

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
