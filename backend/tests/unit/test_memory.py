"""Tests for the memory system."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.domain.entities.memory import Memory, MemoryType


class TestMemoryEntity:
    """Tests for Memory entity."""

    def test_create_memory(self):
        """Test creating a memory."""
        memory = Memory(
            user_id="user-123",
            short_text="User prefers concise answers",
            memory_type=MemoryType.PREFERENCE,
        )

        assert memory.user_id == "user-123"
        assert memory.short_text == "User prefers concise answers"
        assert memory.memory_type == MemoryType.PREFERENCE
        assert memory.relevance_score == 1.0
        assert memory.num_times_referenced == 0

    def test_mark_referenced(self):
        """Test marking memory as referenced."""
        memory = Memory(
            user_id="user-123",
            short_text="Test memory",
            memory_type=MemoryType.FACT,
        )

        old_timestamp = memory.last_referenced_at
        memory.mark_referenced()

        assert memory.num_times_referenced == 1
        assert memory.last_referenced_at >= old_timestamp

    def test_decay_relevance(self):
        """Test relevance decay."""
        memory = Memory(
            user_id="user-123",
            short_text="Test memory",
            memory_type=MemoryType.FACT,
            relevance_score=1.0,
        )

        memory.decay_relevance(0.95)
        assert memory.relevance_score == pytest.approx(0.95)

        memory.decay_relevance(0.95)
        assert memory.relevance_score == pytest.approx(0.9025)

    def test_decay_relevance_minimum(self):
        """Test relevance doesn't go below 0."""
        memory = Memory(
            user_id="user-123",
            short_text="Test memory",
            memory_type=MemoryType.FACT,
            relevance_score=0.01,
        )

        # Apply extreme decay
        for _ in range(100):
            memory.decay_relevance(0.5)

        assert memory.relevance_score >= 0.0

    def test_boost_relevance(self):
        """Test relevance boost."""
        memory = Memory(
            user_id="user-123",
            short_text="Test memory",
            memory_type=MemoryType.FACT,
            relevance_score=0.8,
        )

        memory.boost_relevance(0.1)
        assert memory.relevance_score == pytest.approx(0.9)

    def test_boost_relevance_maximum(self):
        """Test relevance doesn't exceed 1.0."""
        memory = Memory(
            user_id="user-123",
            short_text="Test memory",
            memory_type=MemoryType.FACT,
            relevance_score=0.95,
        )

        memory.boost_relevance(0.2)
        assert memory.relevance_score == 1.0

    def test_is_stale(self):
        """Test stale detection."""
        # Recent memory is not stale
        recent = Memory(
            user_id="user-123",
            short_text="Recent memory",
            memory_type=MemoryType.FACT,
        )
        assert recent.is_stale(90) is False

        # Old memory is stale
        old = Memory(
            user_id="user-123",
            short_text="Old memory",
            memory_type=MemoryType.FACT,
            last_referenced_at=datetime.utcnow() - timedelta(days=100),
        )
        assert old.is_stale(90) is True

    def test_should_consolidate_preference(self):
        """Test that preferences are always consolidated."""
        memory = Memory(
            user_id="user-123",
            short_text="User preference",
            memory_type=MemoryType.PREFERENCE,
            relevance_score=0.1,  # Low score
            num_times_referenced=0,  # Never referenced
        )
        assert memory.should_consolidate() is True

    def test_should_consolidate_profile(self):
        """Test that profile info is always consolidated."""
        memory = Memory(
            user_id="user-123",
            short_text="User name is David",
            memory_type=MemoryType.PROFILE,
            relevance_score=0.1,
            num_times_referenced=0,
        )
        assert memory.should_consolidate() is True

    def test_should_consolidate_frequently_referenced(self):
        """Test that frequently referenced memories are consolidated."""
        memory = Memory(
            user_id="user-123",
            short_text="Frequently used fact",
            memory_type=MemoryType.FACT,
            relevance_score=0.1,  # Low score
            num_times_referenced=5,  # Referenced 5+ times
        )
        assert memory.should_consolidate() is True

    def test_should_consolidate_high_relevance(self):
        """Test that high relevance memories are consolidated."""
        memory = Memory(
            user_id="user-123",
            short_text="High relevance task",
            memory_type=MemoryType.TASK,
            relevance_score=0.8,  # > 0.7
            num_times_referenced=1,
        )
        assert memory.should_consolidate() is True

    def test_should_not_consolidate(self):
        """Test that low value memories are not consolidated."""
        memory = Memory(
            user_id="user-123",
            short_text="Low value memory",
            memory_type=MemoryType.FACT,
            relevance_score=0.3,  # < 0.7
            num_times_referenced=2,  # < 5
        )
        assert memory.should_consolidate() is False

    def test_to_payload(self):
        """Test converting to Qdrant payload."""
        memory_id = uuid4()
        memory = Memory(
            memory_id=memory_id,
            user_id="user-123",
            short_text="Test memory",
            memory_type=MemoryType.GOAL,
            relevance_score=0.9,
            source="conv-456",
        )

        payload = memory.to_payload()

        assert payload["memory_id"] == str(memory_id)
        assert payload["user_id"] == "user-123"
        assert payload["short_text"] == "Test memory"
        assert payload["memory_type"] == "goal"
        assert payload["relevance_score"] == 0.9
        assert payload["source"] == "conv-456"

    def test_from_payload(self):
        """Test creating memory from Qdrant payload."""
        memory_id = str(uuid4())
        payload = {
            "memory_id": memory_id,
            "user_id": "user-123",
            "short_text": "Test memory",
            "memory_type": "preference",
            "timestamp": "2025-01-01T12:00:00",
            "last_referenced_at": "2025-01-02T12:00:00",
            "relevance_score": 0.85,
            "num_times_referenced": 3,
            "source": "conv-123",
            "metadata": {"key": "value"},
        }

        memory = Memory.from_payload(payload)

        assert str(memory.memory_id) == memory_id
        assert memory.user_id == "user-123"
        assert memory.memory_type == MemoryType.PREFERENCE
        assert memory.relevance_score == 0.85
        assert memory.num_times_referenced == 3

    def test_memory_types(self):
        """Test all memory types are valid."""
        for mem_type in MemoryType:
            memory = Memory(
                user_id="user-123",
                short_text=f"Test {mem_type.value}",
                memory_type=mem_type,
            )
            assert memory.memory_type == mem_type

    def test_string_representation(self):
        """Test string representation."""
        memory = Memory(
            user_id="user-123",
            short_text="User prefers Python",
            memory_type=MemoryType.PREFERENCE,
        )

        assert "[preference]" in str(memory).lower()
        assert "Python" in str(memory)


class TestMemoryRepository:
    """Tests for MemoryRepository."""

    @pytest.fixture
    def mock_qdrant(self):
        """Create mock Qdrant client."""
        return AsyncMock()

    @pytest.fixture
    def mock_embeddings(self):
        """Create mock embedding service."""
        service = AsyncMock()
        service.embed_text.return_value = [0.1] * 1536
        service.embed_texts.return_value = [[0.1] * 1536, [0.2] * 1536]
        service.embed_query.return_value = [0.1] * 1536
        return service

    @pytest.mark.asyncio
    async def test_create_memory(self, mock_qdrant, mock_embeddings):
        """Test creating a memory."""
        from src.infrastructure.vector_store.memory_repository import MemoryRepository

        with patch("src.infrastructure.vector_store.memory_repository.get_qdrant_client", return_value=mock_qdrant), \
             patch("src.infrastructure.vector_store.memory_repository.get_embedding_service", return_value=mock_embeddings):

            repo = MemoryRepository()
            memory = Memory(
                user_id="user-123",
                short_text="Test memory",
                memory_type=MemoryType.FACT,
            )

            result = await repo.create(memory)

            assert result.user_id == "user-123"
            mock_embeddings.embed_text.assert_called_once_with("Test memory")
            mock_qdrant.upsert_point.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_similar(self, mock_qdrant, mock_embeddings):
        """Test searching for similar memories."""
        from src.infrastructure.vector_store.memory_repository import MemoryRepository

        # Setup mock search results
        mock_qdrant.search.return_value = [
            (
                "mem-1",
                0.9,
                {
                    "memory_id": str(uuid4()),
                    "user_id": "user-123",
                    "short_text": "Found memory",
                    "memory_type": "fact",
                    "timestamp": "2025-01-01T12:00:00",
                    "last_referenced_at": "2025-01-01T12:00:00",
                    "relevance_score": 0.9,
                    "num_times_referenced": 1,
                },
            )
        ]

        with patch("src.infrastructure.vector_store.memory_repository.get_qdrant_client", return_value=mock_qdrant), \
             patch("src.infrastructure.vector_store.memory_repository.get_embedding_service", return_value=mock_embeddings):

            repo = MemoryRepository()
            results = await repo.search_similar(
                query="test query",
                user_id="user-123",
                limit=5,
            )

            assert len(results) == 1
            memory, score = results[0]
            assert memory.short_text == "Found memory"
            assert score == 0.9


class TestMemoryExtraction:
    """Tests for memory extraction use case."""

    @pytest.mark.asyncio
    async def test_format_conversation(self):
        """Test conversation formatting."""
        from src.application.use_cases.memory_extraction import MemoryExtractionUseCase

        extractor = MemoryExtractionUseCase()

        messages = [
            {"role": "user", "content": "Hello, I'm David"},
            {"role": "assistant", "content": "Hi David!"},
            {"role": "user", "content": "I work as an engineer"},
        ]

        result = extractor._format_conversation(messages)

        assert "User: Hello, I'm David" in result
        assert "Assistant: Hi David!" in result
        assert "User: I work as an engineer" in result

    @pytest.mark.asyncio
    async def test_extract_from_conversation_empty(self):
        """Test extraction with empty messages."""
        from src.application.use_cases.memory_extraction import MemoryExtractionUseCase

        extractor = MemoryExtractionUseCase()

        result = await extractor.extract_from_conversation(
            messages=[],
            user_id="user-123",
            conversation_id="conv-123",
        )

        assert result == []
