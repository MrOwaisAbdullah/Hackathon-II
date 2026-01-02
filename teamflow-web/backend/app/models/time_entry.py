"""Time Entry models for tracking work hours on tasks."""
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field as PDField
from sqlmodel import Field, Relationship, SQLModel


class TimeEntry(SQLModel, table=True):
    """Time Entry database table model.

    Tracks time spent by users on tasks for profitability calculation.
    """

    __tablename__ = "time_entries"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    duration_minutes: int = Field(index=True)  # Duration in minutes
    note: Optional[str] = Field(default=None, max_length=1000)
    entry_date: Optional[date] = Field(default=None, index=True)  # Date of work, defaults to today
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional["Task"] = Relationship(back_populates="time_entries")
    user: Optional["User"] = Relationship(back_populates="time_entries")


# Pydantic schemas for API operations
class TimeEntryBase(SQLModel):
    """Base time entry schema."""

    task_id: UUID = PDField(..., description="ID of the task this time entry is for")
    duration_minutes: int = PDField(..., gt=0, le=1440, description="Duration in minutes (max 24 hours)")
    note: Optional[str] = PDField(None, max_length=1000)
    entry_date: Optional[date] = None


class TimeEntryCreate(TimeEntryBase):
    """Time entry creation schema."""

    pass


class TimeEntryUpdate(SQLModel):
    """Time entry update schema."""

    duration_minutes: Optional[int] = PDField(None, gt=0, le=1440)
    note: Optional[str] = PDField(None, max_length=1000)
    entry_date: Optional[date] = None


class TimeEntryRead(TimeEntryBase):
    """Time entry read/response schema."""

    id: UUID
    user_id: UUID
    agency_id: UUID
    created_at: datetime


# Import related models for relationships
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User
