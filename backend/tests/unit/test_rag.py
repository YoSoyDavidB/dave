"""Tests for RAG system components."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.application.use_cases.rag_query import RAGQueryUseCase, ScoredItem
from src.application.use_cases.vault_indexing import (
    VaultIndexingUseCase,
    compute_content_hash,
    should_index_path,
)
from src.domain.entities.memory import Memory, MemoryType
from src.infrastructure.vector_store.chunking import (
    CHARS_PER_TOKEN,
    chunk_by_tokens,
    chunk_document,
    chunk_markdown,
    estimate_tokens,
)
from src.infrastructure.vector_store.document_repository import (
    DocumentRepository,
    IndexedDocument,
)
from src.infrastructure.vector_store.result_reranker import (
    ResultReranker,
    extract_keywords,
    keyword_match_score,
    mmr_rerank,
    recency_score,
)


# ============================================================================
# Chunking Tests
# ============================================================================

class TestEstimateTokens:
    """Tests for token estimation."""

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_simple_text(self):
        text = "Hello world"
        expected = len(text) // CHARS_PER_TOKEN
        assert estimate_tokens(text) == expected

    def test_long_text(self):
        text = "a" * 100
        assert estimate_tokens(text) == 25


class TestChunkByTokens:
    """Tests for token-based chunking."""

    def test_empty_text(self):
        chunks = list(chunk_by_tokens(""))
        assert chunks == []

    def test_whitespace_only(self):
        chunks = list(chunk_by_tokens("   \n\t  "))
        assert chunks == []

    def test_short_text_single_chunk(self):
        text = "Hello, this is a short text."
        chunks = list(chunk_by_tokens(text, chunk_size=100))
        assert len(chunks) == 1
        assert chunks[0].content == text
        assert chunks[0].chunk_index == 0

    def test_long_text_multiple_chunks(self):
        # Create text that should produce multiple chunks
        text = "This is a sentence. " * 100
        chunks = list(chunk_by_tokens(text, chunk_size=50, chunk_overlap=10))
        assert len(chunks) > 1

        # Verify chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_chunk_positions(self):
        text = "First sentence. Second sentence. Third sentence."
        chunks = list(chunk_by_tokens(text, chunk_size=10, chunk_overlap=2))

        for chunk in chunks:
            assert chunk.start_char >= 0
            assert chunk.end_char <= len(text)
            assert chunk.start_char < chunk.end_char


class TestChunkMarkdown:
    """Tests for markdown-aware chunking."""

    def test_empty_markdown(self):
        chunks = list(chunk_markdown(""))
        assert chunks == []

    def test_single_heading(self):
        text = "# Title\n\nSome content here."
        chunks = list(chunk_markdown(text, chunk_size=100))
        assert len(chunks) == 1
        assert "# Title" in chunks[0].content

    def test_multiple_headings(self):
        text = """# Chapter 1

Some content for chapter 1.

## Section 1.1

Content for section 1.1.

# Chapter 2

Content for chapter 2."""

        chunks = list(chunk_markdown(text, chunk_size=50))
        # Should create chunks at heading boundaries
        assert len(chunks) >= 1

        # At least one chunk should have heading metadata
        has_heading = any(chunk.metadata.get("heading") for chunk in chunks)
        assert has_heading

    def test_preserves_heading_context(self):
        text = """## Important Section

This is very important content that should be associated with the heading."""

        chunks = list(chunk_markdown(text, chunk_size=100))
        assert len(chunks) == 1
        assert "Important Section" in chunks[0].metadata.get("heading", "")


class TestChunkDocument:
    """Tests for document chunking dispatch."""

    def test_markdown_file(self):
        content = "# Test\n\nContent here."
        chunks = chunk_document(content, "test.md")
        assert len(chunks) > 0
        assert all(c.metadata.get("path") == "test.md" for c in chunks)

    def test_non_markdown_file(self):
        content = "Some plain text content."
        chunks = chunk_document(content, "test.txt")
        assert len(chunks) > 0
        assert all(c.metadata.get("path") == "test.txt" for c in chunks)


# ============================================================================
# Result Reranker Tests
# ============================================================================

class TestExtractKeywords:
    """Tests for keyword extraction."""

    def test_empty_text(self):
        assert extract_keywords("") == set()

    def test_removes_stop_words(self):
        keywords = extract_keywords("the quick brown fox")
        assert "the" not in keywords
        assert "quick" in keywords
        assert "brown" in keywords
        assert "fox" in keywords

    def test_removes_short_words(self):
        keywords = extract_keywords("I am a cat")
        assert "am" not in keywords
        assert "cat" in keywords

    def test_lowercase(self):
        keywords = extract_keywords("Python JavaScript TypeScript")
        assert "python" in keywords
        assert "javascript" in keywords


class TestKeywordMatchScore:
    """Tests for keyword matching."""

    def test_empty_keywords(self):
        assert keyword_match_score(set(), "some content") == 0.0

    def test_no_matches(self):
        keywords = {"python", "javascript"}
        score = keyword_match_score(keywords, "ruby golang rust")
        assert score == 0.0

    def test_all_matches(self):
        keywords = {"python", "javascript"}
        score = keyword_match_score(keywords, "Python and JavaScript are great")
        assert score == 1.0

    def test_partial_matches(self):
        keywords = {"python", "javascript", "ruby"}
        score = keyword_match_score(keywords, "I love Python")
        assert 0.0 < score < 1.0


class TestRecencyScore:
    """Tests for recency scoring."""

    def test_very_recent(self):
        # Today's date should get score close to 1.0
        score = recency_score(datetime.utcnow())
        assert score == 1.0

    def test_old_content(self):
        # Very old content should get score 0.0
        from datetime import timedelta
        old_date = datetime.utcnow() - timedelta(days=400)
        score = recency_score(old_date, max_age_days=365)
        assert score == 0.0

    def test_mid_age(self):
        from datetime import timedelta
        mid_date = datetime.utcnow() - timedelta(days=180)
        score = recency_score(mid_date, max_age_days=365)
        assert 0.4 < score < 0.6


class TestMMRRerank:
    """Tests for MMR reranking."""

    def test_empty_results(self):
        assert mmr_rerank([]) == []

    def test_single_result(self):
        results = [("item1", 0.9, "content 1")]
        reranked = mmr_rerank(results, top_k=5)
        assert len(reranked) == 1
        assert reranked[0][0] == "item1"

    def test_diversity(self):
        # Similar content should be penalized
        results = [
            ("item1", 0.9, "python programming language"),
            ("item2", 0.85, "python programming tutorial"),  # Similar to item1
            ("item3", 0.8, "javascript web development"),     # Different
        ]
        reranked = mmr_rerank(results, lambda_param=0.5, top_k=3)
        assert len(reranked) == 3


class TestResultReranker:
    """Tests for ResultReranker class."""

    def test_unknown_strategy(self):
        reranker = ResultReranker()

        class FakeResult:
            score = 0.5
            content = "test"

        with pytest.raises(ValueError, match="Unknown strategy"):
            reranker.rerank([FakeResult()], "test query", strategy="invalid")

    def test_empty_results(self):
        reranker = ResultReranker()
        result = reranker.rerank([], "test query")
        assert result == []

    def test_keyword_strategy(self):
        reranker = ResultReranker()

        class FakeResult:
            score = 0.5
            content = "python programming"

        results = [FakeResult()]
        reranked = reranker.rerank(results, "python", strategy="keyword")
        assert len(reranked) == 1
        assert reranked[0].final_score >= reranked[0].original_score

    def test_hybrid_strategy(self):
        reranker = ResultReranker()

        class FakeResult:
            score = 0.7
            content = "machine learning tutorial"
            timestamp = datetime.utcnow()

        results = [FakeResult()]
        reranked = reranker.rerank(results, "machine learning", strategy="hybrid")
        assert len(reranked) == 1


# ============================================================================
# Document Repository Tests
# ============================================================================

class TestIndexedDocument:
    """Tests for IndexedDocument dataclass."""

    def test_from_payload(self):
        payload = {
            "path": "test/file.md",
            "content": "Test content",
            "chunk_index": 0,
            "title": "Test File",
            "heading": "## Section",
            "last_modified": datetime.utcnow().isoformat(),
        }

        doc = IndexedDocument.from_payload("chunk_001", payload, score=0.85)

        assert doc.chunk_id == "chunk_001"
        assert doc.path == "test/file.md"
        assert doc.content == "Test content"
        assert doc.score == 0.85

    def test_from_payload_defaults(self):
        doc = IndexedDocument.from_payload("id", {})

        assert doc.path == ""
        assert doc.content == ""
        assert doc.chunk_index == 0


# ============================================================================
# Vault Indexing Tests
# ============================================================================

class TestShouldIndexPath:
    """Tests for path filtering."""

    def test_markdown_file(self):
        assert should_index_path("notes/my-note.md") is True

    def test_non_markdown_file(self):
        assert should_index_path("data/file.json") is False

    def test_excluded_obsidian_folder(self):
        assert should_index_path(".obsidian/config.md") is False

    def test_excluded_git_folder(self):
        assert should_index_path(".git/something.md") is False

    def test_excluded_templates(self):
        assert should_index_path("Extras/Templates/daily.md") is False

    def test_archive_folder(self):
        assert should_index_path("Archive/old-note.md") is False

    def test_normal_path(self):
        assert should_index_path("Projects/my-project/notes.md") is True


class TestComputeContentHash:
    """Tests for content hashing."""

    def test_consistent_hash(self):
        content = "Test content"
        hash1 = compute_content_hash(content)
        hash2 = compute_content_hash(content)
        assert hash1 == hash2

    def test_different_content_different_hash(self):
        hash1 = compute_content_hash("Content A")
        hash2 = compute_content_hash("Content B")
        assert hash1 != hash2

    def test_hash_length(self):
        hash_value = compute_content_hash("Test")
        assert len(hash_value) == 16


# ============================================================================
# RAG Query Tests
# ============================================================================

class TestRAGQueryUseCase:
    """Tests for RAG query use case."""

    @pytest.fixture
    def mock_memory(self):
        return Memory(
            memory_id=uuid4(),
            user_id="user123",
            short_text="User prefers dark mode",
            memory_type=MemoryType.PREFERENCE,
            timestamp=datetime.utcnow(),
            last_referenced_at=datetime.utcnow(),
            relevance_score=0.8,
            num_times_referenced=1,
            source="conversation",
            metadata={},
            embedding=[0.1] * 1536,
        )

    @pytest.fixture
    def mock_document(self):
        return IndexedDocument(
            chunk_id="doc_001",
            path="Projects/notes.md",
            content="Project documentation content",
            chunk_index=0,
            title="Project Notes",
            heading="## Setup",
            last_modified=datetime.utcnow(),
            score=0.75,
        )

    def test_format_context_memories_only(self, mock_memory):
        rag = RAGQueryUseCase()
        context = rag._format_context([mock_memory], [])

        assert "User Context" in context
        assert "Preference" in context
        assert "dark mode" in context

    def test_format_context_documents_only(self, mock_document):
        rag = RAGQueryUseCase()
        context = rag._format_context([], [mock_document])

        assert "Relevant Knowledge" in context
        assert "Project Notes" in context or "notes" in context

    def test_format_context_empty(self):
        rag = RAGQueryUseCase()
        context = rag._format_context([], [])
        assert context == ""

    def test_combine_results(self, mock_memory, mock_document):
        rag = RAGQueryUseCase()
        combined = rag._combine_results(
            memories=[mock_memory],
            documents=[mock_document],
            memory_limit=5,
            document_limit=5,
        )

        assert len(combined) == 2
        assert any(item.source_type == "memory" for item in combined)
        assert any(item.source_type == "document" for item in combined)


class TestScoredItem:
    """Tests for ScoredItem dataclass."""

    def test_creation(self):
        item = ScoredItem(
            item="test_item",
            score=0.75,
            content="test content",
            source_type="memory",
        )

        assert item.item == "test_item"
        assert item.score == 0.75
        assert item.source_type == "memory"


# ============================================================================
# Integration-style Tests (with mocks)
# ============================================================================

class TestDocumentRepositoryMocked:
    """Tests for DocumentRepository with mocked dependencies."""

    @pytest.fixture
    def mock_qdrant(self):
        with patch('src.infrastructure.vector_store.document_repository.get_qdrant_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def mock_embeddings(self):
        with patch('src.infrastructure.vector_store.document_repository.get_embedding_service') as mock:
            service = AsyncMock()
            service.embed_texts = AsyncMock(return_value=[[0.1] * 1536])
            service.embed_query = AsyncMock(return_value=[0.1] * 1536)
            mock.return_value = service
            yield service

    @pytest.mark.asyncio
    async def test_index_empty_document(self, mock_qdrant, mock_embeddings):
        repo = DocumentRepository()
        result = await repo.index_document(
            path="test.md",
            content="",
        )
        assert result == 0

    @pytest.mark.asyncio
    async def test_delete_by_path(self, mock_qdrant, mock_embeddings):
        mock_qdrant.delete_by_filter = AsyncMock(return_value=5)

        repo = DocumentRepository()
        result = await repo.delete_by_path("test.md")

        assert result == 5
        mock_qdrant.delete_by_filter.assert_called_once()


class TestVaultIndexingMocked:
    """Tests for VaultIndexingUseCase with mocked dependencies."""

    @pytest.fixture
    def mock_vault_client(self):
        with patch('src.application.use_cases.vault_indexing.get_github_vault_client') as mock:
            client = AsyncMock()
            mock.return_value = client
            yield client

    @pytest.fixture
    def mock_doc_repo(self):
        with patch('src.application.use_cases.vault_indexing.get_document_repository') as mock:
            repo = AsyncMock()
            mock.return_value = repo
            yield repo

    @pytest.mark.asyncio
    async def test_get_stats(self, mock_vault_client, mock_doc_repo):
        mock_doc_repo.count_documents = AsyncMock(return_value={"documents": 10, "chunks": 50})

        use_case = VaultIndexingUseCase()
        stats = await use_case.get_stats()

        assert stats["documents_indexed"] == 10
        assert stats["total_chunks"] == 50

    @pytest.mark.asyncio
    async def test_index_single_document_excluded(self, mock_vault_client, mock_doc_repo):
        use_case = VaultIndexingUseCase()
        result = await use_case.index_single_document(".obsidian/config.md")

        assert result == 0
        mock_vault_client.get_file.assert_not_called()
