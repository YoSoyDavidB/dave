"""RAG API routes - indexing and search."""

from typing import Any

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from src.application.use_cases.rag_query import get_rag_query_use_case
from src.application.use_cases.vault_indexing import get_vault_indexing_use_case
from src.domain.entities.memory import MemoryType
from src.infrastructure.vector_store.memory_repository import get_memory_repository

logger = structlog.get_logger()
router = APIRouter(prefix="/rag", tags=["rag"])


class IndexResponse(BaseModel):
    """Response from indexing operations."""

    status: str
    message: str
    stats: dict[str, Any] | None = None


class SearchRequest(BaseModel):
    """Request for RAG search."""

    query: str
    user_id: str | None = None
    include_memories: bool = True
    include_documents: bool = True
    limit: int = 5
    min_score: float = 0.5


class SearchResult(BaseModel):
    """A single search result."""

    content: str
    source: str
    source_type: str  # "memory" or "document"
    score: float


class SearchResponse(BaseModel):
    """Response from RAG search."""

    results: list[SearchResult]
    context: str
    stats: dict[str, Any]


@router.post("/index/full", response_model=IndexResponse)
async def full_index(background_tasks: BackgroundTasks) -> IndexResponse:
    """Trigger a full vault index.

    This runs in the background and may take a while for large vaults.
    """
    async def run_full_sync():
        try:
            indexer = get_vault_indexing_use_case()
            stats = await indexer.full_sync()
            logger.info("full_index_completed", stats=stats)
        except Exception as e:
            logger.error("full_index_failed", error=str(e))

    background_tasks.add_task(run_full_sync)

    return IndexResponse(
        status="started",
        message="Full vault indexing started in background",
    )


@router.post("/index/incremental", response_model=IndexResponse)
async def incremental_index(background_tasks: BackgroundTasks) -> IndexResponse:
    """Trigger an incremental vault index.

    Only indexes files that have changed since last sync.
    """
    async def run_incremental_sync():
        try:
            indexer = get_vault_indexing_use_case()
            stats = await indexer.incremental_sync()
            logger.info("incremental_index_completed", stats=stats)
        except Exception as e:
            logger.error("incremental_index_failed", error=str(e))

    background_tasks.add_task(run_incremental_sync)

    return IndexResponse(
        status="started",
        message="Incremental vault indexing started in background",
    )


@router.post("/index/document")
async def index_single_document(path: str) -> IndexResponse:
    """Index a single document by path."""
    try:
        indexer = get_vault_indexing_use_case()
        chunks = await indexer.index_single_document(path)

        return IndexResponse(
            status="completed",
            message="Document indexed successfully",
            stats={"path": path, "chunks": chunks},
        )

    except Exception as e:
        logger.error("single_document_index_failed", path=path, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/index/stats", response_model=IndexResponse)
async def get_index_stats() -> IndexResponse:
    """Get current indexing statistics."""
    try:
        indexer = get_vault_indexing_use_case()
        stats = await indexer.get_stats()

        return IndexResponse(
            status="ok",
            message="Index statistics retrieved",
            stats=stats,
        )

    except Exception as e:
        logger.error("get_index_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """Search the RAG system.

    Combines memories and documents based on semantic similarity.
    """
    try:
        rag = get_rag_query_use_case()
        result = await rag.query(
            query=request.query,
            user_id=request.user_id,
            include_memories=request.include_memories,
            include_documents=request.include_documents,
            memory_limit=request.limit,
            document_limit=request.limit,
            min_score=request.min_score,
        )

        # Format results
        search_results = []

        for memory in result.memories:
            search_results.append(SearchResult(
                content=memory.short_text,
                source=memory.source,
                source_type="memory",
                score=memory.relevance_score,
            ))

        for doc in result.documents:
            search_results.append(SearchResult(
                content=doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                source=doc.path,
                source_type="document",
                score=doc.score,
            ))

        return SearchResponse(
            results=search_results,
            context=result.formatted_context,
            stats=result.retrieval_stats,
        )

    except Exception as e:
        logger.error("rag_search_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MEMORY ENDPOINTS
# ============================================

class MemoryResponse(BaseModel):
    """A memory item."""

    id: str
    user_id: str
    short_text: str
    memory_type: str
    timestamp: str
    last_referenced_at: str
    relevance_score: float
    num_times_referenced: int
    source: str


class MemoryListResponse(BaseModel):
    """Response for memory list."""

    memories: list[MemoryResponse]
    total: int


@router.get("/memories/{user_id}", response_model=MemoryListResponse)
async def get_user_memories(
    user_id: str,
    memory_type: str | None = None,
    limit: int = 50,
) -> MemoryListResponse:
    """Get all memories for a user."""
    try:
        repo = get_memory_repository()
        memories = await repo.get_by_user(
            user_id=user_id,
            memory_type=MemoryType(memory_type) if memory_type else None,
            limit=limit,
        )

        return MemoryListResponse(
            memories=[
                MemoryResponse(
                    id=str(m.memory_id),
                    user_id=m.user_id,
                    short_text=m.short_text,
                    memory_type=m.memory_type.value,
                    timestamp=m.timestamp.isoformat(),
                    last_referenced_at=m.last_referenced_at.isoformat(),
                    relevance_score=m.relevance_score,
                    num_times_referenced=m.num_times_referenced,
                    source=m.source,
                )
                for m in memories
            ],
            total=len(memories),
        )

    except Exception as e:
        logger.error("get_memories_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memories/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str) -> dict[str, str]:
    """Delete a specific memory."""
    try:
        repo = get_memory_repository()
        deleted = await repo.delete(memory_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Memory not found")

        return {"status": "deleted", "memory_id": memory_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_memory_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memories/{user_id}/stats")
async def get_memory_stats(user_id: str) -> dict[str, Any]:
    """Get memory statistics for a user."""
    try:
        repo = get_memory_repository()
        total_count = await repo.count_by_user(user_id)

        # Get memories to count by type
        memories = await repo.get_by_user(user_id, limit=1000)
        by_type: dict[str, int] = {}
        for m in memories:
            type_name = m.memory_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1

        return {
            "user_id": user_id,
            "total_memories": total_count,
            "by_type": by_type,
        }

    except Exception as e:
        logger.error("get_memory_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
