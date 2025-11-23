"""Repository for uploaded documents metadata and indexing."""

import hashlib
import uuid
from datetime import datetime
from typing import Any

import structlog
from qdrant_client.http import models

from src.domain.entities.document import Document, DocumentCategory
from src.infrastructure.embeddings import get_embedding_service
from src.infrastructure.vector_store.qdrant_client import get_qdrant_client
from src.infrastructure.vector_store.chunking import chunk_document

logger = structlog.get_logger()

# Collection names
UPLOADED_DOCS_COLLECTION = "uploaded_documents"
UPLOADED_CHUNKS_COLLECTION = "uploaded_chunks"


class UploadedDocumentRepository:
    """Repository for managing uploaded documents."""

    def __init__(self):
        self._qdrant = get_qdrant_client()
        self._embeddings = get_embedding_service()

    async def ensure_collections(self) -> None:
        """Ensure required collections exist."""
        # Collection for document metadata (no vectors needed)
        await self._qdrant.ensure_collection(
            UPLOADED_DOCS_COLLECTION,
            vector_size=1536,  # Required but we'll use dummy vectors
        )
        # Collection for document chunks with embeddings
        await self._qdrant.ensure_collection(UPLOADED_CHUNKS_COLLECTION)

    async def create_document(
        self,
        user_id: str,
        filename: str,
        original_filename: str,
        content_type: str,
        content: str,
        file_size: int,
        category: DocumentCategory,
        tags: list[str] | None = None,
        description: str = "",
    ) -> Document:
        """Create and index a new document.

        Args:
            user_id: Owner user ID
            filename: Stored filename (UUID-based)
            original_filename: Original upload filename
            content_type: MIME type
            content: Document text content
            file_size: File size in bytes
            category: Document category
            tags: Optional tags
            description: Optional description

        Returns:
            Created Document
        """
        doc = Document(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            content_type=content_type,
            category=category,
            tags=tags or [],
            description=description,
            file_size=file_size,
        )

        # Index the document content
        chunk_count = await self._index_document_content(doc, content)
        doc.indexed = True
        doc.chunk_count = chunk_count

        # Store document metadata
        # Use a dummy embedding for metadata storage
        dummy_embedding = [0.0] * 1536
        await self._qdrant.upsert_point(
            collection_name=UPLOADED_DOCS_COLLECTION,
            point_id=str(doc.document_id),
            vector=dummy_embedding,
            payload=doc.to_payload(),
        )

        logger.info(
            "document_created",
            document_id=str(doc.document_id),
            filename=original_filename,
            category=category.value,
            chunks=chunk_count,
        )

        return doc

    async def _index_document_content(self, doc: Document, content: str) -> int:
        """Index document content into chunks.

        Args:
            doc: Document metadata
            content: Text content to index

        Returns:
            Number of chunks created
        """
        if not content.strip():
            return 0

        # Chunk the content
        chunks = chunk_document(
            content=content,
            path=f"uploads/{doc.category.value}/{doc.original_filename}",
            chunk_size=500,
            chunk_overlap=50,
        )

        if not chunks:
            return 0

        # Generate embeddings
        chunk_texts = [c.content for c in chunks]
        embeddings = await self._embeddings.embed_texts(chunk_texts)

        # Prepare points
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_key = f"{doc.document_id}::{chunk.chunk_index}"
            chunk_id = str(uuid.UUID(hashlib.md5(chunk_key.encode()).hexdigest()))

            payload = {
                "document_id": str(doc.document_id),
                "user_id": doc.user_id,
                "chunk_key": chunk_key,
                "content": chunk.content,
                "chunk_index": chunk.chunk_index,
                "category": doc.category.value,
                "tags": doc.tags,
                "filename": doc.original_filename,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            }

            points.append((chunk_id, embedding, payload))

        # Batch upsert
        await self._qdrant.upsert_points_batch(
            collection_name=UPLOADED_CHUNKS_COLLECTION,
            points=points,
        )

        return len(chunks)

    async def get_document(self, document_id: str) -> Document | None:
        """Get document by ID.

        Args:
            document_id: Document UUID

        Returns:
            Document or None if not found
        """
        result = await self._qdrant.get_point(
            collection_name=UPLOADED_DOCS_COLLECTION,
            point_id=document_id,
        )

        if result is None:
            return None

        _, payload = result
        return Document.from_payload(payload)

    async def list_documents(
        self,
        user_id: str,
        category: DocumentCategory | None = None,
        tags: list[str] | None = None,
        limit: int = 100,
    ) -> list[Document]:
        """List documents for a user.

        Args:
            user_id: User ID
            category: Optional category filter
            tags: Optional tags filter
            limit: Maximum documents to return

        Returns:
            List of documents
        """
        client = await self._qdrant._get_client()

        # Build filter
        must_conditions = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]

        if category:
            must_conditions.append(
                models.FieldCondition(
                    key="category",
                    match=models.MatchValue(value=category.value),
                )
            )

        if tags:
            for tag in tags:
                must_conditions.append(
                    models.FieldCondition(
                        key="tags",
                        match=models.MatchAny(any=[tag]),
                    )
                )

        filter_conditions = models.Filter(must=must_conditions)

        results, _ = await client.scroll(
            collection_name=UPLOADED_DOCS_COLLECTION,
            scroll_filter=filter_conditions,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        documents = []
        for point in results:
            if point.payload:
                documents.append(Document.from_payload(point.payload))

        # Sort by created_at descending
        documents.sort(key=lambda d: d.created_at, reverse=True)

        return documents

    async def update_document(
        self,
        document_id: str,
        category: DocumentCategory | None = None,
        tags: list[str] | None = None,
        description: str | None = None,
    ) -> Document | None:
        """Update document metadata.

        Args:
            document_id: Document ID
            category: New category (optional)
            tags: New tags (optional)
            description: New description (optional)

        Returns:
            Updated document or None if not found
        """
        doc = await self.get_document(document_id)
        if doc is None:
            return None

        if category is not None:
            doc.category = category
        if tags is not None:
            doc.tags = tags
        if description is not None:
            doc.description = description

        doc.updated_at = datetime.utcnow()

        # Update metadata
        dummy_embedding = [0.0] * 1536
        await self._qdrant.upsert_point(
            collection_name=UPLOADED_DOCS_COLLECTION,
            point_id=str(doc.document_id),
            vector=dummy_embedding,
            payload=doc.to_payload(),
        )

        # Update chunk payloads if category or tags changed
        if category is not None or tags is not None:
            await self._update_chunk_metadata(doc)

        logger.info("document_updated", document_id=document_id)

        return doc

    async def _update_chunk_metadata(self, doc: Document) -> None:
        """Update metadata in all chunks for a document."""
        client = await self._qdrant._get_client()

        filter_conditions = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=str(doc.document_id)),
                )
            ]
        )

        # Update payload fields
        await client.set_payload(
            collection_name=UPLOADED_CHUNKS_COLLECTION,
            payload={
                "category": doc.category.value,
                "tags": doc.tags,
            },
            points=filter_conditions,
        )

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks.

        Args:
            document_id: Document ID

        Returns:
            True if deleted
        """
        # Delete chunks first
        client = await self._qdrant._get_client()

        chunk_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id),
                )
            ]
        )

        await client.delete(
            collection_name=UPLOADED_CHUNKS_COLLECTION,
            points_selector=models.FilterSelector(filter=chunk_filter),
        )

        # Delete document metadata
        deleted = await self._qdrant.delete_point(
            collection_name=UPLOADED_DOCS_COLLECTION,
            point_id=document_id,
        )

        if deleted:
            logger.info("document_deleted", document_id=document_id)

        return deleted

    async def search_documents(
        self,
        query: str,
        user_id: str,
        category: DocumentCategory | None = None,
        limit: int = 10,
        min_score: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Search uploaded documents.

        Args:
            query: Search query
            user_id: User ID
            category: Optional category filter
            limit: Maximum results
            min_score: Minimum similarity score

        Returns:
            List of search results with content and metadata
        """
        query_embedding = await self._embeddings.embed_query(query)

        # Build filter
        must_conditions = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]

        if category:
            must_conditions.append(
                models.FieldCondition(
                    key="category",
                    match=models.MatchValue(value=category.value),
                )
            )

        filter_conditions = models.Filter(must=must_conditions)

        results = await self._qdrant.search(
            collection_name=UPLOADED_CHUNKS_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=min_score,
            filter_conditions=filter_conditions,
        )

        return [
            {
                "chunk_id": chunk_id,
                "score": score,
                "content": payload.get("content", ""),
                "document_id": payload.get("document_id"),
                "filename": payload.get("filename"),
                "category": payload.get("category"),
                "chunk_index": payload.get("chunk_index"),
            }
            for chunk_id, score, payload in results
        ]

    async def get_stats(self, user_id: str) -> dict[str, Any]:
        """Get document statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Statistics dict
        """
        documents = await self.list_documents(user_id, limit=1000)

        by_category: dict[str, int] = {}
        total_size = 0
        total_chunks = 0

        for doc in documents:
            cat = doc.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            total_size += doc.file_size
            total_chunks += doc.chunk_count

        return {
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "total_size_bytes": total_size,
            "by_category": by_category,
        }


# Singleton instance
_uploaded_doc_repo: UploadedDocumentRepository | None = None


def get_uploaded_document_repository() -> UploadedDocumentRepository:
    """Get the singleton uploaded document repository."""
    global _uploaded_doc_repo
    if _uploaded_doc_repo is None:
        _uploaded_doc_repo = UploadedDocumentRepository()
    return _uploaded_doc_repo
