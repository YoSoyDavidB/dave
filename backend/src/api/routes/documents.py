"""Document upload and management API routes."""

import io
from typing import Any

import structlog
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.domain.entities.document import DocumentCategory
from src.infrastructure.vector_store.uploaded_document_repository import (
    get_uploaded_document_repository,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/documents", tags=["documents"])

# Supported file types and their extractors
SUPPORTED_TYPES = {
    "text/plain": "text",
    "text/markdown": "text",
    "text/csv": "text",
    "application/json": "text",
    "application/pdf": "pdf",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class DocumentResponse(BaseModel):
    """Response for a single document."""

    id: str
    user_id: str
    filename: str
    original_filename: str
    content_type: str
    category: str
    tags: list[str]
    description: str
    file_size: int
    created_at: str
    updated_at: str
    indexed: bool
    chunk_count: int


class DocumentListResponse(BaseModel):
    """Response for document list."""

    documents: list[DocumentResponse]
    total: int


class DocumentStatsResponse(BaseModel):
    """Response for document statistics."""

    total_documents: int
    total_chunks: int
    total_size_bytes: int
    by_category: dict[str, int]


class DocumentUpdateRequest(BaseModel):
    """Request to update document metadata."""

    category: str | None = None
    tags: list[str] | None = None
    description: str | None = None


class DocumentSearchResult(BaseModel):
    """A search result."""

    chunk_id: str
    score: float
    content: str
    document_id: str
    filename: str
    category: str
    chunk_index: int


class DocumentSearchResponse(BaseModel):
    """Response for document search."""

    results: list[DocumentSearchResult]
    total: int


# Static routes must come before dynamic routes
@router.get("/categories/list")
async def list_categories() -> dict[str, Any]:
    """List available document categories."""
    return {"categories": [{"value": c.value, "label": c.value.title()} for c in DocumentCategory]}


async def extract_text_content(file: UploadFile, content_type: str) -> str:
    """Extract text content from uploaded file.

    Args:
        file: Uploaded file
        content_type: MIME type

    Returns:
        Extracted text content
    """
    content = await file.read()

    extractor = SUPPORTED_TYPES.get(content_type)

    if extractor == "text":
        # Direct text files
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")

    elif extractor == "pdf":
        # PDF extraction using pypdf
        try:
            import pypdf

            pdf_reader = pypdf.PdfReader(io.BytesIO(content))
            text_parts = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error("pdf_extraction_failed", error=str(e))
            raise HTTPException(
                status_code=400, detail=f"Failed to extract text from PDF: {str(e)}"
            )

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    category: str = Form(...),
    tags: str = Form(""),  # Comma-separated
    description: str = Form(""),
) -> DocumentResponse:
    """Upload and index a new document.

    Supported file types:
    - Text files (.txt, .md, .csv, .json)
    - PDF files (.pdf)
    """
    # Validate file type
    content_type = file.content_type or "application/octet-stream"
    if content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {content_type}. Supported: "
                f"{list(SUPPORTED_TYPES.keys())}"
            ),
        )

    # Validate category
    try:
        doc_category = DocumentCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}. Valid: {[c.value for c in DocumentCategory]}",
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Reset file position for extraction
    await file.seek(0)

    # Extract text
    text_content = await extract_text_content(file, content_type)

    if not text_content.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from file. File may be empty or corrupted.",
        )

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # Create document
    repo = get_uploaded_document_repository()

    # Generate stored filename
    import uuid

    stored_filename = f"{uuid.uuid4()}{_get_extension(file.filename or 'file')}"

    doc = await repo.create_document(
        user_id=user_id,
        filename=stored_filename,
        original_filename=file.filename or "unnamed",
        content_type=content_type,
        content=text_content,
        file_size=file_size,
        category=doc_category,
        tags=tag_list,
        description=description,
    )

    return DocumentResponse(
        id=str(doc.document_id),
        user_id=doc.user_id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        content_type=doc.content_type,
        category=doc.category.value,
        tags=doc.tags,
        description=doc.description,
        file_size=doc.file_size,
        created_at=doc.created_at.isoformat(),
        updated_at=doc.updated_at.isoformat(),
        indexed=doc.indexed,
        chunk_count=doc.chunk_count,
    )


def _get_extension(filename: str) -> str:
    """Get file extension including the dot."""
    if "." in filename:
        return "." + filename.rsplit(".", 1)[1]
    return ""


@router.get("/{user_id}", response_model=DocumentListResponse)
async def list_documents(
    user_id: str,
    category: str | None = None,
    tags: str | None = None,  # Comma-separated
    limit: int = 100,
) -> DocumentListResponse:
    """List documents for a user."""
    repo = get_uploaded_document_repository()

    doc_category = None
    if category:
        try:
            doc_category = DocumentCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None

    documents = await repo.list_documents(
        user_id=user_id,
        category=doc_category,
        tags=tag_list,
        limit=limit,
    )

    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=str(doc.document_id),
                user_id=doc.user_id,
                filename=doc.filename,
                original_filename=doc.original_filename,
                content_type=doc.content_type,
                category=doc.category.value,
                tags=doc.tags,
                description=doc.description,
                file_size=doc.file_size,
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat(),
                indexed=doc.indexed,
                chunk_count=doc.chunk_count,
            )
            for doc in documents
        ],
        total=len(documents),
    )


@router.get("/{user_id}/stats", response_model=DocumentStatsResponse)
async def get_document_stats(user_id: str) -> DocumentStatsResponse:
    """Get document statistics for a user."""
    repo = get_uploaded_document_repository()
    stats = await repo.get_stats(user_id)

    return DocumentStatsResponse(
        total_documents=stats["total_documents"],
        total_chunks=stats["total_chunks"],
        total_size_bytes=stats["total_size_bytes"],
        by_category=stats["by_category"],
    )


@router.get("/{user_id}/{document_id}", response_model=DocumentResponse)
async def get_document(user_id: str, document_id: str) -> DocumentResponse:
    """Get a specific document."""
    repo = get_uploaded_document_repository()
    doc = await repo.get_document(document_id)

    if doc is None or doc.user_id != user_id:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=str(doc.document_id),
        user_id=doc.user_id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        content_type=doc.content_type,
        category=doc.category.value,
        tags=doc.tags,
        description=doc.description,
        file_size=doc.file_size,
        created_at=doc.created_at.isoformat(),
        updated_at=doc.updated_at.isoformat(),
        indexed=doc.indexed,
        chunk_count=doc.chunk_count,
    )


@router.patch("/{user_id}/{document_id}", response_model=DocumentResponse)
async def update_document(
    user_id: str,
    document_id: str,
    request: DocumentUpdateRequest,
) -> DocumentResponse:
    """Update document metadata."""
    repo = get_uploaded_document_repository()

    # Verify document exists and belongs to user
    doc = await repo.get_document(document_id)
    if doc is None or doc.user_id != user_id:
        raise HTTPException(status_code=404, detail="Document not found")

    # Parse category if provided
    doc_category = None
    if request.category:
        try:
            doc_category = DocumentCategory(request.category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {request.category}")

    updated_doc = await repo.update_document(
        document_id=document_id,
        category=doc_category,
        tags=request.tags,
        description=request.description,
    )

    if updated_doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=str(updated_doc.document_id),
        user_id=updated_doc.user_id,
        filename=updated_doc.filename,
        original_filename=updated_doc.original_filename,
        content_type=updated_doc.content_type,
        category=updated_doc.category.value,
        tags=updated_doc.tags,
        description=updated_doc.description,
        file_size=updated_doc.file_size,
        created_at=updated_doc.created_at.isoformat(),
        updated_at=updated_doc.updated_at.isoformat(),
        indexed=updated_doc.indexed,
        chunk_count=updated_doc.chunk_count,
    )


@router.delete("/{user_id}/{document_id}")
async def delete_document(user_id: str, document_id: str) -> dict[str, str]:
    """Delete a document and its chunks."""
    repo = get_uploaded_document_repository()

    # Verify document exists and belongs to user
    doc = await repo.get_document(document_id)
    if doc is None or doc.user_id != user_id:
        raise HTTPException(status_code=404, detail="Document not found")

    deleted = await repo.delete_document(document_id)

    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete document")

    return {"status": "deleted", "document_id": document_id}


@router.post("/{user_id}/search", response_model=DocumentSearchResponse)
async def search_documents(
    user_id: str,
    query: str,
    category: str | None = None,
    limit: int = 10,
    min_score: float = 0.5,
) -> DocumentSearchResponse:
    """Search within uploaded documents."""
    repo = get_uploaded_document_repository()

    doc_category = None
    if category:
        try:
            doc_category = DocumentCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    results = await repo.search_documents(
        query=query,
        user_id=user_id,
        category=doc_category,
        limit=limit,
        min_score=min_score,
    )

    return DocumentSearchResponse(
        results=[
            DocumentSearchResult(
                chunk_id=r["chunk_id"],
                score=r["score"],
                content=r["content"],
                document_id=r["document_id"],
                filename=r["filename"],
                category=r["category"],
                chunk_index=r["chunk_index"],
            )
            for r in results
        ],
        total=len(results),
    )
