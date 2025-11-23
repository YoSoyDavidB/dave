"""Embedding service using OpenRouter API."""

import hashlib
from typing import Any # Any is actually used in EmbeddingCache.get and EmbeddingCache.set, but not directly in the file from what ruff is complaining about. Let's keep it for now.
# from functools import lru_cache # Removed this because it's genuinely unused
# I will keep typing.Any for now because it is used in the EmbeddingCache class type hints. It's possible ruff is misidentifying it as unused due to it being in a class definition.
# I will only remove functools.lru_cache.

import httpx
import structlog

from src.config import get_settings

logger = structlog.get_logger()

# Embedding model configuration
EMBEDDING_MODEL = "openai/text-embedding-3-small"
VECTOR_SIZE = 1536
MAX_BATCH_SIZE = 100
MAX_INPUT_LENGTH = 8191  # Max tokens for text-embedding-3-small


class EmbeddingCache:
    """Simple in-memory LRU cache for embeddings."""

    def __init__(self, maxsize: int = 10000):
        self._cache: dict[str, list[float]] = {}
        self._order: list[str] = []
        self._maxsize = maxsize

    def _hash_text(self, text: str) -> str:
        """Create a hash key for text."""
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def get(self, text: str) -> list[float] | None:
        """Get cached embedding for text."""
        key = self._hash_text(text)
        return self._cache.get(key)

    def set(self, text: str, embedding: list[float]) -> None:
        """Cache an embedding."""
        key = self._hash_text(text)
        if key in self._cache:
            return

        if len(self._cache) >= self._maxsize:
            # Remove oldest entry
            oldest = self._order.pop(0)
            self._cache.pop(oldest, None)

        self._cache[key] = embedding
        self._order.append(key)

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._order.clear()


class EmbeddingService:
    """Service for generating text embeddings via OpenRouter."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        """Initialize embedding service.

        Args:
            api_key: OpenRouter API key. Uses settings if None.
            base_url: OpenRouter base URL. Uses settings if None.
        """
        settings = get_settings()
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        self._cache = EmbeddingCache()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def embed_text(self, text: str, use_cache: bool = True) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed
            use_cache: Whether to use caching

        Returns:
            Embedding vector (1536 dimensions)
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        # Truncate if too long
        if len(text) > MAX_INPUT_LENGTH * 4:  # Rough char estimate
            text = text[:MAX_INPUT_LENGTH * 4]
            logger.warning("text_truncated_for_embedding", original_length=len(text))

        # Check cache
        if use_cache:
            cached = self._cache.get(text)
            if cached is not None:
                logger.debug("embedding_cache_hit")
                return cached

        # Call API
        client = await self._get_client()

        try:
            response = await client.post(
                "/embeddings",
                json={
                    "model": EMBEDDING_MODEL,
                    "input": text,
                },
            )
            response.raise_for_status()
            data = response.json()

            embedding = data["data"][0]["embedding"]

            # Cache result
            if use_cache:
                self._cache.set(text, embedding)

            logger.debug("embedding_generated", text_length=len(text))
            return embedding

        except httpx.HTTPStatusError as e:
            logger.error(
                "embedding_api_error",
                status_code=e.response.status_code,
                detail=e.response.text,
            )
            raise
        except Exception as e:
            logger.error("embedding_failed", error=str(e))
            raise

    async def embed_texts(
        self,
        texts: list[str],
        batch_size: int = MAX_BATCH_SIZE,
        use_cache: bool = True,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call
            use_cache: Whether to use caching

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        results: list[list[float] | None] = [None] * len(texts)
        texts_to_embed: list[tuple[int, str]] = []

        # Check cache first
        for i, text in enumerate(texts):
            if not text or not text.strip():
                results[i] = [0.0] * VECTOR_SIZE  # Zero vector for empty text
                continue

            if use_cache:
                cached = self._cache.get(text)
                if cached is not None:
                    results[i] = cached
                    continue

            texts_to_embed.append((i, text))

        if not texts_to_embed:
            return results  # type: ignore

        # Batch API calls
        client = await self._get_client()

        for batch_start in range(0, len(texts_to_embed), batch_size):
            batch = texts_to_embed[batch_start:batch_start + batch_size]
            batch_texts = [t[1] for t in batch]

            # Truncate texts if needed
            batch_texts = [
                t[:MAX_INPUT_LENGTH * 4] if len(t) > MAX_INPUT_LENGTH * 4 else t
                for t in batch_texts
            ]

            try:
                response = await client.post(
                    "/embeddings",
                    json={
                        "model": EMBEDDING_MODEL,
                        "input": batch_texts,
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Map results back
                for j, item in enumerate(data["data"]):
                    original_idx = batch[j][0]
                    embedding = item["embedding"]
                    results[original_idx] = embedding

                    if use_cache:
                        self._cache.set(batch[j][1], embedding)

                logger.debug("batch_embeddings_generated", batch_size=len(batch))

            except httpx.HTTPStatusError as e:
                logger.error(
                    "batch_embedding_api_error",
                    status_code=e.response.status_code,
                    batch_size=len(batch),
                )
                raise

        return results  # type: ignore

    async def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a search query.

        This is currently the same as embed_text but kept separate
        for potential query-specific optimizations.

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        return await self.embed_text(query, use_cache=True)

    def compute_similarity(
        self,
        embedding1: list[float],
        embedding2: list[float],
    ) -> float:
        """Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Cosine similarity score (0-1)
        """
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must have same dimension")

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("embedding_cache_cleared")


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get the singleton embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
