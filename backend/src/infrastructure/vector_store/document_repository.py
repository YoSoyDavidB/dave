"""Document repository for vault content indexing."""

from datetime import datetime
from typing import Any
from dataclasses import dataclass

import structlog
from qdrant_client.http import models

from src.infrastructure.embeddings import get_embedding_service
from src.infrastructure.vector_store.qdrant_client import (
    DOCUMENTS_COLLECTION,
    get_qdrant_client,
)
from src.infrastructure.vector_store.chunking import DocumentChunk, chunk_document

logger = structlog.get_logger()


@dataclass
class IndexedDocument:
    """Represents an indexed document chunk."""

    chunk_id: str
    path: str
    content: str
    chunk_index: int
    title: str
    heading: str
    last_modified: datetime
    score: float = 0.0

    @classmethod
    def from_payload(cls, chunk_id: str, payload: dict[str, Any], score: float = 0.0) -> "IndexedDocument":
        """Create from Qdrant payload."""
        return cls(
            chunk_id=chunk_id,
            path=payload.get("path", ""),
            content=payload.get("content", ""),
            chunk_index=payload.get("chunk_index", 0),
            title=payload.get("title", ""),
            heading=payload.get("heading", ""),
            last_modified=datetime.fromisoformat(payload.get("last_modified", datetime.utcnow().isoformat())),
            score=score,
        )


class DocumentRepository:
    """Repository for storing and searching vault documents in Qdrant."""

    def __init__(self):
        self._qdrant = get_qdrant_client()
        self._embeddings = get_embedding_service()

    async def index_document(
        self,
        path: str,
        content: str,
        title: str | None = None,
        last_modified: datetime | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> int:
        """Index a document by chunking and storing embeddings.

        Args:
            path: Document path in vault
            content: Document content
            title: Document title (extracted from path if not provided)
            last_modified: Last modification time
            chunk_size: Target tokens per chunk
            chunk_overlap: Overlap between chunks

        Returns:
            Number of chunks indexed
        """
        if not content.strip():
            return 0

        # Extract title from path if not provided
        if title is None:
            title = path.split("/")[-1].replace(".md", "")

        if last_modified is None:
            last_modified = datetime.utcnow()

        # Delete existing chunks for this document
        await self.delete_by_path(path)

        # Chunk the document
        chunks = chunk_document(content, path, chunk_size, chunk_overlap)

        if not chunks:
            return 0

        # Generate embeddings for all chunks
        chunk_texts = [c.content for c in chunks]
        embeddings = await self._embeddings.embed_texts(chunk_texts)

        # Prepare points for batch upsert
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{path}::{chunk.chunk_index}"

            payload = {
                "path": path,
                "content": chunk.content,
                "chunk_index": chunk.chunk_index,
                "title": title,
                "heading": chunk.metadata.get("heading", ""),
                "last_modified": last_modified.isoformat(),
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            }

            points.append((chunk_id, embedding, payload))

        # Batch upsert
        await self._qdrant.upsert_points_batch(
            collection_name=DOCUMENTS_COLLECTION,
            points=points,
        )

        logger.info(
            "document_indexed",
            path=path,
            chunks=len(chunks),
            title=title,
        )

        return len(chunks)

    async def search_similar(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.5,
        path_filter: str | None = None,
    ) -> list[IndexedDocument]:
        """Search for similar document chunks.

        Args:
            query: Search query
            limit: Maximum results
            min_score: Minimum similarity score
            path_filter: Optional path prefix filter

        Returns:
            List of IndexedDocument results
        """
        # Generate query embedding
        query_embedding = await self._embeddings.embed_query(query)

        # Build filter if path specified
        filter_conditions = None
        if path_filter:
            filter_conditions = models.Filter(
                must=[
                    models.FieldCondition(
                        key="path",
                        match=models.MatchText(text=path_filter),
                    )
                ]
            )

        # Search
        results = await self._qdrant.search(
            collection_name=DOCUMENTS_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=min_score,
            filter_conditions=filter_conditions,
        )

        # Convert to IndexedDocument objects
        documents = []
        for chunk_id, score, payload in results:
            doc = IndexedDocument.from_payload(chunk_id, payload, score)
            documents.append(doc)

        logger.debug(
            "documents_searched",
            query_length=len(query),
            results_count=len(documents),
        )

        return documents

    async def delete_by_path(self, path: str) -> int:
        """Delete all chunks for a document path.

        Args:
            path: Document path

        Returns:
            Number of chunks deleted (approximate)
        """
        filter_conditions = models.Filter(
            must=[
                models.FieldCondition(
                    key="path",
                    match=models.MatchValue(value=path),
                )
            ]
        )

        count = await self._qdrant.delete_by_filter(
            collection_name=DOCUMENTS_COLLECTION,
            filter_conditions=filter_conditions,
        )

        if count > 0:
            logger.debug("document_chunks_deleted", path=path, count=count)

        return count

    async def get_indexed_paths(self) -> list[str]:
        """Get list of all indexed document paths.

        Returns:
            List of unique paths
        """
        client = await self._qdrant._get_client()

        # Scroll through all documents to get unique paths
        paths = set()
        offset = None

        while True:
            results, offset = await client.scroll(
                collection_name=DOCUMENTS_COLLECTION,
                limit=100,
                offset=offset,
                with_payload=["path"],
                with_vectors=False,
            )

            for point in results:
                if point.payload:
                    paths.add(point.payload.get("path", ""))

            if offset is None:
                break

        return sorted(paths)

    async def get_document_chunks(self, path: str) -> list[IndexedDocument]:
        """Get all chunks for a specific document.

        Args:
            path: Document path

        Returns:
            List of chunks sorted by index
        """
        client = await self._qdrant._get_client()

        filter_conditions = models.Filter(
            must=[
                models.FieldCondition(
                    key="path",
                    match=models.MatchValue(value=path),
                )
            ]
        )

        results, _ = await client.scroll(
            collection_name=DOCUMENTS_COLLECTION,
            scroll_filter=filter_conditions,
            limit=100,
            with_payload=True,
            with_vectors=False,
        )

        chunks = [
            IndexedDocument.from_payload(str(point.id), point.payload or {})
            for point in results
        ]

        # Sort by chunk index
        chunks.sort(key=lambda c: c.chunk_index)

        return chunks

    async def count_documents(self) -> dict[str, int]:
        """Get document and chunk counts.

        Returns:
            Dict with 'documents' and 'chunks' counts
        """
        total_chunks = await self._qdrant.count_points(DOCUMENTS_COLLECTION)
        paths = await self.get_indexed_paths()

        return {
            "documents": len(paths),
            "chunks": total_chunks,
        }


# Singleton instance
_document_repository: DocumentRepository | None = None


def get_document_repository() -> DocumentRepository:
    """Get the singleton document repository instance."""
    global _document_repository
    if _document_repository is None:
        _document_repository = DocumentRepository()
    return _document_repository
