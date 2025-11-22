from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class ErrorCategory(str, Enum):
    """Categories of English errors."""

    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    SPELLING = "spelling"
    EXPRESSION = "expression"


class EnglishCorrection(Base):
    """Model for tracking English corrections."""

    __tablename__ = "english_corrections"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # The error details
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    # Categorization
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Context
    conversation_context: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<EnglishCorrection {self.id}: {self.original_text[:30]}...>"
