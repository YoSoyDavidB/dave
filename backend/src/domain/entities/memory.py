"""Memory entity for long-term user memory storage."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memories that can be stored."""

    PREFERENCE = "preference"  # User preferences (e.g., "prefers concise answers")
    FACT = "fact"              # Factual info (e.g., "is a software engineer")
    TASK = "task"              # Tasks/todos (e.g., "wants to learn Rust")
    GOAL = "goal"              # Long-term goals (e.g., "building a startup")
    PROFILE = "profile"        # Profile info (e.g., "name is David")


class Memory(BaseModel):
    """A memory extracted from user conversations.

    Memories represent information about the user that Dave should remember
    across conversations. They are stored as vectors in Qdrant for semantic
    retrieval.
    """

    memory_id: UUID = Field(default_factory=uuid4)
    user_id: str
    short_text: str = Field(max_length=500)
    memory_type: MemoryType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    last_referenced_at: datetime = Field(default_factory=datetime.utcnow)
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    num_times_referenced: int = Field(default=0, ge=0)
    source: str = ""  # conversation_id or file path
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Embedding is stored separately in Qdrant, not in the model
    # This is just for passing around during creation
    embedding: list[float] | None = Field(default=None, exclude=True)

    def mark_referenced(self) -> None:
        """Mark this memory as referenced, updating counters."""
        self.num_times_referenced += 1
        self.last_referenced_at = datetime.utcnow()

    def decay_relevance(self, decay_factor: float = 0.95) -> None:
        """Apply decay to relevance score.

        Args:
            decay_factor: Multiplier for relevance (0.95 = 5% decay)
        """
        self.relevance_score = max(0.0, self.relevance_score * decay_factor)

    def boost_relevance(self, boost: float = 0.1) -> None:
        """Boost relevance score when memory is used.

        Args:
            boost: Amount to add to relevance (capped at 1.0)
        """
        self.relevance_score = min(1.0, self.relevance_score + boost)

    def is_stale(self, days_threshold: int = 90) -> bool:
        """Check if memory hasn't been referenced in a while.

        Args:
            days_threshold: Days without reference to consider stale

        Returns:
            True if memory is stale
        """
        threshold = datetime.utcnow() - timedelta(days=days_threshold)
        return self.last_referenced_at < threshold

    def should_consolidate(self) -> bool:
        """Determine if this memory should be kept during consolidation.

        Memories are kept if:
        - Referenced 5+ times, OR
        - Relevance score > 0.7, OR
        - Type is PREFERENCE or PROFILE (always kept)

        Returns:
            True if memory should be kept
        """
        if self.memory_type in (MemoryType.PREFERENCE, MemoryType.PROFILE):
            return True
        if self.num_times_referenced >= 5:
            return True
        if self.relevance_score > 0.7:
            return True
        return False

    def to_payload(self) -> dict[str, Any]:
        """Convert to Qdrant payload format.

        Returns:
            Dict suitable for Qdrant point payload
        """
        return {
            "memory_id": str(self.memory_id),
            "user_id": self.user_id,
            "short_text": self.short_text,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp.isoformat(),
            "last_referenced_at": self.last_referenced_at.isoformat(),
            "relevance_score": self.relevance_score,
            "num_times_referenced": self.num_times_referenced,
            "source": self.source,
            "metadata": self.metadata,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Memory":
        """Create Memory from Qdrant payload.

        Args:
            payload: Qdrant point payload

        Returns:
            Memory instance
        """
        return cls(
            memory_id=UUID(payload["memory_id"]),
            user_id=payload["user_id"],
            short_text=payload["short_text"],
            memory_type=MemoryType(payload["memory_type"]),
            timestamp=datetime.fromisoformat(payload["timestamp"]),
            last_referenced_at=datetime.fromisoformat(payload["last_referenced_at"]),
            relevance_score=payload["relevance_score"],
            num_times_referenced=payload["num_times_referenced"],
            source=payload.get("source", ""),
            metadata=payload.get("metadata", {}),
        )

    def __str__(self) -> str:
        return f"[{self.memory_type.value}] {self.short_text}"

    def __repr__(self) -> str:
        return f"Memory(id={self.memory_id}, type={self.memory_type.value}, text='{self.short_text[:30]}...')"
