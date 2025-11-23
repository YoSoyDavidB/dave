"""Tests for the embedding service."""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.infrastructure.embeddings.embedding_service import (
    EMBEDDING_MODEL,
    VECTOR_SIZE,
    EmbeddingCache,
    EmbeddingService,
)


@pytest.fixture
def embedding_service():
    """Create an EmbeddingService instance."""
    return EmbeddingService(api_key="test-key", base_url="https://api.test.com")


@pytest.fixture
def mock_response():
    """Create a mock embedding API response."""
    return {
        "data": [
            {"embedding": [0.1] * VECTOR_SIZE}
        ]
    }


class TestEmbeddingCache:
    """Tests for EmbeddingCache."""

    def test_cache_set_and_get(self):
        """Test setting and getting cached embeddings."""
        cache = EmbeddingCache(maxsize=100)

        embedding = [0.1] * VECTOR_SIZE
        cache.set("test text", embedding)

        result = cache.get("test text")
        assert result == embedding

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = EmbeddingCache()

        result = cache.get("nonexistent")
        assert result is None

    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = EmbeddingCache(maxsize=2)

        cache.set("text1", [0.1] * VECTOR_SIZE)
        cache.set("text2", [0.2] * VECTOR_SIZE)
        cache.set("text3", [0.3] * VECTOR_SIZE)  # Should evict text1

        assert cache.get("text1") is None
        assert cache.get("text2") is not None
        assert cache.get("text3") is not None

    def test_cache_clear(self):
        """Test clearing the cache."""
        cache = EmbeddingCache()

        cache.set("text", [0.1] * VECTOR_SIZE)
        cache.clear()

        assert cache.get("text") is None

    def test_cache_no_duplicate_entries(self):
        """Test that setting same key twice doesn't create duplicates."""
        cache = EmbeddingCache(maxsize=2)

        embedding1 = [0.1] * VECTOR_SIZE
        cache.set("text", embedding1)
        cache.set("text", [0.2] * VECTOR_SIZE)  # Should not update

        # Should still have original value
        result = cache.get("text")
        assert result == embedding1


class TestEmbeddingService:
    """Tests for EmbeddingService."""

    @pytest.mark.asyncio
    async def test_embed_text_success(self, embedding_service, mock_response):
        """Test successful text embedding."""
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        with patch.object(embedding_service, "_get_client", return_value=mock_client):
            result = await embedding_service.embed_text("test text", use_cache=False)

            assert len(result) == VECTOR_SIZE
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_text_with_cache(self, embedding_service, mock_response):
        """Test embedding with cache."""
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        with patch.object(embedding_service, "_get_client", return_value=mock_client):
            # First call should hit API
            result1 = await embedding_service.embed_text("cached text")
            assert mock_client.post.call_count == 1

            # Second call should use cache
            result2 = await embedding_service.embed_text("cached text")
            assert mock_client.post.call_count == 1  # Still 1

            assert result1 == result2

    @pytest.mark.asyncio
    async def test_embed_text_empty_raises(self, embedding_service):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Cannot embed empty text"):
            await embedding_service.embed_text("")

        with pytest.raises(ValueError, match="Cannot embed empty text"):
            await embedding_service.embed_text("   ")

    @pytest.mark.asyncio
    async def test_embed_texts_batch(self, embedding_service):
        """Test batch embedding."""
        mock_response = {
            "data": [
                {"embedding": [0.1] * VECTOR_SIZE},
                {"embedding": [0.2] * VECTOR_SIZE},
            ]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        with patch.object(embedding_service, "_get_client", return_value=mock_client):
            results = await embedding_service.embed_texts(
                ["text1", "text2"],
                use_cache=False,
            )

            assert len(results) == 2
            assert all(len(r) == VECTOR_SIZE for r in results)

    @pytest.mark.asyncio
    async def test_embed_texts_empty_list(self, embedding_service):
        """Test embedding empty list returns empty list."""
        results = await embedding_service.embed_texts([])
        assert results == []

    @pytest.mark.asyncio
    async def test_embed_texts_with_empty_strings(self, embedding_service):
        """Test batch with empty strings returns zero vectors."""
        mock_response = {
            "data": [
                {"embedding": [0.1] * VECTOR_SIZE},
            ]
        }

        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        with patch.object(embedding_service, "_get_client", return_value=mock_client):
            results = await embedding_service.embed_texts(
                ["", "valid text", ""],
                use_cache=False,
            )

            assert len(results) == 3
            # Empty strings get zero vectors
            assert results[0] == [0.0] * VECTOR_SIZE
            assert results[2] == [0.0] * VECTOR_SIZE
            # Valid text gets real embedding
            assert results[1] != [0.0] * VECTOR_SIZE

    @pytest.mark.asyncio
    async def test_embed_query(self, embedding_service, mock_response):
        """Test query embedding."""
        mock_client = AsyncMock()
        mock_client.post.return_value = MagicMock(
            json=lambda: mock_response,
            raise_for_status=lambda: None,
        )

        with patch.object(embedding_service, "_get_client", return_value=mock_client):
            result = await embedding_service.embed_query("search query")

            assert len(result) == VECTOR_SIZE

    def test_compute_similarity(self, embedding_service):
        """Test cosine similarity computation."""
        # Same vector should have similarity 1.0
        vec = [1.0, 0.0, 0.0]
        assert embedding_service.compute_similarity(vec, vec) == pytest.approx(1.0)

        # Orthogonal vectors should have similarity 0.0
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        assert embedding_service.compute_similarity(vec1, vec2) == pytest.approx(0.0)

        # Opposite vectors should have similarity -1.0
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 0.0, 0.0]
        assert embedding_service.compute_similarity(vec1, vec2) == pytest.approx(-1.0)

    def test_compute_similarity_dimension_mismatch(self, embedding_service):
        """Test similarity with mismatched dimensions raises."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        with pytest.raises(ValueError, match="same dimension"):
            embedding_service.compute_similarity(vec1, vec2)

    def test_compute_similarity_zero_vector(self, embedding_service):
        """Test similarity with zero vector returns 0."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 0.0, 0.0]

        assert embedding_service.compute_similarity(vec1, vec2) == 0.0

    def test_clear_cache(self, embedding_service):
        """Test clearing the cache."""
        embedding_service._cache.set("test", [0.1] * VECTOR_SIZE)
        embedding_service.clear_cache()

        assert embedding_service._cache.get("test") is None

    @pytest.mark.asyncio
    async def test_api_error_handling(self, embedding_service):
        """Test API error handling."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limited"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Rate limited",
            request=MagicMock(),
            response=mock_response,
        )
        mock_client.post.return_value = mock_response

        with patch.object(embedding_service, "_get_client", return_value=mock_client):
            with pytest.raises(httpx.HTTPStatusError):
                await embedding_service.embed_text("test", use_cache=False)


class TestEmbeddingModel:
    """Tests for embedding model configuration."""

    def test_model_name(self):
        """Verify embedding model is configured correctly."""
        assert EMBEDDING_MODEL == "openai/text-embedding-3-small"

    def test_vector_size(self):
        """Verify vector size matches model output."""
        assert VECTOR_SIZE == 1536
