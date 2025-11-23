"""Tests for the Qdrant client wrapper."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.vector_store.qdrant_client import (
    DOCUMENTS_COLLECTION,
    MEMORIES_COLLECTION,
    VECTOR_SIZE,
    QdrantClientWrapper,
)


@pytest.fixture
def mock_qdrant():
    """Create a mock AsyncQdrantClient."""
    return AsyncMock()


@pytest.fixture
def client_wrapper():
    """Create a QdrantClientWrapper instance."""
    return QdrantClientWrapper(url="http://localhost:6333")


class TestQdrantClientWrapper:
    """Tests for QdrantClientWrapper."""

    @pytest.mark.asyncio
    async def test_ensure_collection_creates_new(self, client_wrapper, mock_qdrant):
        """Test creating a new collection."""
        mock_qdrant.get_collections.return_value = MagicMock(collections=[])
        mock_qdrant.create_collection = AsyncMock()

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            result = await client_wrapper.ensure_collection("test_collection")

            assert result is True
            mock_qdrant.create_collection.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_collection_already_exists(self, client_wrapper, mock_qdrant):
        """Test when collection already exists."""
        existing = MagicMock()
        existing.name = "test_collection"
        mock_qdrant.get_collections.return_value = MagicMock(collections=[existing])

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            result = await client_wrapper.ensure_collection("test_collection")

            assert result is False
            mock_qdrant.create_collection.assert_not_called()

    @pytest.mark.asyncio
    async def test_upsert_point(self, client_wrapper, mock_qdrant):
        """Test upserting a point."""
        mock_qdrant.upsert = AsyncMock()

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            await client_wrapper.upsert_point(
                collection_name="test",
                point_id="point-1",
                vector=[0.1] * VECTOR_SIZE,
                payload={"text": "test"},
            )

            mock_qdrant.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_search(self, client_wrapper, mock_qdrant):
        """Test searching for vectors."""
        mock_result = MagicMock()
        mock_result.id = "point-1"
        mock_result.score = 0.95
        mock_result.payload = {"text": "found"}

        mock_qdrant.search.return_value = [mock_result]

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            results = await client_wrapper.search(
                collection_name="test",
                query_vector=[0.1] * VECTOR_SIZE,
                limit=5,
            )

            assert len(results) == 1
            assert results[0][0] == "point-1"
            assert results[0][1] == 0.95
            assert results[0][2]["text"] == "found"

    @pytest.mark.asyncio
    async def test_search_with_threshold(self, client_wrapper, mock_qdrant):
        """Test search with score threshold."""
        mock_qdrant.search.return_value = []

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            results = await client_wrapper.search(
                collection_name="test",
                query_vector=[0.1] * VECTOR_SIZE,
                limit=5,
                score_threshold=0.8,
            )

            assert len(results) == 0
            # Verify threshold was passed
            call_args = mock_qdrant.search.call_args
            assert call_args.kwargs["score_threshold"] == 0.8

    @pytest.mark.asyncio
    async def test_get_point(self, client_wrapper, mock_qdrant):
        """Test getting a point by ID."""
        mock_point = MagicMock()
        mock_point.vector = [0.1] * VECTOR_SIZE
        mock_point.payload = {"text": "test"}

        mock_qdrant.retrieve.return_value = [mock_point]

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            result = await client_wrapper.get_point("test", "point-1")

            assert result is not None
            assert result[1]["text"] == "test"

    @pytest.mark.asyncio
    async def test_get_point_not_found(self, client_wrapper, mock_qdrant):
        """Test getting a non-existent point."""
        mock_qdrant.retrieve.return_value = []

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            result = await client_wrapper.get_point("test", "nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_delete_point(self, client_wrapper, mock_qdrant):
        """Test deleting a point."""
        mock_qdrant.delete = AsyncMock()

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            result = await client_wrapper.delete_point("test", "point-1")

            assert result is True
            mock_qdrant.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_batch(self, client_wrapper, mock_qdrant):
        """Test batch upsert."""
        mock_qdrant.upsert = AsyncMock()

        points = [
            (f"point-{i}", [0.1] * VECTOR_SIZE, {"index": i})
            for i in range(5)
        ]

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            count = await client_wrapper.upsert_points_batch(
                collection_name="test",
                points=points,
                batch_size=2,
            )

            assert count == 5
            # Should be called 3 times (2+2+1)
            assert mock_qdrant.upsert.call_count == 3

    @pytest.mark.asyncio
    async def test_count_points(self, client_wrapper, mock_qdrant):
        """Test counting points."""
        mock_qdrant.count.return_value = MagicMock(count=42)

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            count = await client_wrapper.count_points("test")

            assert count == 42

    @pytest.mark.asyncio
    async def test_collection_exists(self, client_wrapper, mock_qdrant):
        """Test checking if collection exists."""
        existing = MagicMock()
        existing.name = "memories"
        mock_qdrant.get_collections.return_value = MagicMock(collections=[existing])

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            assert await client_wrapper.collection_exists("memories") is True
            assert await client_wrapper.collection_exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, client_wrapper, mock_qdrant):
        """Test health check when healthy."""
        col1 = MagicMock()
        col1.name = MEMORIES_COLLECTION
        mock_qdrant.get_collections.return_value = MagicMock(collections=[col1])

        col_info = MagicMock()
        col_info.vectors_count = 100
        col_info.points_count = 100
        mock_qdrant.get_collection.return_value = col_info

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            health = await client_wrapper.health_check()

            assert health["status"] == "healthy"
            assert MEMORIES_COLLECTION in health["collections"]

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, client_wrapper, mock_qdrant):
        """Test health check when unhealthy."""
        mock_qdrant.get_collections.side_effect = Exception("Connection failed")

        with patch.object(client_wrapper, "_get_client", return_value=mock_qdrant):
            health = await client_wrapper.health_check()

            assert health["status"] == "unhealthy"
            assert "error" in health


class TestCollectionNames:
    """Tests for collection name constants."""

    def test_collection_names(self):
        """Verify collection names are defined."""
        assert MEMORIES_COLLECTION == "memories"
        assert DOCUMENTS_COLLECTION == "kb_documents"

    def test_vector_size(self):
        """Verify vector size matches OpenAI embedding model."""
        assert VECTOR_SIZE == 1536
