"""Graph models for Neo4j knowledge graph."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RelationType(str, Enum):
    """Types of relationships in the knowledge graph."""

    # Memory relationships
    RELATES_TO = "RELATES_TO"  # General semantic relation between memories
    LEADS_TO = "LEADS_TO"  # One memory leads to another (temporal/causal)
    CONTRADICTS = "CONTRADICTS"  # Memories that contradict each other
    UPDATES = "UPDATES"  # New memory updates/refines old memory

    # Topic relationships
    DISCUSSES = "DISCUSSES"  # Memory discusses a topic
    SUBTOPIC_OF = "SUBTOPIC_OF"  # Topic is a subtopic of another
    EVOLVED_INTO = "EVOLVED_INTO"  # Topic evolved into another topic

    # Concept relationships
    MENTIONS = "MENTIONS"  # Memory mentions a concept
    RELATED_CONCEPT = "RELATED_CONCEPT"  # Concepts that are related
    IS_A = "IS_A"  # Concept is a type of another concept


class GraphNode(BaseModel):
    """Base model for graph nodes."""

    node_id: str  # Unique identifier
    labels: list[str]  # Node labels (e.g., ["Memory", "Preference"])
    properties: dict[str, Any] = Field(default_factory=dict)

    def to_cypher_props(self) -> str:
        """Convert properties to Cypher property string.

        Returns:
            String like: {prop1: $prop1, prop2: $prop2, ...}
        """
        if not self.properties:
            return "{}"

        prop_assignments = [f"{key}: ${key}" for key in self.properties.keys()]
        return "{" + ", ".join(prop_assignments) + "}"


class MemoryNode(GraphNode):
    """Graph node representing a user memory.

    This connects to the Memory stored in Qdrant, adding graph relationships
    to enable contextual retrieval.
    """

    def __init__(
        self,
        memory_id: UUID,
        user_id: str,
        short_text: str,
        memory_type: str,
        timestamp: datetime,
        relevance_score: float = 1.0,
        **kwargs: Any,
    ):
        super().__init__(
            node_id=str(memory_id),
            labels=["Memory", memory_type.capitalize()],
            properties={
                "memory_id": str(memory_id),
                "user_id": user_id,
                "short_text": short_text,
                "memory_type": memory_type,
                "timestamp": timestamp.isoformat(),
                "relevance_score": relevance_score,
                **kwargs,
            },
        )


class TopicNode(GraphNode):
    """Graph node representing a conversation topic."""

    def __init__(
        self,
        user_id: str,
        name: str,
        description: str = "",
        first_mentioned: datetime | None = None,
        last_mentioned: datetime | None = None,
        mention_count: int = 1,
    ):
        now = datetime.now(UTC)
        super().__init__(
            node_id=f"{user_id}:{name}",
            labels=["Topic"],
            properties={
                "user_id": user_id,
                "name": name,
                "description": description,
                "first_mentioned": (first_mentioned or now).isoformat(),
                "last_mentioned": (last_mentioned or now).isoformat(),
                "mention_count": mention_count,
            },
        )


class ConceptNode(GraphNode):
    """Graph node representing a concept extracted from conversations."""

    def __init__(
        self,
        name: str,
        category: str = "general",
        description: str = "",
        first_seen: datetime | None = None,
    ):
        super().__init__(
            node_id=name.lower().replace(" ", "_"),
            labels=["Concept", category.capitalize()],
            properties={
                "name": name,
                "category": category,
                "description": description,
                "first_seen": (first_seen or datetime.now(UTC)).isoformat(),
            },
        )


class GraphRelationship(BaseModel):
    """Model for graph relationships between nodes."""

    from_node: str  # Node ID
    to_node: str  # Node ID
    rel_type: RelationType
    properties: dict[str, Any] = Field(default_factory=dict)

    def to_cypher(self) -> str:
        """Convert to Cypher relationship syntax.

        Returns:
            String like: -[r:REL_TYPE {prop: value}]->
        """
        if not self.properties:
            return f"-[:{self.rel_type.value}]->"

        props = ", ".join([f"{k}: ${k}" for k in self.properties.keys()])
        return f"-[:{self.rel_type.value} {{{props}}}]->"


class MemoryGraph(BaseModel):
    """Complete memory graph including nodes and relationships."""

    memories: list[MemoryNode] = Field(default_factory=list)
    topics: list[TopicNode] = Field(default_factory=list)
    concepts: list[ConceptNode] = Field(default_factory=list)
    relationships: list[GraphRelationship] = Field(default_factory=list)

    def add_memory_relation(
        self,
        from_memory_id: UUID,
        to_memory_id: UUID,
        rel_type: RelationType,
        strength: float = 1.0,
        reason: str = "",
    ) -> None:
        """Add a relationship between two memories.

        Args:
            from_memory_id: Source memory ID
            to_memory_id: Target memory ID
            rel_type: Type of relationship
            strength: Relationship strength (0.0-1.0)
            reason: Optional explanation of the relationship
        """
        self.relationships.append(
            GraphRelationship(
                from_node=str(from_memory_id),
                to_node=str(to_memory_id),
                rel_type=rel_type,
                properties={
                    "strength": strength,
                    "reason": reason,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )
        )

    def add_memory_topic(
        self,
        memory_id: UUID,
        topic_name: str,
        relevance: float = 1.0,
    ) -> None:
        """Link a memory to a topic.

        Args:
            memory_id: Memory ID
            topic_name: Topic name
            relevance: How relevant the memory is to the topic
        """
        self.relationships.append(
            GraphRelationship(
                from_node=str(memory_id),
                to_node=topic_name,
                rel_type=RelationType.DISCUSSES,
                properties={
                    "relevance": relevance,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )
        )

    def add_memory_concept(
        self,
        memory_id: UUID,
        concept_name: str,
        sentiment: str = "neutral",
    ) -> None:
        """Link a memory to a concept.

        Args:
            memory_id: Memory ID
            concept_name: Concept name
            sentiment: User's sentiment about the concept (positive/negative/neutral)
        """
        concept_id = concept_name.lower().replace(" ", "_")
        self.relationships.append(
            GraphRelationship(
                from_node=str(memory_id),
                to_node=concept_id,
                rel_type=RelationType.MENTIONS,
                properties={
                    "sentiment": sentiment,
                    "created_at": datetime.now(UTC).isoformat(),
                },
            )
        )
