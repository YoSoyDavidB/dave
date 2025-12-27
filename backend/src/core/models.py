import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database import Base


class ErrorCategory(str, Enum):
    """Categories of English errors."""

    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    SPELLING = "spelling"
    EXPRESSION = "expression"


class User(Base):
    """Model for application users."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.email}>"


class EnglishCorrection(Base):
    """Model for tracking English corrections."""

    __tablename__ = "english_corrections"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

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


class Conversation(Base):
    """Model for chat conversations."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Title (auto-generated from first message or set manually)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship to messages
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.id}: {self.title or 'Untitled'}>"


class Message(Base):
    """Model for individual chat messages."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Foreign key to conversation
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

    # Message content
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional metadata
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tools_used: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array as string

    # Relationship
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message {self.id}: {self.role} - {self.content[:30]}...>"


class DailySummaryModel(Base):
    """Model for storing daily summaries and insights."""

    __tablename__ = "daily_summaries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Task metrics
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tasks_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tasks_pending: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Goal metrics
    goals_updated: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    goals_progress_delta: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Conversation metrics
    conversations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # English learning metrics
    english_corrections: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Productivity score
    productivity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # AI-generated insights
    top_topics: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    key_achievements: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    suggestions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<DailySummary {self.id}: {self.user_id} - {self.date}>"


class FocusSessionModel(Base):
    """Model for storing focus sessions."""

    __tablename__ = "focus_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Session type and status
    session_type: Mapped[str] = mapped_column(String(20), default="pomodoro", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)

    # Time tracking
    duration_minutes: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Notes and metadata
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    interruptions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<FocusSession {self.id}: {self.user_id} - {self.status}>"


class TaskModel(Base):
    """Model for storing user tasks."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    # Status and priority
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)

    # Time tracking
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Integration with focus sessions
    focus_session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Organization
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Task {self.id}: {self.title} - {self.status}>"
