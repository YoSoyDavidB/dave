"""Repository for managing memory knowledge graph in Neo4j."""

from datetime import datetime
from typing import Any
from uuid import UUID

import structlog

from src.domain.entities.memory import Memory
from src.infrastructure.graph.models import (
    ConceptNode,
    MemoryNode,
    RelationType,
    TopicNode,
)
from src.infrastructure.graph.neo4j_client import Neo4jClient

logger = structlog.get_logger()


class MemoryGraphRepository:
    """Repository for managing the memory knowledge graph.

    This repository handles:
    - Creating memory nodes when memories are stored
    - Creating and updating topic nodes
    - Creating relationships between memories
    - Querying the graph for contextual information
    """

    def __init__(self, neo4j_client: Neo4jClient):
        """Initialize repository.

        Args:
            neo4j_client: Neo4j client instance
        """
        self.client = neo4j_client

    async def create_memory_node(self, memory: Memory) -> None:
        """Create a node in the graph for a memory.

        Args:
            memory: Memory entity to create node for
        """
        node = MemoryNode(
            memory_id=memory.memory_id,
            user_id=memory.user_id,
            short_text=memory.short_text,
            memory_type=memory.memory_type.value,
            timestamp=memory.timestamp,
            relevance_score=memory.relevance_score,
        )

        query = f"""
        MERGE (m:Memory:{memory.memory_type.value.capitalize()} {{memory_id: $memory_id}})
        SET m += {node.to_cypher_props()}
        RETURN m
        """

        await self.client.execute_write(query, node.properties)
        logger.info("memory_node_created", memory_id=str(memory.memory_id))

    async def create_topic_node(
        self,
        user_id: str,
        topic_name: str,
        description: str = "",
    ) -> None:
        """Create or update a topic node.

        Args:
            user_id: User ID
            topic_name: Topic name
            description: Topic description
        """
        node = TopicNode(
            user_id=user_id,
            name=topic_name,
            description=description,
        )

        # MERGE will create if not exists, or update if exists
        query = """
        MERGE (t:Topic {user_id: $user_id, name: $name})
        ON CREATE SET
            t.description = $description,
            t.first_mentioned = $first_mentioned,
            t.last_mentioned = $last_mentioned,
            t.mention_count = 1
        ON MATCH SET
            t.last_mentioned = $last_mentioned,
            t.mention_count = t.mention_count + 1,
            t.description = CASE WHEN $description <> '' THEN $description ELSE t.description END
        RETURN t
        """

        await self.client.execute_write(query, node.properties)
        logger.info("topic_node_created", user_id=user_id, topic=topic_name)

    async def create_concept_node(
        self,
        concept_name: str,
        category: str = "general",
        description: str = "",
    ) -> None:
        """Create a concept node.

        Args:
            concept_name: Concept name
            category: Concept category
            description: Concept description
        """
        node = ConceptNode(
            name=concept_name,
            category=category,
            description=description,
        )

        query = f"""
        MERGE (c:Concept:{category.capitalize()} {{name: $name}})
        ON CREATE SET c += {node.to_cypher_props()}
        RETURN c
        """

        await self.client.execute_write(query, node.properties)
        logger.info("concept_node_created", concept=concept_name)

    async def link_memory_to_topic(
        self,
        memory_id: UUID,
        user_id: str,
        topic_name: str,
        relevance: float = 1.0,
    ) -> None:
        """Create a relationship between a memory and a topic.

        Args:
            memory_id: Memory ID
            user_id: User ID (for topic lookup)
            topic_name: Topic name
            relevance: Relevance score (0.0-1.0)
        """
        # Ensure topic exists
        await self.create_topic_node(user_id, topic_name)

        query = """
        MATCH (m:Memory {memory_id: $memory_id})
        MATCH (t:Topic {user_id: $user_id, name: $topic_name})
        MERGE (m)-[r:DISCUSSES]->(t)
        SET r.relevance = $relevance,
            r.created_at = $created_at
        RETURN r
        """

        await self.client.execute_write(
            query,
            {
                "memory_id": str(memory_id),
                "user_id": user_id,
                "topic_name": topic_name,
                "relevance": relevance,
                "created_at": datetime.utcnow().isoformat(),
            },
        )
        logger.info("memory_topic_linked", memory_id=str(memory_id), topic=topic_name)

    async def link_memory_to_concept(
        self,
        memory_id: UUID,
        concept_name: str,
        sentiment: str = "neutral",
        category: str = "general",
    ) -> None:
        """Create a relationship between a memory and a concept.

        Args:
            memory_id: Memory ID
            concept_name: Concept name
            sentiment: Sentiment (positive/negative/neutral)
            category: Concept category
        """
        # Ensure concept exists
        await self.create_concept_node(concept_name, category)

        query = """
        MATCH (m:Memory {memory_id: $memory_id})
        MATCH (c:Concept {name: $concept_name})
        MERGE (m)-[r:MENTIONS]->(c)
        SET r.sentiment = $sentiment,
            r.created_at = $created_at
        RETURN r
        """

        await self.client.execute_write(
            query,
            {
                "memory_id": str(memory_id),
                "concept_name": concept_name,
                "sentiment": sentiment,
                "created_at": datetime.utcnow().isoformat(),
            },
        )
        logger.info(
            "memory_concept_linked",
            memory_id=str(memory_id),
            concept=concept_name,
        )

    async def link_related_memories(
        self,
        from_memory_id: UUID,
        to_memory_id: UUID,
        rel_type: RelationType,
        strength: float = 1.0,
        reason: str = "",
    ) -> None:
        """Create a relationship between two memories.

        Args:
            from_memory_id: Source memory ID
            to_memory_id: Target memory ID
            rel_type: Type of relationship
            strength: Relationship strength (0.0-1.0)
            reason: Optional explanation
        """
        query = f"""
        MATCH (m1:Memory {{memory_id: $from_id}})
        MATCH (m2:Memory {{memory_id: $to_id}})
        MERGE (m1)-[r:{rel_type.value}]->(m2)
        SET r.strength = $strength,
            r.reason = $reason,
            r.created_at = $created_at
        RETURN r
        """

        await self.client.execute_write(
            query,
            {
                "from_id": str(from_memory_id),
                "to_id": str(to_memory_id),
                "strength": strength,
                "reason": reason,
                "created_at": datetime.utcnow().isoformat(),
            },
        )
        logger.info(
            "memories_linked",
            from_id=str(from_memory_id),
            to_id=str(to_memory_id),
            rel_type=rel_type.value,
        )

    async def get_related_memories(
        self,
        memory_id: UUID,
        max_depth: int = 2,
        min_strength: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Get memories related to a given memory through the graph.

        Args:
            memory_id: Memory ID to start from
            max_depth: Maximum depth of relationships to traverse
            min_strength: Minimum relationship strength to consider

        Returns:
            List of related memory nodes with relationship info
        """
        query = f"""
        MATCH path = (m1:Memory {{memory_id: $memory_id}})-[r*1..{max_depth}]-(m2:Memory)
        WHERE ALL(rel IN r WHERE rel.strength >= $min_strength)
        RETURN DISTINCT m2.memory_id as memory_id,
               m2.short_text as short_text,
               m2.memory_type as memory_type,
               m2.relevance_score as relevance_score,
               length(path) as distance,
               [rel IN r | type(rel)] as relationship_types
        ORDER BY distance, relevance_score DESC
        LIMIT 20
        """

        results = await self.client.execute_query(
            query,
            {
                "memory_id": str(memory_id),
                "min_strength": min_strength,
            },
        )
        return results

    async def get_memories_by_topic(
        self,
        user_id: str,
        topic_name: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get all memories discussing a specific topic.

        Args:
            user_id: User ID
            topic_name: Topic name
            limit: Maximum number of results

        Returns:
            List of memory nodes
        """
        query = """
        MATCH (t:Topic {user_id: $user_id, name: $topic_name})<-[r:DISCUSSES]-(m:Memory)
        RETURN m.memory_id as memory_id,
               m.short_text as short_text,
               m.memory_type as memory_type,
               m.timestamp as timestamp,
               r.relevance as relevance
        ORDER BY r.relevance DESC, m.timestamp DESC
        LIMIT $limit
        """

        results = await self.client.execute_query(
            query,
            {
                "user_id": user_id,
                "topic_name": topic_name,
                "limit": limit,
            },
        )
        return results

    async def get_user_topics(
        self,
        user_id: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get all topics discussed by a user.

        Args:
            user_id: User ID
            limit: Maximum number of topics

        Returns:
            List of topic nodes with mention counts
        """
        query = """
        MATCH (t:Topic {user_id: $user_id})
        RETURN t.name as name,
               t.description as description,
               t.mention_count as mention_count,
               t.first_mentioned as first_mentioned,
               t.last_mentioned as last_mentioned
        ORDER BY t.mention_count DESC, t.last_mentioned DESC
        LIMIT $limit
        """

        results = await self.client.execute_query(
            query,
            {
                "user_id": user_id,
                "limit": limit,
            },
        )
        return results

    async def get_memories_by_concept(
        self,
        concept_name: str,
        user_id: str | None = None,
        sentiment_filter: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get memories that mention a specific concept.

        Args:
            concept_name: Concept name
            user_id: Optional user ID filter
            sentiment_filter: Optional sentiment filter (positive/negative/neutral)
            limit: Maximum number of results

        Returns:
            List of memory nodes
        """
        user_filter = "AND m.user_id = $user_id" if user_id else ""
        sentiment_filter_clause = "AND r.sentiment = $sentiment" if sentiment_filter else ""

        query = f"""
        MATCH (c:Concept {{name: $concept_name}})<-[r:MENTIONS]-(m:Memory)
        WHERE 1=1 {user_filter} {sentiment_filter_clause}
        RETURN m.memory_id as memory_id,
               m.short_text as short_text,
               m.memory_type as memory_type,
               m.user_id as user_id,
               r.sentiment as sentiment
        ORDER BY m.timestamp DESC
        LIMIT $limit
        """

        params: dict[str, Any] = {
            "concept_name": concept_name,
            "limit": limit,
        }
        if user_id:
            params["user_id"] = user_id
        if sentiment_filter:
            params["sentiment"] = sentiment_filter

        results = await self.client.execute_query(query, params)
        return results

    async def find_memory_context(
        self,
        user_id: str,
        query_text: str,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Find contextual information for a query using the graph.

        This combines:
        - Related topics
        - Related concepts
        - Connected memories

        Args:
            user_id: User ID
            query_text: Query text to find context for
            limit: Number of results per category

        Returns:
            Dictionary with topics, concepts, and related memories
        """
        # Simple keyword matching for now
        # In production, you'd want to use embeddings or NLP
        keywords = query_text.lower().split()

        # Find relevant topics
        topic_query = """
        MATCH (t:Topic {user_id: $user_id})
        WHERE ANY(keyword IN $keywords WHERE toLower(t.name) CONTAINS keyword
                  OR toLower(t.description) CONTAINS keyword)
        RETURN t.name as name, t.mention_count as mention_count
        ORDER BY t.mention_count DESC
        LIMIT $limit
        """

        topics = await self.client.execute_query(
            topic_query,
            {"user_id": user_id, "keywords": keywords, "limit": limit},
        )

        # Find relevant concepts
        concept_query = """
        MATCH (c:Concept)
        WHERE ANY(keyword IN $keywords WHERE toLower(c.name) CONTAINS keyword)
        RETURN DISTINCT c.name as name, c.category as category
        LIMIT $limit
        """

        concepts = await self.client.execute_query(
            concept_query,
            {"keywords": keywords, "limit": limit},
        )

        return {
            "topics": topics,
            "concepts": concepts,
            "query": query_text,
        }
