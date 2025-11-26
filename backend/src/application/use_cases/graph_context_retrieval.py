"""Graph context retrieval - enriches RAG with knowledge graph information."""

from dataclasses import dataclass
from typing import Any

import structlog

from src.infrastructure.graph.memory_graph_repository import MemoryGraphRepository
from src.infrastructure.graph.neo4j_client import get_neo4j_client

logger = structlog.get_logger()


@dataclass
class GraphContext:
    """Context retrieved from knowledge graph."""

    topics: list[dict[str, Any]]
    concepts: list[dict[str, Any]]
    related_topics: list[dict[str, Any]]
    formatted_context: str


class GraphContextRetrievalUseCase:
    """Retrieves contextual information from the knowledge graph.

    This enhances RAG by providing:
    - Topics the user has discussed
    - Concepts the user has mentioned with sentiment
    - Related topics and concepts
    """

    def __init__(self):
        """Initialize graph context retrieval use case."""
        self._neo4j_client = get_neo4j_client()
        self._graph_repo = MemoryGraphRepository(self._neo4j_client)

    async def get_context_for_query(
        self,
        user_id: str,
        query: str,
        max_topics: int = 5,
        max_concepts: int = 5,
    ) -> GraphContext:
        """Retrieve graph context relevant to a query.

        Args:
            user_id: User ID
            query: User's query
            max_topics: Maximum topics to retrieve
            max_concepts: Maximum concepts to retrieve

        Returns:
            GraphContext with topics, concepts, and formatted text
        """
        try:
            # Find relevant context from graph
            graph_context = await self._graph_repo.find_memory_context(
                user_id=user_id,
                query_text=query,
                limit=max_topics,
            )

            topics = graph_context.get("topics", [])
            concepts = graph_context.get("concepts", [])

            # Get related topics if we found any
            related_topics = []
            if topics:
                # Get topics that share concepts with found topics
                related_topics = await self._get_related_topics(
                    user_id=user_id,
                    topic_names=[t["name"] for t in topics[:2]],
                    limit=3,
                )

            # Format context for LLM
            formatted_context = self._format_graph_context(
                topics=topics,
                concepts=concepts,
                related_topics=related_topics,
            )

            logger.info(
                "graph_context_retrieved",
                user_id=user_id,
                topics_count=len(topics),
                concepts_count=len(concepts),
                related_topics_count=len(related_topics),
            )

            return GraphContext(
                topics=topics,
                concepts=concepts,
                related_topics=related_topics,
                formatted_context=formatted_context,
            )

        except Exception as e:
            logger.warning("graph_context_retrieval_failed", error=str(e))
            return GraphContext(
                topics=[],
                concepts=[],
                related_topics=[],
                formatted_context="",
            )

    async def get_topic_memories(
        self,
        user_id: str,
        topic_name: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Get memories about a specific topic.

        Args:
            user_id: User ID
            topic_name: Topic name
            limit: Maximum memories to retrieve

        Returns:
            List of memory information
        """
        try:
            memories = await self._graph_repo.get_memories_by_topic(
                user_id=user_id,
                topic_name=topic_name,
                limit=limit,
            )
            return memories
        except Exception as e:
            logger.error("topic_memory_retrieval_failed", error=str(e))
            return []

    async def get_concept_memories(
        self,
        concept_name: str,
        user_id: str | None = None,
        sentiment_filter: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Get memories mentioning a specific concept.

        Args:
            concept_name: Concept name
            user_id: Optional user filter
            sentiment_filter: Optional sentiment filter
            limit: Maximum memories to retrieve

        Returns:
            List of memory information
        """
        try:
            memories = await self._graph_repo.get_memories_by_concept(
                concept_name=concept_name,
                user_id=user_id,
                sentiment_filter=sentiment_filter,
                limit=limit,
            )
            return memories
        except Exception as e:
            logger.error("concept_memory_retrieval_failed", error=str(e))
            return []

    async def get_user_topics_summary(
        self,
        user_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get summary of all topics discussed by user.

        Args:
            user_id: User ID
            limit: Maximum topics to retrieve

        Returns:
            List of topic information with mention counts
        """
        try:
            topics = await self._graph_repo.get_user_topics(
                user_id=user_id,
                limit=limit,
            )
            return topics
        except Exception as e:
            logger.error("topic_summary_retrieval_failed", error=str(e))
            return []

    async def _get_related_topics(
        self,
        user_id: str,
        topic_names: list[str],
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Find topics related to given topics through shared concepts.

        Args:
            user_id: User ID
            topic_names: List of topic names to find related topics for
            limit: Maximum related topics per input topic

        Returns:
            List of related topic information
        """
        if not topic_names:
            return []

        try:
            # Query to find topics that share concepts with the input topics
            query = """
            MATCH (t1:Topic {user_id: $user_id})-[:DISCUSSES]-(m:Memory)-[:MENTIONS]-(c:Concept)
            WHERE t1.name IN $topic_names
            WITH c, t1
            MATCH (t2:Topic {user_id: $user_id})-[:DISCUSSES]-(m2:Memory)-[:MENTIONS]-(c)
            WHERE t2.name <> t1.name AND NOT t2.name IN $topic_names
            RETURN DISTINCT t2.name as name,
                   t2.mention_count as mention_count,
                   count(DISTINCT c) as shared_concepts
            ORDER BY shared_concepts DESC, t2.mention_count DESC
            LIMIT $limit
            """

            results = await self._neo4j_client.execute_query(
                query,
                {
                    "user_id": user_id,
                    "topic_names": topic_names,
                    "limit": limit,
                },
            )

            return results

        except Exception as e:
            logger.warning("related_topics_query_failed", error=str(e))
            return []

    def _format_graph_context(
        self,
        topics: list[dict[str, Any]],
        concepts: list[dict[str, Any]],
        related_topics: list[dict[str, Any]],
    ) -> str:
        """Format graph context for LLM consumption.

        Args:
            topics: Relevant topics
            concepts: Relevant concepts
            related_topics: Related topics

        Returns:
            Formatted context string
        """
        parts = []

        # Format topics
        if topics:
            topic_lines = []
            for topic in topics:
                name = topic.get("name", "")
                mentions = topic.get("mention_count", 0)
                topic_lines.append(f"- {name} (mentioned {mentions}x)")

            parts.append(
                "## Conversation Topics\n"
                "The user has previously discussed:\n" + "\n".join(topic_lines)
            )

        # Format concepts with sentiment
        if concepts:
            concept_lines = []
            for concept in concepts:
                name = concept.get("name", "")
                category = concept.get("category", "general")
                # Note: sentiment is on the relationship, not the concept node
                concept_lines.append(f"- {name} ({category})")

            parts.append(
                "## Related Concepts\n"
                "Concepts relevant to this conversation:\n" + "\n".join(concept_lines)
            )

        # Format related topics
        if related_topics:
            related_lines = []
            for topic in related_topics:
                name = topic.get("name", "")
                mentions = topic.get("mention_count", 0)
                shared = topic.get("shared_concepts", 0)
                related_lines.append(f"- {name} (mentioned {mentions}x, {shared} shared concepts)")

            parts.append(
                "## Related Topics\n" "Topics that might be relevant:\n" + "\n".join(related_lines)
            )

        if not parts:
            return ""

        return "\n\n".join(parts)


# Singleton
_graph_context_retrieval: GraphContextRetrievalUseCase | None = None


def get_graph_context_retrieval() -> GraphContextRetrievalUseCase:
    """Get singleton graph context retrieval use case."""
    global _graph_context_retrieval
    if _graph_context_retrieval is None:
        _graph_context_retrieval = GraphContextRetrievalUseCase()
    return _graph_context_retrieval
