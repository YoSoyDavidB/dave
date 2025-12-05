"""Focus session domain entity."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FocusSessionStatus(str, Enum):
    """Focus session status."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FocusSessionType(str, Enum):
    """Focus session type."""

    POMODORO = "pomodoro"  # 25 min work / 5 min break
    CUSTOM = "custom"  # Custom duration


class FocusSession(BaseModel):
    """Focus session entity representing a focused work period."""

    session_id: UUID = Field(default_factory=uuid4)
    user_id: str
    task_id: str | None = None  # Optional link to a specific task
    session_type: FocusSessionType = FocusSessionType.POMODORO
    status: FocusSessionStatus = FocusSessionStatus.ACTIVE

    # Time tracking
    duration_minutes: int = 25  # Default Pomodoro duration
    elapsed_seconds: int = 0  # Time actually spent (for pause/resume)
    started_at: datetime = Field(default_factory=datetime.now)
    paused_at: datetime | None = None
    completed_at: datetime | None = None

    # Notes and metadata
    notes: str = ""
    interruptions: int = 0  # Track how many times session was interrupted

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def complete(self) -> None:
        """Mark session as completed."""
        self.status = FocusSessionStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def cancel(self) -> None:
        """Cancel the session."""
        self.status = FocusSessionStatus.CANCELLED
        self.updated_at = datetime.now()

    def pause(self) -> None:
        """Pause the session."""
        if self.status == FocusSessionStatus.ACTIVE:
            self.status = FocusSessionStatus.PAUSED
            self.paused_at = datetime.now()
            self.interruptions += 1
            self.updated_at = datetime.now()

    def resume(self) -> None:
        """Resume a paused session."""
        if self.status == FocusSessionStatus.PAUSED:
            self.status = FocusSessionStatus.ACTIVE
            # Add pause duration to elapsed time
            if self.paused_at:
                pause_duration = (datetime.now() - self.paused_at).total_seconds()
                self.elapsed_seconds += int(pause_duration)
            self.paused_at = None
            self.updated_at = datetime.now()

    def get_remaining_seconds(self) -> int:
        """Calculate remaining seconds in the session."""
        target_seconds = self.duration_minutes * 60
        if self.status == FocusSessionStatus.COMPLETED:
            return 0

        if self.status == FocusSessionStatus.PAUSED:
            return max(0, target_seconds - self.elapsed_seconds)

        # Active session
        actual_elapsed = (datetime.now() - self.started_at).total_seconds() - self.elapsed_seconds
        return max(0, int(target_seconds - actual_elapsed))

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return self.get_remaining_seconds() == 0 and self.status == FocusSessionStatus.ACTIVE

    model_config = {"use_enum_values": False}
