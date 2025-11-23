"""Document entity for uploaded files."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentCategory(str, Enum):
    """Categories for organizing documents."""

    MANUAL = "manual"
    INVOICE = "invoice"
    CONTRACT = "contract"
    RECEIPT = "receipt"
    NOTE = "note"
    REPORT = "report"
    GUIDE = "guide"
    REFERENCE = "reference"
    PERSONAL = "personal"
    WORK = "work"
    OTHER = "other"


class Document(BaseModel):
    """Represents an uploaded document."""

    document_id: UUID = Field(default_factory=uuid4)
    user_id: str
    filename: str
    original_filename: str
    content_type: str  # MIME type
    category: DocumentCategory
    tags: list[str] = Field(default_factory=list)
    description: str = ""
    file_size: int  # bytes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    indexed: bool = False
    chunk_count: int = 0

    def to_payload(self) -> dict:
        """Convert to Qdrant payload format."""
        return {
            "document_id": str(self.document_id),
            "user_id": self.user_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "content_type": self.content_type,
            "category": self.category.value,
            "tags": self.tags,
            "description": self.description,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "indexed": self.indexed,
            "chunk_count": self.chunk_count,
        }

    @classmethod
    def from_payload(cls, payload: dict) -> "Document":
        """Create from Qdrant payload."""
        return cls(
            document_id=UUID(payload["document_id"]),
            user_id=payload["user_id"],
            filename=payload["filename"],
            original_filename=payload["original_filename"],
            content_type=payload["content_type"],
            category=DocumentCategory(payload["category"]),
            tags=payload.get("tags", []),
            description=payload.get("description", ""),
            file_size=payload["file_size"],
            created_at=datetime.fromisoformat(payload["created_at"]),
            updated_at=datetime.fromisoformat(payload["updated_at"]),
            indexed=payload.get("indexed", False),
            chunk_count=payload.get("chunk_count", 0),
        )
