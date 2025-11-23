"""Qdrant client wrapper for vector storage operations."""

from typing import Any

import structlog
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from src.config import get_settings

logger = structlog.get_logger()

# Collection configuration
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small dimension
DISTANCE_METRIC = models.Distance.COSINE

# Collection names
MEMORIES_COLLECTION = "memories"
DOCUMENTS_COLLECTION = "kb_documents"


class QdrantClientWrapper:
    """Async wrapper for Qdrant operations with error handling."""

    def __init__(self, url: str | None = None):
        """Initialize Qdrant client.

        Args:
            url: Qdrant server URL. If None, uses settings.
        """
        settings = get_settings()
        self.url = url or settings.qdrant_url
        self._client: AsyncQdrantClient | None = None

    async def _get_client(self) -> AsyncQdrantClient:
        """Get or create async Qdrant client."""
        if self._client is None:
            self._client = AsyncQdrantClient(url=self.url)
        return self._client

    async def close(self) -> None:
        """Close the client connection."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def ensure_collection(
        self,
        collection_name: str,
        vector_size: int = VECTOR_SIZE,
    ) -> bool:
        """Ensure a collection exists, creating it if necessary.

        Args:
            collection_name: Name of the collection
            vector_size: Dimension of vectors to store

        Returns:
            True if collection was created, False if it already existed
        """
        client = await self._get_client()

        try:
            collections = await client.get_collections()
            existing = [c.name for c in collections.collections]

            if collection_name in existing:
                logger.info("collection_exists", collection=collection_name)
                return False

            await client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=DISTANCE_METRIC,
                ),
            )
            logger.info("collection_created", collection=collection_name, vector_size=vector_size)
            return True

        except UnexpectedResponse as e:
            logger.error("ensure_collection_failed", collection=collection_name, error=str(e))
            raise

    async def upsert_point(
        self,
        collection_name: str,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> None:
        """Insert or update a point in a collection.

        Args:
            collection_name: Target collection
            point_id: Unique identifier for the point
            vector: Embedding vector
            payload: Metadata to store with the vector
        """
        client = await self._get_client()

        await client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )
        logger.debug("point_upserted", collection=collection_name, point_id=point_id)

    async def upsert_points_batch(
        self,
        collection_name: str,
        points: list[tuple[str, list[float], dict[str, Any]]],
        batch_size: int = 100,
    ) -> int:
        """Batch insert/update points.

        Args:
            collection_name: Target collection
            points: List of (point_id, vector, payload) tuples
            batch_size: Number of points per batch

        Returns:
            Number of points upserted
        """
        client = await self._get_client()
        total = 0

        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            point_structs = [
                models.PointStruct(id=pid, vector=vec, payload=pay)
                for pid, vec, pay in batch
            ]
            await client.upsert(
                collection_name=collection_name,
                points=point_structs,
            )
            total += len(batch)
            logger.debug("batch_upserted", collection=collection_name, batch_size=len(batch))

        return total

    async def search(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: float | None = None,
        filter_conditions: models.Filter | None = None,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Search for similar vectors.

        Args:
            collection_name: Collection to search
            query_vector: Query embedding
            limit: Maximum results to return
            score_threshold: Minimum similarity score (0-1 for cosine)
            filter_conditions: Optional Qdrant filter

        Returns:
            List of (point_id, score, payload) tuples
        """
        client = await self._get_client()

        # Use query_points (qdrant-client 1.16+ API)
        results = await client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=filter_conditions,
            with_payload=True,
        )

        return [
            (str(r.id), r.score, r.payload or {})
            for r in results.points
        ]

    async def get_point(
        self,
        collection_name: str,
        point_id: str,
    ) -> tuple[list[float], dict[str, Any]] | None:
        """Get a single point by ID.

        Args:
            collection_name: Collection name
            point_id: Point identifier

        Returns:
            (vector, payload) tuple or None if not found
        """
        client = await self._get_client()

        try:
            results = await client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_vectors=True,
                with_payload=True,
            )
            if results:
                point = results[0]
                return (point.vector, point.payload or {})  # type: ignore
            return None
        except UnexpectedResponse:
            return None

    async def delete_point(
        self,
        collection_name: str,
        point_id: str,
    ) -> bool:
        """Delete a point by ID.

        Args:
            collection_name: Collection name
            point_id: Point identifier

        Returns:
            True if deleted successfully
        """
        client = await self._get_client()

        try:
            await client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[point_id]),
            )
            logger.debug("point_deleted", collection=collection_name, point_id=point_id)
            return True
        except UnexpectedResponse as e:
            logger.error(
                "delete_failed",
                collection=collection_name,
                point_id=point_id,
                error=str(e),
            )
            return False

    async def delete_by_filter(
        self,
        collection_name: str,
        filter_conditions: models.Filter,
    ) -> int:
        """Delete points matching a filter.

        Args:
            collection_name: Collection name
            filter_conditions: Qdrant filter for points to delete

        Returns:
            Number of points deleted (approximate)
        """
        client = await self._get_client()

        # Get count before deletion
        count_before = await self.count_points(collection_name, filter_conditions)

        await client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(filter=filter_conditions),
        )

        logger.info("points_deleted_by_filter", collection=collection_name, count=count_before)
        return count_before

    async def count_points(
        self,
        collection_name: str,
        filter_conditions: models.Filter | None = None,
    ) -> int:
        """Count points in a collection.

        Args:
            collection_name: Collection name
            filter_conditions: Optional filter

        Returns:
            Number of points
        """
        client = await self._get_client()

        result = await client.count(
            collection_name=collection_name,
            count_filter=filter_conditions,
            exact=True,
        )
        return result.count

    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists."""
        client = await self._get_client()
        collections = await client.get_collections()
        return collection_name in [c.name for c in collections.collections]

    async def health_check(self) -> dict[str, Any]:
        """Check Qdrant health and return status info."""
        try:
            client = await self._get_client()
            collections = await client.get_collections()

            collection_info = {}
            for col in collections.collections:
                info = await client.get_collection(col.name)
                collection_info[col.name] = {
                    "vectors_count": info.vectors_count,
                    "points_count": info.points_count,
                }

            return {
                "status": "healthy",
                "url": self.url,
                "collections": collection_info,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "url": self.url,
                "error": str(e),
            }


# Singleton instance
_qdrant_client: QdrantClientWrapper | None = None


def get_qdrant_client() -> QdrantClientWrapper:
    """Get the singleton Qdrant client instance."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClientWrapper()
    return _qdrant_client


async def init_qdrant_collections() -> None:
    """Initialize required Qdrant collections on startup."""
    client = get_qdrant_client()

    # Create memories collection
    await client.ensure_collection(MEMORIES_COLLECTION)

    # Create documents collection
    await client.ensure_collection(DOCUMENTS_COLLECTION)

    logger.info("qdrant_collections_initialized")
