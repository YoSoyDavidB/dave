"""Graph enrichment use case - extracts topics and concepts for the knowledge graph."""

import json
from typing import Any

import httpx
import structlog

from src.config import get_settings
from src.domain.entities.memory import Memory
from src.infrastructure.graph.memory_graph_repository import MemoryGraphRepository
from src.infrastructure.graph.models import RelationType
from src.infrastructure.graph.neo4j_client import get_neo4j_client

logger = structlog.get_logger()

# Prompt for extracting topics and concepts
GRAPH_EXTRACTION_PROMPT = """Analyze this conversation and extract:
1. **Topics**: Main subjects being discussed
2. **Concepts**: Specific concepts, technologies, or ideas mentioned
3. **Relationships**: How the user feels about these topics/concepts

Return a JSON object with:
- "topics": Array of topic names being discussed
- "concepts": Array of objects with "name", "category" (technology/hobby/location/other), and
    "sentiment" (positive/negative/neutral)

Example:
{{
  "topics": ["machine learning", "career development", "python programming"],
  "concepts": [
    {{"name": "FastAPI", "category": "technology", "sentiment": "positive"}},
    {{"name": "Neo4j", "category": "technology", "sentiment": "neutral"}},
    {{"name": "hiking", "category": "hobby", "sentiment": "positive"}}
  ]
}}

Conversation:
{conversation}

Return ONLY the JSON object, no other text."""


class GraphEnrichmentUseCase:
    """Enriches the knowledge graph with topics and concepts from conversations."""

    def __init__(self):
        self._settings = get_settings()
        self._neo4j_client = get_neo4j_client()
        self._graph_repo = MemoryGraphRepository(self._neo4j_client)
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

    async def enrich_from_conversation(
        self,
        messages: list[dict[str, str]],
        user_id: str,
        memories: list[Memory] | None = None,
    ) -> dict[str, Any]:
        """Extract topics and concepts from conversation and add to graph.

        Args:
            messages: Conversation messages
            user_id: User ID
            memories: Optional list of memories extracted from this conversation

        Returns:
            Dictionary with extracted topics and concepts
        """
        if not messages:
            return {"topics": [], "concepts": []}

        # Format conversation
        conversation_text = self._format_conversation(messages)

        # Extract topics and concepts using LLM
        extraction = await self._extract_graph_entities(conversation_text)

        if not extraction:
            return {"topics": [], "concepts": []}

        topics = extraction.get("topics", [])
        concepts = extraction.get("concepts", [])

        # Create topic nodes
        for topic_name in topics:
            try:
                await self._graph_repo.create_topic_node(
                    user_id=user_id,
                    topic_name=topic_name,
                )

                # Link memories to this topic if provided
                if memories:
                    for memory in memories:
                        await self._graph_repo.link_memory_to_topic(
                            memory_id=memory.memory_id,
                            user_id=user_id,
                            topic_name=topic_name,
                            relevance=0.8,  # Default relevance
                        )
            except Exception as e:
                logger.error("failed_to_create_topic", topic=topic_name, error=str(e))

        # Create concept nodes
        for concept in concepts:
            try:
                concept_name = concept.get("name", "")
                category = concept.get("category", "general")
                sentiment = concept.get("sentiment", "neutral")

                if not concept_name:
                    continue

                await self._graph_repo.create_concept_node(
                    concept_name=concept_name,
                    category=category,
                )

                # Link memories to this concept if provided
                if memories:
                    for memory in memories:
                        # Link if memory text mentions the concept
                        if concept_name.lower() in memory.short_text.lower():
                            await self._graph_repo.link_memory_to_concept(
                                memory_id=memory.memory_id,
                                concept_name=concept_name,
                                sentiment=sentiment,
                                category=category,
                            )
            except Exception as e:
                logger.error("failed_to_create_concept", concept=concept, error=str(e))

        logger.info(
            "graph_enriched",
            user_id=user_id,
            topics_count=len(topics),
            concepts_count=len(concepts),
        )

        return {
            "topics": topics,
            "concepts": concepts,
        }

    async def link_related_memories(
        self,
        memories: list[Memory],
    ) -> None:
        """Create relationships between related memories.

        Args:
            memories: List of memories to analyze for relationships
        """
        if len(memories) < 2:
            return

        # For now, use simple heuristics
        # In production, you'd want to use embeddings similarity
        for i, memory1 in enumerate(memories):
            for memory2 in memories[i + 1 :]:
                # Check if memories are related based on type and content
                relation = self._detect_relationship(memory1, memory2)
                if relation:
                    try:
                        await self._graph_repo.link_related_memories(
                            from_memory_id=memory1.memory_id,
                            to_memory_id=memory2.memory_id,
                            rel_type=relation["type"],
                            strength=relation["strength"],
                            reason=relation.get("reason", ""),
                        )
                    except Exception as e:
                        logger.error(
                            "failed_to_link_memories",
                            from_id=str(memory1.memory_id),
                            to_id=str(memory2.memory_id),
                            error=str(e),
                        )

    def _detect_relationship(
        self,
        memory1: Memory,
        memory2: Memory,
    ) -> dict[str, Any] | None:
        """Detect if two memories are related.

        Args:
            memory1: First memory
            memory2: Second memory

        Returns:
            Dictionary with relationship type, strength, and reason if related,
            None otherwise
        """
        # Same type memories are related
        if memory1.memory_type == memory2.memory_type:
            # Check for keyword overlap
            words1 = set(memory1.short_text.lower().split())
            words2 = set(memory2.short_text.lower().split())
            overlap = len(words1 & words2)

            if overlap >= 3:  # At least 3 common words
                return {
                    "type": RelationType.RELATES_TO,
                    "strength": min(1.0, overlap / 10),
                    "reason": f"Same type with {overlap} common words",
                }

        # Task -> Goal relationship
        if memory1.memory_type.value == "task" and memory2.memory_type.value == "goal":
            return {
                "type": RelationType.LEADS_TO,
                "strength": 0.7,
                "reason": "Task contributes to goal",
            }

        return None

    def _format_conversation(self, messages: list[dict[str, str]]) -> str:
        """Format messages into readable conversation text."""
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n\n".join(lines)

    async def _extract_graph_entities(
        self,
        conversation_text: str,
    ) -> dict[str, Any]:
        """Extract topics and concepts from conversation.

        Args:
            conversation_text: Formatted conversation

        Returns:
            Dictionary with topics and concepts
        """
        client = await self._get_client()

        prompt = GRAPH_EXTRACTION_PROMPT.format(conversation=conversation_text)

        try:
            response = await client.post(
                "/chat/completions",
                json={
                    "model": "meta-llama/llama-3.2-3b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 800,
                },
            )
            response.raise_for_status()
            data = response.json()

            content = data["choices"][0]["message"]["content"].strip()

            # Handle markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            logger.debug("graph_extraction_raw_response", content=content[:500])

            result = json.loads(content)
            return result

        except json.JSONDecodeError as e:
            logger.warning("graph_extraction_json_error", error=str(e))
            return {"topics": [], "concepts": []}
        except httpx.HTTPStatusError as e:
            logger.error("graph_extraction_api_error", status=e.response.status_code)
            return {"topics": [], "concepts": []}
        except Exception as e:
            logger.error("graph_extraction_failed", error=str(e))
            return {"topics": [], "concepts": []}


# Singleton
_graph_enrichment_use_case: GraphEnrichmentUseCase | None = None


def get_graph_enrichment_use_case() -> GraphEnrichmentUseCase:
    """Get singleton graph enrichment use case."""
    global _graph_enrichment_use_case
    if _graph_enrichment_use_case is None:
        _graph_enrichment_use_case = GraphEnrichmentUseCase()
    return _graph_enrichment_use_case
