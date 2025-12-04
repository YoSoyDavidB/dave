"""Daily insights and summary generation use case."""

from datetime import UTC, date, datetime

import structlog
from sqlalchemy import and_, func, select

from src.core.models import Conversation, EnglishCorrection
from src.domain.entities.daily_summary import DailySummary
from src.domain.entities.memory import MemoryType
from src.infrastructure.database import async_session
from src.infrastructure.embeddings.embedding_service import get_embedding_service
from src.infrastructure.openrouter import get_openrouter_client
from src.infrastructure.vector_store.memory_repository import get_memory_repository

logger = structlog.get_logger()


class InsightsService:
    """Service for generating daily/weekly insights and summaries."""

    def __init__(self):
        self._memory_repo = get_memory_repository()
        self._embeddings = get_embedding_service()
        self._llm = get_openrouter_client()

    async def generate_daily_summary(
        self,
        user_id: str,
        target_date: date | None = None,
    ) -> DailySummary:
        """Generate comprehensive daily summary for a user.

        Args:
            user_id: User to generate summary for
            target_date: Date to generate summary for (defaults to today)

        Returns:
            DailySummary with metrics and AI-generated insights
        """
        if target_date is None:
            target_date = date.today()

        logger.info("generating_daily_summary", user_id=user_id, date=target_date.isoformat())

        summary = DailySummary(user_id=user_id, date=target_date)

        # Gather metrics in parallel
        try:
            # Task metrics
            await self._gather_task_metrics(summary, user_id, target_date)

            # Goal metrics
            await self._gather_goal_metrics(summary, user_id, target_date)

            # Conversation metrics
            await self._gather_conversation_metrics(summary, user_id, target_date)

            # English learning metrics
            await self._gather_english_metrics(summary, user_id, target_date)

            # Calculate productivity score
            summary.calculate_productivity_score()

            # Generate AI insights
            await self._generate_ai_insights(summary, user_id, target_date)

            logger.info(
                "daily_summary_generated",
                user_id=user_id,
                date=target_date.isoformat(),
                productivity_score=summary.productivity_score,
            )

            return summary

        except Exception as e:
            logger.error("daily_summary_generation_failed", user_id=user_id, error=str(e))
            # Return partial summary even if some parts failed
            return summary

    async def _gather_task_metrics(
        self,
        summary: DailySummary,
        user_id: str,
        target_date: date,
    ) -> None:
        """Gather task-related metrics for the day."""
        try:
            # Get all TASK memories for user
            tasks = await self._memory_repo.get_by_type(
                user_id=user_id,
                memory_type=MemoryType.TASK,
            )

            start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=UTC)
            end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=UTC)

            for task in tasks:
                # Tasks created today
                if start_of_day <= task.timestamp <= end_of_day:
                    summary.tasks_created += 1

                # Tasks completed today
                if task.completed and task.last_referenced_at:
                    if start_of_day <= task.last_referenced_at <= end_of_day:
                        summary.tasks_completed += 1

                # Tasks still pending
                if not task.completed:
                    summary.tasks_pending += 1

        except Exception as e:
            logger.error("task_metrics_failed", error=str(e))

    async def _gather_goal_metrics(
        self,
        summary: DailySummary,
        user_id: str,
        target_date: date,
    ) -> None:
        """Gather goal-related metrics for the day."""
        try:
            goals = await self._memory_repo.get_by_type(
                user_id=user_id,
                memory_type=MemoryType.GOAL,
            )

            start_of_day = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=UTC)
            end_of_day = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=UTC)

            for goal in goals:
                # Goals updated today
                if start_of_day <= goal.last_referenced_at <= end_of_day:
                    summary.goals_updated.append(goal.short_text)

                    # Track progress delta (assuming progress field exists)
                    if hasattr(goal, "progress") and goal.progress > 0:
                        # Simplified: assume progress was added today
                        # In real implementation, track previous progress
                        summary.goals_progress_delta += goal.progress

        except Exception as e:
            logger.error("goal_metrics_failed", error=str(e))

    async def _gather_conversation_metrics(
        self,
        summary: DailySummary,
        user_id: str,
        target_date: date,
    ) -> None:
        """Gather conversation-related metrics for the day."""
        try:
            async with async_session() as session:
                start_of_day = datetime.combine(target_date, datetime.min.time())
                end_of_day = datetime.combine(target_date, datetime.max.time())

                # Count conversations
                result = await session.execute(
                    select(func.count(Conversation.id)).where(
                        and_(
                            Conversation.user_id == user_id,
                            Conversation.created_at >= start_of_day,
                            Conversation.created_at <= end_of_day,
                        )
                    )
                )
                summary.conversations_count = result.scalar() or 0

                # Count messages (approximation: each conversation has ~5 messages)
                # TODO: Track actual message count if needed
                summary.messages_sent = summary.conversations_count * 5

        except Exception as e:
            logger.error("conversation_metrics_failed", error=str(e))

    async def _gather_english_metrics(
        self,
        summary: DailySummary,
        user_id: str,
        target_date: date,
    ) -> None:
        """Gather English learning metrics for the day."""
        try:
            async with async_session() as session:
                start_of_day = datetime.combine(target_date, datetime.min.time())
                end_of_day = datetime.combine(target_date, datetime.max.time())

                result = await session.execute(
                    select(func.count(EnglishCorrection.id)).where(
                        and_(
                            EnglishCorrection.user_id == user_id,
                            EnglishCorrection.created_at >= start_of_day,
                            EnglishCorrection.created_at <= end_of_day,
                        )
                    )
                )
                summary.english_corrections = result.scalar() or 0

        except Exception as e:
            logger.error("english_metrics_failed", error=str(e))

    async def _generate_ai_insights(
        self,
        summary: DailySummary,
        user_id: str,
        target_date: date,
    ) -> None:
        """Use LLM to generate insights, achievements, and suggestions."""
        try:
            # Build context for LLM
            context = self._build_context_for_llm(summary)

            prompt = f"""You are Dave, an AI productivity assistant. Generate a daily \
summary and insights for the user.

**User's Activity on {target_date.strftime('%B %d, %Y')}:**

{context}

Based on this activity, provide:

1. **Top 3 Topics**: What were the main topics or themes discussed/worked on?
2. **Key Achievements**: What did the user accomplish today? (2-3 items)
3. **Suggestions**: What should the user focus on next? (3-4 actionable suggestions)
4. **Summary**: A brief, friendly 2-3 sentence summary of the day

Format your response as JSON:
{{
    "top_topics": ["topic1", "topic2", "topic3"],
    "key_achievements": ["achievement1", "achievement2"],
    "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
    "summary_text": "Your day summary here..."
}}

Be encouraging and specific. If the user had a productive day, celebrate it. \
If not, be supportive and suggest concrete next steps."""

            response = await self._llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="anthropic/claude-3.5-sonnet",
                temperature=0.7,
            )

            # Parse JSON response
            import json

            insights = json.loads(response)

            summary.top_topics = insights.get("top_topics", [])[:3]
            summary.key_achievements = insights.get("key_achievements", [])[:3]
            summary.suggestions = insights.get("suggestions", [])[:4]
            summary.summary_text = insights.get("summary_text", "")

        except Exception as e:
            logger.error("ai_insights_generation_failed", error=str(e))
            # Fallback to basic summary
            summary.summary_text = self._generate_fallback_summary(summary)

    def _build_context_for_llm(self, summary: DailySummary) -> str:
        """Build context string for LLM prompt."""
        lines = []

        lines.append("**Tasks:**")
        lines.append(f"- Completed: {summary.tasks_completed}")
        lines.append(f"- Created: {summary.tasks_created}")
        lines.append(f"- Still pending: {summary.tasks_pending}")

        if summary.goals_updated:
            lines.append("\n**Goals Worked On:**")
            for goal in summary.goals_updated[:5]:
                lines.append(f"- {goal}")

        lines.append("\n**Activity:**")
        lines.append(f"- Conversations: {summary.conversations_count}")
        lines.append(f"- English corrections: {summary.english_corrections}")
        lines.append(f"- Productivity score: {summary.productivity_score}/100")

        return "\n".join(lines)

    def _generate_fallback_summary(self, summary: DailySummary) -> str:
        """Generate simple summary if LLM fails."""
        if summary.tasks_completed > 0:
            return (
                f"You completed {summary.tasks_completed} task(s) today "
                f"with a productivity score of {summary.productivity_score}. Keep it up!"
            )
        return "Your day summary is being prepared. Check back soon!"


# Singleton
_insights_service: InsightsService | None = None


def get_insights_service() -> InsightsService:
    """Get or create insights service singleton."""
    global _insights_service
    if _insights_service is None:
        _insights_service = InsightsService()
    return _insights_service
