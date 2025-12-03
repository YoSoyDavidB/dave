"""Extract memories and tasks from vault notes."""

import re
from datetime import UTC, datetime
from typing import Any, cast

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
        return datetime.now(UTC)

    def _extract_checkboxes_from_content(self, content: str) -> list[str]:
        """Extract uncompleted checkboxes from markdown content.

        Returns:
            List of task texts (without the checkbox prefix)
        """
        tasks = []
        # Match uncompleted checkboxes: - [ ] Task text
        pattern = r"^[\s]*-\s*\[\s*\]\s*(.+)$"

        for line in content.split("\n"):
            match = re.match(pattern, line)
            if match:
                task_text = match.group(1).strip()
                if task_text:  # Only add non-empty tasks
                    tasks.append(task_text)

        return tasks

    def _extract_completed_checkboxes(self, content: str) -> list[str]:
        """Extract completed checkboxes from markdown content.

        Returns:
            List of completed task texts (without the checkbox prefix)
        """
        completed_tasks = []
        # Match completed checkboxes: - [x] Task text or - [X] Task text
        pattern = r"^[\s]*-\s*\[[xX]\]\s*(.+)$"

        for line in content.split("\n"):
            match = re.match(pattern, line)
            if match:
                task_text = match.group(1).strip()
                if task_text:
                    completed_tasks.append(task_text)

        return completed_tasks

    async def _mark_vault_tasks_completed(
        self,
        user_id: str,
        completed_task_texts: list[str],
    ) -> int:
        """Mark tasks as completed based on vault checkbox status.

        Finds existing TASK memories that match the completed task texts
        and marks them as completed.

        Args:
            user_id: User ID
            completed_task_texts: List of task texts that are marked complete in vault

        Returns:
            Number of tasks marked as completed
        """
        if not completed_task_texts:
            return 0

        try:
            # Get all user's task memories
            all_tasks = await self._memory_repo.get_by_type(
                user_id=user_id,
                memory_type=MemoryType.TASK,
            )

            marked_count = 0
            for task in all_tasks:
                # Skip already completed tasks
                if task.completed:
                    continue

                # Check if this task's text matches any completed task
                task_text_lower = task.short_text.lower().strip()
                for completed_text in completed_task_texts:
                    # Fuzzy match: if the task text contains the completed text or vice versa
                    # This handles minor variations in task description
                    completed_lower = completed_text.lower().strip()
                    if (
                        task_text_lower == completed_lower
                        or completed_lower in task_text_lower
                        or task_text_lower in completed_lower
                    ):
                        # Mark as completed
                        task.mark_completed()
                        await self._memory_repo.update(task)
                        marked_count += 1
                        logger.info(
                            "vault_task_marked_completed",
                            task_text=task.short_text,
                            memory_id=str(task.memory_id),
                        )
                        break  # Move to next task

            if marked_count > 0:
                logger.info(
                    "vault_tasks_completed_sync",
                    user_id=user_id,
                    marked_count=marked_count,
                    total_completed=len(completed_task_texts),
                )

            return marked_count

        except Exception as e:
            logger.error("mark_vault_tasks_failed", user_id=user_id, error=str(e))
            return 0

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
            print(f"[DEBUG] File content length: {len(content)} chars")
            print(f"[DEBUG] First 500 chars: {content[:500]}")

            # Extract note date
            note_date = self._extract_note_date(path, content)

            # Skip if note is too old (more than 7 days)
            days_old = (datetime.now(UTC) - note_date).days
            if days_old > 7:
                logger.debug("vault_note_too_old", path=path, days_old=days_old)
                return []

            # First, try to extract checkboxes directly with regex (faster and more reliable)
            checkbox_tasks = self._extract_checkboxes_from_content(content)
            print(f"[DEBUG] Found {len(checkbox_tasks)} uncompleted checkboxes in {path}")
            if checkbox_tasks:
                print(f"[DEBUG] Uncompleted tasks: {checkbox_tasks[:3]}...")  # Print first 3

            # Also extract completed checkboxes to mark them as done
            completed_tasks = self._extract_completed_checkboxes(content)
            print(f"[DEBUG] Found {len(completed_tasks)} completed checkboxes in {path}")
            if completed_tasks:
                print(f"[DEBUG] Completed tasks: {completed_tasks[:3]}...")
                # Mark these tasks as completed in existing memories
                await self._mark_vault_tasks_completed(user_id, completed_tasks)

            # If we found checkboxes, use them directly
            if checkbox_tasks:
                raw_items = [
                    {
                        "text": task,
                        "type": "task",
                        "confidence": 1.0,  # High confidence for explicit checkboxes
                    }
                    for task in checkbox_tasks
                ]
                logger.info("extracted_checkboxes_from_note", path=path, count=len(checkbox_tasks))
            else:
                # Fallback to LLM extraction for implicit tasks/goals
                raw_items = await self._call_extraction_llm(content, note_date)

            if not raw_items:
                logger.debug("no_tasks_found_in_note", path=path)
                print(f"[DEBUG] No raw_items found for {path}")
                return []

            print(f"[DEBUG] Processing {len(raw_items)} raw items from {path}")
            # Convert to Memory objects
            memories = []
            for raw in raw_items:
                try:
                    # Type assertion for raw dict
                    raw_dict: dict[str, object] = raw  # type: ignore
                    memory_type = MemoryType.TASK if raw_dict["type"] == "task" else MemoryType.GOAL

                    # Parse due date if present
                    due_date = None
                    if "due_date" in raw_dict and raw_dict["due_date"]:
                        due_str = str(raw_dict["due_date"])
                        try:
                            due_date = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
                        except ValueError:
                            logger.warning("invalid_due_date_vault", date=due_str)

                    text = str(raw_dict["text"])
                    confidence_val = raw_dict.get("confidence", 0.8)
                    confidence = float(cast(float, confidence_val))
                    memory = Memory(
                        user_id=user_id,
                        short_text=text[:500],
                        memory_type=memory_type,
                        relevance_score=confidence,
                        source=f"vault:{path}",
                        metadata={
                            "extraction_confidence": confidence,
                            "note_date": note_date.isoformat(),
                        },
                        due_date=due_date,
                    )
                    memories.append(memory)

                except (KeyError, ValueError) as e:
                    logger.warning("invalid_vault_item_format", error=str(e), raw=raw)
                    continue

            print(f"[DEBUG] Created {len(memories)} Memory objects from {path}")

            # Filter duplicates
            memories = await self._filter_duplicates(memories, user_id)

            print(
                f"[DEBUG] After filtering duplicates: "
                f"{len(memories)} memories remaining from {path}"
            )
            if not memories:
                logger.debug("all_vault_items_were_duplicates", path=path)
                print(f"[DEBUG] All items were duplicates for {path}")
                return []

            # Store memories
            print(f"[DEBUG] Attempting to store {len(memories)} memories from {path}")
            stored = await self._memory_repo.bulk_create(memories)
            print(f"[DEBUG] Successfully stored {len(stored)} memories from {path}")

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
                    "model": "meta-llama/llama-3.2-3b-instruct:free",
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
                print("[DEBUG] DUPLICATE FOUND:")
                print(f"[DEBUG]   New task: {memory.short_text[:100]}")
                print(f"[DEBUG]   Existing: {existing.short_text[:100]}")
                print(f"[DEBUG]   Similarity: {score}")
                print(f"[DEBUG]   Existing source: {existing.source}")
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
        logger.info("process_recent_daily_notes_started", user_id=user_id, days=days)
        print(f"[DEBUG] process_recent_daily_notes called for user: {user_id}, days: {days}")
        all_memories = []

        try:
            # GitHub search API doesn't support glob patterns, so we search for files
            # in Timestamps folder
            # We'll search for recent dates to find daily notes
            from datetime import datetime, timedelta

            today = datetime.now(UTC)
            search_queries = []

            # Generate search queries for the last 7 days
            for i in range(days):
                date = today - timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                # Search for this specific date in Timestamps folder
                search_queries.append(f"Timestamps {date_str}")

            print(
                f"[DEBUG] Generated {len(search_queries)} search queries: {search_queries[:3]}..."
            )

            for query in search_queries:
                try:
                    print(f"[DEBUG] Searching with query: {query}")
                    results = await self._vault_client.search_files(query)
                    print(f"[DEBUG] Found {len(results)} results for query: {query}")
                    logger.info("vault_search_results", query=query, count=len(results))

                    for result in results:
                        path = result["path"]
                        print(f"[DEBUG] Checking file: {path}")
                        # Only process if it's actually in Timestamps folder and looks like a date
                        if "Timestamps" in path or "Daily" in path or "Journal" in path:
                            logger.info("processing_daily_note", path=path)
                            print(f"[DEBUG] Processing daily note: {path}")

                            # Extract memories from this note
                            memories = await self.extract_from_daily_note(path, user_id)
                            all_memories.extend(memories)
                            print(f"[DEBUG] Extracted {len(memories)} memories from {path}")
                            logger.info(
                                "extracted_from_note", path=path, memories_count=len(memories)
                            )
                        else:
                            print(
                                f"[DEBUG] Skipping file (not in Timestamps/Daily/Journal): {path}"
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
