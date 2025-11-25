"""Memory extraction use case - extracts memories from conversations."""

import json
from typing import Any

import httpx
import structlog

from src.config import get_settings
from src.domain.entities.memory import Memory, MemoryType
from src.infrastructure.vector_store.memory_repository import get_memory_repository

logger = structlog.get_logger()

# Prompt for memory extraction
EXTRACTION_PROMPT = """Analyze this conversation and extract any information
worth remembering about the user.

Look for:
1. **Preferences**: How the user likes things done (communication style,
   format preferences, etc.)
2. **Facts**: Information about the user (job, skills, location, etc.)
3. **Tasks**: Things the user wants to do or accomplish (with optional due dates)
4. **Goals**: Long-term objectives or aspirations (with optional progress)
5. **Profile**: Personal details (name, background, etc.)

Return a JSON array of memories. Each memory should have:
- "text": A concise statement (max 100 words) about the user in third person
- "type": One of "preference", "fact", "task", "goal", "profile"
- "confidence": How confident you are (0.0-1.0)
- "due_date": (Optional, for tasks only) ISO format datetime if user mentions when
  task should be done
- "progress": (Optional, for goals only) Progress percentage 0-100 if user mentions progress

Only include memories with confidence >= 0.7. Return empty array [] if nothing notable.

Example output:
[
  {"text": "Prefers concise, direct answers without excessive explanation",
   "type": "preference", "confidence": 0.9},
  {"text": "Is a software engineer working with Python and FastAPI",
   "type": "fact", "confidence": 0.95},
  {"text": "Needs to finish project documentation",
   "type": "task", "confidence": 0.85, "due_date": "2025-11-30T23:59:59Z"},
  {"text": "Wants to improve English speaking skills",
   "type": "goal", "confidence": 0.85, "progress": 30}
]

Conversation:
{conversation}

Return ONLY the JSON array, no other text."""


class MemoryExtractionUseCase:
    """Extracts memorable information from conversations."""

    def __init__(self):
        self._settings = get_settings()
        self._memory_repo = get_memory_repository()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._settings.openrouter_base_url,
                headers={
                    "Authorization": f"Bearer {self._settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def extract_from_conversation(
        self,
        messages: list[dict[str, str]],
        user_id: str,
        conversation_id: str,
    ) -> list[Memory]:
        """Extract memories from a conversation.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            user_id: User who owns these memories
            conversation_id: Source conversation ID

        Returns:
            List of extracted and stored memories
        """
        if not messages:
            return []

        # Format conversation for the prompt
        conversation_text = self._format_conversation(messages)

        # Call LLM to extract memories
        raw_memories = await self._call_extraction_llm(conversation_text)

        if not raw_memories:
            logger.debug("no_memories_extracted", conversation_id=conversation_id)
            return []

        # Convert to Memory objects
        memories = []
        for raw in raw_memories:
            try:
                memory_type = MemoryType(raw["type"])

                # Parse optional fields
                due_date = None
                if "due_date" in raw and raw["due_date"]:
                    from datetime import datetime

                    try:
                        due_date = datetime.fromisoformat(raw["due_date"].replace("Z", "+00:00"))
                    except ValueError:
                        logger.warning("invalid_due_date_format", date=raw["due_date"])

                progress = raw.get("progress", 0.0)

                memory = Memory(
                    user_id=user_id,
                    short_text=raw["text"][:500],  # Enforce max length
                    memory_type=memory_type,
                    relevance_score=raw.get("confidence", 0.8),
                    source=conversation_id,
                    metadata={"extraction_confidence": raw.get("confidence", 0.8)},
                    due_date=due_date,
                    progress=progress,
                )
                memories.append(memory)
            except (KeyError, ValueError) as e:
                logger.warning("invalid_memory_format", error=str(e), raw=raw)
                continue

        # Check for duplicates before storing
        memories = await self._filter_duplicates(memories, user_id)

        if not memories:
            logger.debug("all_memories_were_duplicates", conversation_id=conversation_id)
            return []

        # Store memories
        stored = await self._memory_repo.bulk_create(memories)

        logger.info(
            "memories_extracted",
            conversation_id=conversation_id,
            user_id=user_id,
            count=len(stored),
            types=[m.memory_type.value for m in stored],
        )

        return stored

    def _format_conversation(self, messages: list[dict[str, str]]) -> str:
        """Format messages into readable conversation text."""
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n\n".join(lines)

    async def _call_extraction_llm(self, conversation_text: str) -> list[dict[str, Any]]:
        """Call LLM to extract memories from conversation.

        Args:
            conversation_text: Formatted conversation

        Returns:
            List of raw memory dicts from LLM
        """
        client = await self._get_client()

        prompt = EXTRACTION_PROMPT.format(conversation=conversation_text)

        try:
            response = await client.post(
                "/chat/completions",
                json={
                    # Fast, cheap model for extraction
                    "model": "meta-llama/llama-3.2-3b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}],
                    # Low temperature for consistent extraction
                    "temperature": 0.1,
                    "max_tokens": 1000,
                },
            )
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"].strip()

            # Parse JSON response
            # Handle case where LLM wraps in markdown code block
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            logger.debug("memory_extraction_raw_response", content=content[:500])

            memories = json.loads(content)

            # Filter by confidence
            return [m for m in memories if m.get("confidence", 0) >= 0.7]

        except json.JSONDecodeError as e:
            logger.warning("memory_extraction_json_error", error=str(e))
            return []
        except httpx.HTTPStatusError as e:
            logger.error("memory_extraction_api_error", status=e.response.status_code)
            return []
        except Exception as e:
            logger.error("memory_extraction_failed", error=str(e))
            return []

    async def _filter_duplicates(
        self,
        memories: list[Memory],
        user_id: str,
    ) -> list[Memory]:
        """Filter out memories that are too similar to existing ones.

        Args:
            memories: New memories to check
            user_id: User ID

        Returns:
            Filtered list without duplicates
        """
        filtered = []

        for memory in memories:
            # Search for similar existing memories
            similar = await self._memory_repo.search_similar(
                query=memory.short_text,
                user_id=user_id,
                limit=1,
                # High threshold for duplicate detection
                min_score=0.85,
                memory_types=[memory.memory_type],
            )

            if similar:
                # Found a very similar memory, skip this one
                existing, score = similar[0]
                logger.debug(
                    "duplicate_memory_skipped",
                    new_text=memory.short_text[:50],
                    existing_text=existing.short_text[:50],
                    similarity=score,
                )

                # But boost the existing memory since user mentioned it again
                await self._memory_repo.mark_referenced(existing.memory_id)
            else:
                filtered.append(memory)

        return filtered


# Singleton
_extraction_use_case: MemoryExtractionUseCase | None = None


def get_memory_extraction_use_case() -> MemoryExtractionUseCase:
    """Get singleton memory extraction use case."""
    global _extraction_use_case
    if _extraction_use_case is None:
        _extraction_use_case = MemoryExtractionUseCase()
    return _extraction_use_case
