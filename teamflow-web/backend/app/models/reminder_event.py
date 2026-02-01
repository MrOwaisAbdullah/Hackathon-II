"""
T068: ReminderEvent Pydantic Model

Defines the data structure for reminder events with status tracking
(pending/sent/failed) for the notification service.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReminderEventStatus(str, Enum):
    """Status of a reminder event"""

    PENDING = "PENDING"  # Reminder scheduled but not yet sent
    SENT = "SENT"  # Reminder successfully sent
    FAILED = "FAILED"  # Reminder failed after max retries


class ReminderEvent(BaseModel):
    """
    Represents a reminder event for due date notifications.

    This model tracks reminders that need to be sent before task deadlines.
    It includes retry logic and status tracking for reliable delivery.
    """

    id: UUID = Field(description="Unique identifier for the reminder event")
    task_id: UUID = Field(description="ID of the task this reminder is for")
    agency_id: UUID = Field(description="ID of the agency")
    user_id: UUID = Field(description="ID of the user to notify")

    status: ReminderEventStatus = Field(
        default=ReminderEventStatus.PENDING,
        description="Current status of the reminder",
    )

    remind_at: datetime = Field(description="When to send the reminder (UTC)")
    due_date: datetime = Field(description="Task due date (UTC)")

    task_title: str = Field(description="Title of the task")
    task_description: Optional[str] = Field(default=None, description="Task description")

    user_email: str = Field(description="Email address of the user")
    user_name: str = Field(description="Name of the user")

    error_message: Optional[str] = Field(
        default=None,
        description="Error message if sending failed",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of retry attempts",
    )
    last_retry_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last retry attempt",
    )

    created_at: datetime = Field(description="When the reminder was created")
    updated_at: Optional[datetime] = Field(
        default=None,
        description="When the reminder was last updated",
    )


class ReminderEventCreate(BaseModel):
    """Request model for creating a reminder event"""

    task_id: UUID
    agency_id: UUID
    user_id: UUID
    remind_at: datetime
    due_date: datetime
    task_title: str
    task_description: Optional[str] = None
    user_email: str
    user_name: str


class ReminderEventUpdate(BaseModel):
    """Request model for updating a reminder event status"""

    status: Optional[ReminderEventStatus] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    last_retry_at: Optional[datetime] = None


class ReminderEventResponse(ReminderEvent):
    """Response model for reminder event with computed fields"""

    time_until_due: Optional[str] = Field(
        default=None,
        description="Human-readable time until due date",
    )
    is_overdue: bool = Field(
        default=False,
        description="Whether the reminder time has passed",
    )

    @classmethod
    def from_reminder_event(cls, event: ReminderEvent) -> "ReminderEventResponse":
        """Create a response from a ReminderEvent with computed fields"""
        now = datetime.utcnow()
        is_overdue = event.remind_at < now

        # Calculate time until due
        time_until = None
        if not is_overdue:
            delta = event.remind_at - now
            hours = delta.total_seconds() / 3600
            if hours < 1:
                minutes = int(delta.total_seconds() / 60)
                time_until = f"{minutes} minute{'s' if minutes != 1 else ''}"
            elif hours < 24:
                time_until = f"{int(hours)} hour{'s' if int(hours) != 1 else ''}"
            else:
                days = int(hours / 24)
                time_until = f"{days} day{'s' if days != 1 else ''}"

        return cls(
            **event.model_dump(),
            time_until_due=time_until,
            is_overdue=is_overdue,
        )
