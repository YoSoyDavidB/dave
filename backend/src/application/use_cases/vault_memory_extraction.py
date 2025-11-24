"""Extract memories and tasks from vault notes."""

import re
from datetime import datetime
from typing import Any

import httpx
import structlog

from src.config import get_settings
from src.domain.entities.memory import Memory, MemoryType
from src.infrastructure.github_vault import get_github_vault_client
from src.infrastructure.vector_store.memory_repository import get_memory_repository

logger = structlog.get_logger()

# Prompt for extracting tasks from markdown notes
VAULT_EXTRACTION_PROMPT = """Analyze this daily note and extract any tasks or goals mentioned.

Look for:
1. **Tasks**: Things to do, action items, checkboxes (- [ ])
2. **Goals**: Long-term objectives mentioned
3. **Due dates**: Any mentioned deadlines or time references

Return a JSON array of items. Each item should have:
- "text": A concise statement about the task/goal in third person
- "type": Either "task" or "goal"
- "due_date": (Optional) ISO format datetime if a deadline is mentioned
- "confidence": How confident you are (0.0-1.0)

Important:
- Convert relative dates like "tomorrow", "next week" to absolute dates based on
  note date: {note_date}
- Only include actionable items
- Ignore completed tasks (- [x])
- Return empty array [] if nothing found

Example output:
[
  {{"text": "Needs to review project documentation", "type": "task",
    "due_date": "2025-11-25T23:59:59Z", "confidence": 0.9}},
  {{"text": "Wants to improve Python skills", "type": "goal", "confidence": 0.85}}
]

Daily Note Content:
{content}

Return ONLY the JSON array, no other text."""


class VaultMemoryExtraction:
    """Extract tasks and memories from vault notes."""

    def __init__(self):
        self._settings = get_settings()
        self._vault_client = get_github_vault_client()
        self._memory_repo = get_memory_repository()
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                base_url=self._settings.openrouter_base_url,
                headers={
                    "Authorization": f"Bearer {self._settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._http_client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    def _extract_note_date(self, path: str, content: str) -> datetime:
        """Extract date from daily note path or frontmatter.

        Supports formats like:
        - Daily Notes/2025-11-24.md
        - Daily/2025/11/24.md
        - Timestamps/2025/11-November/2025-11-22-Saturday.md
        - Frontmatter: date: 2025-11-24
        """
        # Try to extract from path (YYYY-MM-DD format, possibly with day name)
        # Matches: 2025-11-22 or 2025-11-22-Saturday
        date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})(?:-\w+)?", path)
        if date_match:
            year, month, day = map(int, date_match.groups())
            return datetime(year, month, day)

        # Try to extract from frontmatter
        frontmatter_match = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
        if frontmatter_match:
            date_str = frontmatter_match.group(1)
            return datetime.fromisoformat(date_str)

        # Default to today
        return datetime.utcnow()

    async def extract_from_daily_note(
        self,
        path: str,
        user_id: str,
    ) -> list[Memory]:
        """Extract tasks and goals from a daily note.

        Args:
            path: Path to the daily note in vault
            user_id: User who owns the note

        Returns:
            List of extracted memories (tasks/goals)
        """
        try:
            # Get note content
            file_data = await self._vault_client.get_file(path)
            if not file_data:
                logger.warning("vault_note_not_found", path=path)
                return []

            content = file_data["content"]

            # Extract note date
            note_date = self._extract_note_date(path, content)

            # Skip if note is too old (more than 7 days)
            days_old = (datetime.utcnow() - note_date).days
            if days_old > 7:
                logger.debug("vault_note_too_old", path=path, days_old=days_old)
                return []

            # Call LLM to extract tasks/goals
            raw_items = await self._call_extraction_llm(content, note_date)

            if not raw_items:
                logger.debug("no_tasks_found_in_note", path=path)
                return []

            # Convert to Memory objects
            memories = []
            for raw in raw_items:
                try:
                    memory_type = MemoryType.TASK if raw["type"] == "task" else MemoryType.GOAL

                    # Parse due date if present
                    due_date = None
                    if "due_date" in raw and raw["due_date"]:
                        try:
                            due_date = datetime.fromisoformat(
                                raw["due_date"].replace("Z", "+00:00")
                            )
                        except ValueError:
                            logger.warning("invalid_due_date_vault", date=raw["due_date"])

                    memory = Memory(
                        user_id=user_id,
                        short_text=raw["text"][:500],
                        memory_type=memory_type,
                        relevance_score=raw.get("confidence", 0.8),
                        source=f"vault:{path}",
                        metadata={
                            "extraction_confidence": raw.get("confidence", 0.8),
                            "note_date": note_date.isoformat(),
                        },
                        due_date=due_date,
                    )
                    memories.append(memory)

                except (KeyError, ValueError) as e:
                    logger.warning("invalid_vault_item_format", error=str(e), raw=raw)
                    continue

            # Filter duplicates
            memories = await self._filter_duplicates(memories, user_id)

            if not memories:
                logger.debug("all_vault_items_were_duplicates", path=path)
                return []

            # Store memories
            stored = await self._memory_repo.bulk_create(memories)

            logger.info(
                "vault_memories_extracted",
                path=path,
                user_id=user_id,
                count=len(stored),
            )

            return stored

        except Exception as e:
            logger.error("vault_extraction_failed", path=path, error=str(e))
            return []

    async def _call_extraction_llm(
        self,
        content: str,
        note_date: datetime,
    ) -> list[dict[str, Any]]:
        """Call LLM to extract tasks/goals from note content."""
        client = await self._get_http_client()

        prompt = VAULT_EXTRACTION_PROMPT.format(
            content=content,
            note_date=note_date.strftime("%Y-%m-%d"),
        )

        try:
            response = await client.post(
                "/chat/completions",
                json={
                    "model": "anthropic/claude-3.5-haiku",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 1000,
                },
            )
            response.raise_for_status()
            data = response.json()

            content_str = data["choices"][0]["message"]["content"].strip()

            # Handle markdown code block
            if content_str.startswith("```"):
                content_str = content_str.split("```")[1]
                if content_str.startswith("json"):
                    content_str = content_str[4:]
                content_str = content_str.strip()

            import json

            items = json.loads(content_str)

            # Filter by confidence
            return [item for item in items if item.get("confidence", 0) >= 0.7]

        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                logger.error(
                    "vault_extraction_llm_http_error",
                    status=e.response.status_code,
                    error_detail=error_detail,
                )
            except Exception:
                logger.error(
                    "vault_extraction_llm_http_error",
                    status=e.response.status_code,
                    error_text=e.response.text[:500],
                )
            return []
        except Exception as e:
            logger.error("vault_extraction_llm_failed", error=str(e))
            return []

    async def _filter_duplicates(
        self,
        memories: list[Memory],
        user_id: str,
    ) -> list[Memory]:
        """Filter out duplicate tasks/goals."""
        filtered = []

        for memory in memories:
            # Search for similar existing memories
            similar = await self._memory_repo.search_similar(
                query=memory.short_text,
                user_id=user_id,
                limit=1,
                min_score=0.85,
                memory_types=[memory.memory_type],
            )

            if similar:
                # Found duplicate, boost existing instead
                existing, score = similar[0]
                logger.debug(
                    "duplicate_vault_task_skipped",
                    new_text=memory.short_text[:50],
                    existing_text=existing.short_text[:50],
                    similarity=score,
                )
                await self._memory_repo.mark_referenced(existing.memory_id)
            else:
                filtered.append(memory)

        return filtered

    async def process_recent_daily_notes(
        self,
        user_id: str,
        days: int = 7,
    ) -> list[Memory]:
        """Process recent daily notes to extract tasks.

        Args:
            user_id: User ID
            days: Number of recent days to process (default 7)

        Returns:
            All extracted memories from recent notes
        """
        all_memories = []

        try:
            # GitHub search API doesn't support glob patterns, so we search for files
            # in Timestamps folder
            # We'll search for recent dates to find daily notes
            from datetime import datetime, timedelta

            today = datetime.utcnow()
            search_queries = []

            # Generate search queries for the last 7 days
            for i in range(days):
                date = today - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                # Search for this specific date in Timestamps folder
                search_queries.append(f"Timestamps {date_str}")

            for query in search_queries:
                try:
                    results = await self._vault_client.search_files(query)
                    logger.info("vault_search_results", query=query, count=len(results))

                    for result in results:
                        path = result["path"]
                        # Only process if it's actually in Timestamps folder and looks like a date
                        if "Timestamps" in path or "Daily" in path or "Journal" in path:
                            logger.info("processing_daily_note", path=path)

                            # Extract memories from this note
                            memories = await self.extract_from_daily_note(path, user_id)
                            all_memories.extend(memories)
                            logger.info(
                                "extracted_from_note", path=path, memories_count=len(memories)
                            )

                except Exception as e:
                    logger.error("vault_search_failed", query=query, error=str(e))
                    continue

            logger.info(
                "recent_daily_notes_processed",
                user_id=user_id,
                days=days,
                total_memories=len(all_memories),
            )

            return all_memories

        except Exception as e:
            logger.error("process_daily_notes_failed", error=str(e))
            return []


# Singleton
_vault_extraction: VaultMemoryExtraction | None = None


def get_vault_memory_extraction() -> VaultMemoryExtraction:
    """Get singleton vault memory extraction service."""
    global _vault_extraction
    if _vault_extraction is None:
        _vault_extraction = VaultMemoryExtraction()
    return _vault_extraction
