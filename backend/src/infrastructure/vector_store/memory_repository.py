"""Memory repository implementation using Qdrant."""

from datetime import datetime
from typing import Any
from uuid import UUID

import structlog
from qdrant_client.http import models

from src.domain.entities.memory import Memory, MemoryType
from src.infrastructure.embeddings import get_embedding_service
from src.infrastructure.vector_store.qdrant_client import (
    MEMORIES_COLLECTION,
    get_qdrant_client,
)

logger = structlog.get_logger()


class MemoryRepository:
    """Repository for storing and retrieving user memories from Qdrant."""

    def __init__(self):
        self._qdrant = get_qdrant_client()
        self._embeddings = get_embedding_service()

    async def create(self, memory: Memory) -> Memory:
        """Create a new memory with embedding.

        Args:
            memory: Memory to store (embedding will be generated if not provided)

        Returns:
            Stored memory with ID
        """
        # Generate embedding if not provided
        if memory.embedding is None:
            memory.embedding = await self._embeddings.embed_text(memory.short_text)

        # Store in Qdrant
        await self._qdrant.upsert_point(
            collection_name=MEMORIES_COLLECTION,
            point_id=str(memory.memory_id),
            vector=memory.embedding,
            payload=memory.to_payload(),
        )

        logger.info(
            "memory_created",
            memory_id=str(memory.memory_id),
            memory_type=memory.memory_type.value,
            user_id=memory.user_id,
        )

        return memory

    async def bulk_create(self, memories: list[Memory]) -> list[Memory]:
        """Create multiple memories efficiently.

        Args:
            memories: List of memories to store

        Returns:
            List of stored memories
        """
        if not memories:
            return []

        # Generate embeddings for memories that don't have them
        texts_to_embed = []
        indices_to_embed = []

        for i, mem in enumerate(memories):
            if mem.embedding is None:
                texts_to_embed.append(mem.short_text)
                indices_to_embed.append(i)

        if texts_to_embed:
            embeddings = await self._embeddings.embed_texts(texts_to_embed)
            for idx, embedding in zip(indices_to_embed, embeddings):
                memories[idx].embedding = embedding

        # Prepare points for batch upsert
        points = [
            (str(mem.memory_id), mem.embedding, mem.to_payload())
            for mem in memories
            if mem.embedding is not None
        ]

        await self._qdrant.upsert_points_batch(
            collection_name=MEMORIES_COLLECTION,
            points=points,
        )

        logger.info("memories_bulk_created", count=len(memories))
        return memories

    async def get_by_id(self, memory_id: UUID) -> Memory | None:
        """Get a memory by ID.

        Args:
            memory_id: Memory UUID

        Returns:
            Memory if found, None otherwise
        """
        result = await self._qdrant.get_point(
            collection_name=MEMORIES_COLLECTION,
            point_id=str(memory_id),
        )

        if result is None:
            return None

        _, payload = result
        return Memory.from_payload(payload)

    async def update(self, memory: Memory) -> Memory:
        """Update an existing memory.

        Args:
            memory: Memory with updated fields

        Returns:
            Updated memory
        """
        # Re-embed if text changed (check via metadata or always re-embed)
        memory.embedding = await self._embeddings.embed_text(memory.short_text)

        await self._qdrant.upsert_point(
            collection_name=MEMORIES_COLLECTION,
            point_id=str(memory.memory_id),
            vector=memory.embedding,
            payload=memory.to_payload(),
        )

        logger.debug("memory_updated", memory_id=str(memory.memory_id))
        return memory

    async def delete(self, memory_id: UUID) -> bool:
        """Delete a memory.

        Args:
            memory_id: Memory UUID to delete

        Returns:
            True if deleted
        """
        return await self._qdrant.delete_point(
            collection_name=MEMORIES_COLLECTION,
            point_id=str(memory_id),
        )

    async def search_similar(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
        min_score: float = 0.7,
        memory_types: list[MemoryType] | None = None,
    ) -> list[tuple[Memory, float]]:
        """Search for similar memories.

        Args:
            query: Search query text
            user_id: Filter by user
            limit: Maximum results
            min_score: Minimum similarity score
            memory_types: Optional filter by memory types

        Returns:
            List of (Memory, score) tuples
        """
        # Generate query embedding
        query_embedding = await self._embeddings.embed_query(query)

        # Build filter
        must_conditions = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]

        if memory_types:
            must_conditions.append(
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchAny(any=[mt.value for mt in memory_types]),
                )
            )

        filter_conditions = models.Filter(must=must_conditions)

        # Search
        results = await self._qdrant.search(
            collection_name=MEMORIES_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=min_score,
            filter_conditions=filter_conditions,
        )

        # Convert to Memory objects
        memories = []
        for point_id, score, payload in results:
            memory = Memory.from_payload(payload)
            memories.append((memory, score))

        logger.debug(
            "memories_searched",
            query_length=len(query),
            user_id=user_id,
            results_count=len(memories),
        )

        return memories

    async def get_by_user(
        self,
        user_id: str,
        limit: int = 100,
        memory_types: list[MemoryType] | None = None,
    ) -> list[Memory]:
        """Get all memories for a user.

        Args:
            user_id: User ID
            limit: Maximum results
            memory_types: Optional filter by types

        Returns:
            List of memories
        """
        must_conditions = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]

        if memory_types:
            must_conditions.append(
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchAny(any=[mt.value for mt in memory_types]),
                )
            )

        filter_conditions = models.Filter(must=must_conditions)

        # Use scroll to get all points matching filter
        client = await self._qdrant._get_client()
        results, _ = await client.scroll(
            collection_name=MEMORIES_COLLECTION,
            scroll_filter=filter_conditions,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        return [Memory.from_payload(point.payload) for point in results]

    async def mark_referenced(self, memory_id: UUID) -> Memory | None:
        """Mark a memory as referenced and boost relevance.

        Args:
            memory_id: Memory to update

        Returns:
            Updated memory or None if not found
        """
        memory = await self.get_by_id(memory_id)
        if memory is None:
            return None

        memory.mark_referenced()
        memory.boost_relevance()

        # Update payload only (no need to re-embed)
        client = await self._qdrant._get_client()
        await client.set_payload(
            collection_name=MEMORIES_COLLECTION,
            payload=memory.to_payload(),
            points=[str(memory_id)],
        )

        return memory

    async def decay_all_relevance(
        self,
        user_id: str,
        decay_factor: float = 0.95,
    ) -> int:
        """Apply decay to all user memories.

        Args:
            user_id: User whose memories to decay
            decay_factor: Decay multiplier

        Returns:
            Number of memories updated
        """
        memories = await self.get_by_user(user_id)
        updated = 0

        client = await self._qdrant._get_client()

        for memory in memories:
            old_score = memory.relevance_score
            memory.decay_relevance(decay_factor)

            if memory.relevance_score != old_score:
                await client.set_payload(
                    collection_name=MEMORIES_COLLECTION,
                    payload={"relevance_score": memory.relevance_score},
                    points=[str(memory.memory_id)],
                )
                updated += 1

        logger.info(
            "relevance_decayed",
            user_id=user_id,
            updated_count=updated,
            decay_factor=decay_factor,
        )

        return updated

    async def delete_stale(
        self,
        user_id: str,
        days_threshold: int = 90,
    ) -> int:
        """Delete stale memories that should not be consolidated.

        Args:
            user_id: User whose memories to clean
            days_threshold: Days without reference to consider stale

        Returns:
            Number of memories deleted
        """
        memories = await self.get_by_user(user_id)
        deleted = 0

        for memory in memories:
            if memory.is_stale(days_threshold) and not memory.should_consolidate():
                await self.delete(memory.memory_id)
                deleted += 1
                logger.debug(
                    "stale_memory_deleted",
                    memory_id=str(memory.memory_id),
                    last_referenced=memory.last_referenced_at.isoformat(),
                )

        logger.info(
            "stale_memories_cleaned",
            user_id=user_id,
            deleted_count=deleted,
            threshold_days=days_threshold,
        )

        return deleted

    async def count_by_user(self, user_id: str) -> int:
        """Count memories for a user.

        Args:
            user_id: User ID

        Returns:
            Memory count
        """
        filter_conditions = models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=user_id),
                )
            ]
        )

        return await self._qdrant.count_points(
            collection_name=MEMORIES_COLLECTION,
            filter_conditions=filter_conditions,
        )


# Singleton instance
_memory_repository: MemoryRepository | None = None


def get_memory_repository() -> MemoryRepository:
    """Get the singleton memory repository instance."""
    global _memory_repository
    if _memory_repository is None:
        _memory_repository = MemoryRepository()
    return _memory_repository
