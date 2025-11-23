"""RAG Query use case - retrieval augmented generation for chat."""

from dataclasses import dataclass
from typing import Any

import structlog

from src.domain.entities.memory import Memory
from src.infrastructure.vector_store.document_repository import (
    IndexedDocument,
    get_document_repository,
)
from src.infrastructure.vector_store.memory_repository import get_memory_repository
from src.infrastructure.vector_store.result_reranker import (
    get_result_reranker,
)
from src.infrastructure.vector_store.uploaded_document_repository import (
    get_uploaded_document_repository,
)

logger = structlog.get_logger()


@dataclass
class UploadedDocChunk:
    """Represents a chunk from an uploaded document."""

    chunk_id: str
    content: str
    score: float
    document_id: str
    filename: str
    category: str
    chunk_index: int


@dataclass
class RAGContext:
    """Context assembled from RAG retrieval."""

    memories: list[Memory]
    documents: list[IndexedDocument]
    uploaded_docs: list[UploadedDocChunk]
    formatted_context: str
    retrieval_stats: dict[str, Any]


@dataclass
class ScoredItem:
    """Wrapper to make items compatible with reranker."""

    item: Any
    score: float
    content: str
    source_type: str  # "memory", "document", or "uploaded_doc"


class RAGQueryUseCase:
    """Retrieval Augmented Generation query processor.

    Combines memory search and document search with reranking
    to provide relevant context for LLM responses.
    """

    def __init__(
        self,
        memory_weight: float = 0.5,
        document_weight: float = 0.3,
        uploaded_doc_weight: float = 0.5,
        max_context_tokens: int = 2000,
    ):
        """Initialize RAG query use case.

        Args:
            memory_weight: Weight for memory results (0-1)
            document_weight: Weight for vault document results (0-1)
            uploaded_doc_weight: Weight for uploaded document results (0-1)
            max_context_tokens: Maximum tokens for context window
        """
        self._memory_repo = get_memory_repository()
        self._doc_repo = get_document_repository()
        self._uploaded_doc_repo = get_uploaded_document_repository()
        self._reranker = get_result_reranker()

        self._memory_weight = memory_weight
        self._document_weight = document_weight
        self._uploaded_doc_weight = uploaded_doc_weight
        self._max_context_tokens = max_context_tokens

    async def query(
        self,
        query: str,
        user_id: str | None = None,
        include_memories: bool = True,
        include_documents: bool = True,
        include_uploaded_docs: bool = True,
        memory_limit: int = 5,
        document_limit: int = 5,
        uploaded_doc_limit: int = 5,
        min_score: float = 0.5,
        rerank_strategy: str = "hybrid",
        path_filter: str | None = None,
    ) -> RAGContext:
        """Execute RAG query to retrieve relevant context.

        Args:
            query: User query
            user_id: User ID for memory and uploaded doc search
            include_memories: Whether to search memories
            include_documents: Whether to search vault documents
            include_uploaded_docs: Whether to search uploaded documents
            memory_limit: Max memories to retrieve
            document_limit: Max vault documents to retrieve
            uploaded_doc_limit: Max uploaded document chunks to retrieve
            min_score: Minimum similarity score
            rerank_strategy: Reranking strategy to use
            path_filter: Optional path prefix filter for documents

        Returns:
            RAGContext with retrieved and formatted context
        """
        memories: list[Memory] = []
        documents: list[IndexedDocument] = []
        uploaded_docs: list[UploadedDocChunk] = []
        stats = {
            "query_length": len(query),
            "memories_searched": 0,
            "documents_searched": 0,
            "uploaded_docs_searched": 0,
            "memories_retrieved": 0,
            "documents_retrieved": 0,
            "uploaded_docs_retrieved": 0,
            "rerank_strategy": rerank_strategy,
        }

        # Search memories if user_id provided
        if include_memories and user_id:
            try:
                memories = await self._memory_repo.search_similar(
                    user_id=user_id,
                    query=query,
                    limit=memory_limit * 2,  # Get extra for reranking
                    min_score=min_score,
                )
                stats["memories_searched"] = len(memories)

                # Mark memories as referenced
                for memory in memories:
                    await self._memory_repo.mark_referenced(memory.memory_id)

            except Exception as e:
                logger.error("memory_search_error", error=str(e))

        # Search vault documents
        if include_documents:
            try:
                documents = await self._doc_repo.search_similar(
                    query=query,
                    limit=document_limit * 2,  # Get extra for reranking
                    min_score=min_score,
                    path_filter=path_filter,
                )
                stats["documents_searched"] = len(documents)

            except Exception as e:
                logger.error("document_search_error", error=str(e))

        # Search uploaded documents
        if include_uploaded_docs and user_id:
            try:
                uploaded_results = await self._uploaded_doc_repo.search_documents(
                    query=query,
                    user_id=user_id,
                    limit=uploaded_doc_limit * 2,  # Get extra for reranking
                    min_score=min_score,
                )
                stats["uploaded_docs_searched"] = len(uploaded_results)

                # Convert to UploadedDocChunk objects
                for r in uploaded_results:
                    uploaded_docs.append(UploadedDocChunk(
                        chunk_id=r["chunk_id"],
                        content=r["content"],
                        score=r["score"],
                        document_id=r["document_id"],
                        filename=r["filename"],
                        category=r["category"],
                        chunk_index=r["chunk_index"],
                    ))

            except Exception as e:
                logger.error("uploaded_doc_search_error", error=str(e))

        # Combine and rerank results
        combined_results = self._combine_results(
            memories=memories,
            documents=documents,
            uploaded_docs=uploaded_docs,
            memory_limit=memory_limit,
            document_limit=document_limit,
            uploaded_doc_limit=uploaded_doc_limit,
        )

        # Apply reranking
        if combined_results and rerank_strategy != "none":
            reranked = self._rerank_results(
                results=combined_results,
                query=query,
                strategy=rerank_strategy,
                top_k=memory_limit + document_limit + uploaded_doc_limit,
            )

            # Separate back into memories, documents, and uploaded docs
            memories = []
            documents = []
            uploaded_docs = []

            for result in reranked:
                if result.source_type == "memory":
                    memories.append(result.item)
                elif result.source_type == "document":
                    documents.append(result.item)
                else:  # uploaded_doc
                    uploaded_docs.append(result.item)

        # Limit final results
        memories = memories[:memory_limit]
        documents = documents[:document_limit]
        uploaded_docs = uploaded_docs[:uploaded_doc_limit]

        stats["memories_retrieved"] = len(memories)
        stats["documents_retrieved"] = len(documents)
        stats["uploaded_docs_retrieved"] = len(uploaded_docs)

        # Format context for LLM
        formatted_context = self._format_context(memories, documents, uploaded_docs)

        logger.info(
            "rag_query_completed",
            query_length=len(query),
            memories=len(memories),
            documents=len(documents),
            uploaded_docs=len(uploaded_docs),
        )

        return RAGContext(
            memories=memories,
            documents=documents,
            uploaded_docs=uploaded_docs,
            formatted_context=formatted_context,
            retrieval_stats=stats,
        )

    def _combine_results(
        self,
        memories: list[Memory],
        documents: list[IndexedDocument],
        uploaded_docs: list[UploadedDocChunk],
        memory_limit: int,
        document_limit: int,
        uploaded_doc_limit: int,
    ) -> list[ScoredItem]:
        """Combine memory, document, and uploaded doc results into scored items.

        Args:
            memories: Memory search results
            documents: Vault document search results
            uploaded_docs: Uploaded document search results
            memory_limit: Max memories
            document_limit: Max vault documents
            uploaded_doc_limit: Max uploaded document chunks

        Returns:
            List of ScoredItem for reranking
        """
        combined = []

        # Add memories with weighted scores
        for memory in memories:
            # Use relevance_score as the score, weighted
            weighted_score = memory.relevance_score * self._memory_weight
            combined.append(ScoredItem(
                item=memory,
                score=weighted_score,
                content=memory.short_text,
                source_type="memory",
            ))

        # Add vault documents with weighted scores
        for doc in documents:
            weighted_score = doc.score * self._document_weight
            combined.append(ScoredItem(
                item=doc,
                score=weighted_score,
                content=doc.content,
                source_type="document",
            ))

        # Add uploaded documents with weighted scores
        for uploaded_doc in uploaded_docs:
            weighted_score = uploaded_doc.score * self._uploaded_doc_weight
            combined.append(ScoredItem(
                item=uploaded_doc,
                score=weighted_score,
                content=uploaded_doc.content,
                source_type="uploaded_doc",
            ))

        return combined

    def _rerank_results(
        self,
        results: list[ScoredItem],
        query: str,
        strategy: str,
        top_k: int,
    ) -> list[ScoredItem]:
        """Rerank combined results.

        Args:
            results: Combined scored items
            query: Original query
            strategy: Reranking strategy
            top_k: Number of results to keep

        Returns:
            Reranked list of ScoredItem
        """
        if not results:
            return []

        # Prepare for reranker (needs score and content attributes)
        reranker_input = []
        for item in results:
            # Create a simple object with required attributes
            class ScoreableWrapper:
                def __init__(self, score: float, content: str, original: ScoredItem):
                    self.score = score
                    self.content = content
                    self._original = original

            wrapper = ScoreableWrapper(item.score, item.content, item)
            reranker_input.append(wrapper)

        # Rerank
        reranked = self._reranker.rerank(
            results=reranker_input,
            query=query,
            strategy=strategy,
            top_k=top_k,
        )

        # Extract original ScoredItems in new order
        return [r.original_item._original for r in reranked]

    def _format_context(
        self,
        memories: list[Memory],
        documents: list[IndexedDocument],
        uploaded_docs: list[UploadedDocChunk],
    ) -> str:
        """Format retrieved context for LLM consumption.

        Args:
            memories: Retrieved memories
            documents: Retrieved vault documents
            uploaded_docs: Retrieved uploaded document chunks

        Returns:
            Formatted context string
        """
        parts = []

        # Format memories
        if memories:
            memory_lines = []
            for memory in memories:
                type_label = memory.memory_type.value.title()
                memory_lines.append(f"- [{type_label}] {memory.short_text}")

            parts.append(
                "## User Context (from memory)\n"
                + "\n".join(memory_lines)
            )

        # Format vault documents
        if documents:
            doc_lines = []
            for doc in documents:
                # Truncate long content
                content = doc.content
                if len(content) > 500:
                    content = content[:500] + "..."

                source = doc.path.split("/")[-1].replace(".md", "")
                if doc.heading:
                    source = f"{source} > {doc.heading}"

                doc_lines.append(f"### {source}\n{content}")

            parts.append(
                "## Relevant Knowledge (from vault)\n"
                + "\n\n".join(doc_lines)
            )

        # Format uploaded documents
        if uploaded_docs:
            uploaded_lines = []
            for udoc in uploaded_docs:
                # Truncate long content
                content = udoc.content
                if len(content) > 500:
                    content = content[:500] + "..."

                source = f"{udoc.filename} [{udoc.category}]"
                uploaded_lines.append(f"### {source}\n{content}")

            parts.append(
                "## Relevant Documents (uploaded)\n"
                + "\n\n".join(uploaded_lines)
            )

        if not parts:
            return ""

        return "\n\n".join(parts)

    async def query_memories_only(
        self,
        query: str,
        user_id: str,
        limit: int = 5,
        min_score: float = 0.5,
    ) -> list[Memory]:
        """Query only memories.

        Args:
            query: Search query
            user_id: User ID
            limit: Max results
            min_score: Minimum score

        Returns:
            List of relevant memories
        """
        result = await self.query(
            query=query,
            user_id=user_id,
            include_memories=True,
            include_documents=False,
            memory_limit=limit,
            min_score=min_score,
        )
        return result.memories

    async def query_documents_only(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.5,
        path_filter: str | None = None,
    ) -> list[IndexedDocument]:
        """Query only documents.

        Args:
            query: Search query
            limit: Max results
            min_score: Minimum score
            path_filter: Optional path prefix filter

        Returns:
            List of relevant documents
        """
        result = await self.query(
            query=query,
            user_id=None,
            include_memories=False,
            include_documents=True,
            document_limit=limit,
            min_score=min_score,
            path_filter=path_filter,
        )
        return result.documents


# Singleton instance
_rag_query: RAGQueryUseCase | None = None


def get_rag_query_use_case() -> RAGQueryUseCase:
    """Get the singleton RAG query use case."""
    global _rag_query
    if _rag_query is None:
        _rag_query = RAGQueryUseCase()
    return _rag_query
