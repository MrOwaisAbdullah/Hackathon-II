"""Task models."""
from datetime import date, datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING, Any
from uuid import UUID, uuid4

from pydantic import Field as PDField
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class TaskStatus(str, Enum):
    """Task status values."""

    TODO = "TODO"
    DOING = "DOING"
    REVIEW = "REVIEW"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"


class TaskPriority(str, Enum):
    """Task priority values."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Task(SQLModel, table=True):
    """Task database table model."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    priority: Optional[TaskPriority] = Field(default=None)
    project_id: Optional[UUID] = Field(default=None, foreign_key="projects.id")
    assignee_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    due_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Optional["Project"] = Relationship(back_populates="tasks")
    assignee: Optional["User"] = Relationship(back_populates="assigned_tasks")
    time_entries: list["TimeEntry"] = Relationship(back_populates="task")


# Pydantic schemas for API operations
class TaskBase(SQLModel):
    """Base task schema."""

    title: str = PDField(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = PDField(default=TaskStatus.TODO)
    priority: Optional[TaskPriority] = None
    project_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    """Task creation schema."""

    pass


class TaskUpdate(SQLModel):
    """Task update schema."""

    title: Optional[str] = PDField(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    project_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None
    due_date: Optional[date] = None


class TaskRead(TaskBase):
    """Task read/response schema."""

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Include assignee data (populated from relationship)
    # Using Any to avoid forward reference issues with Pydantic v2
    assignee: Optional[Any] = None

    class Config:
        from_attributes = True


class TaskAssign(SQLModel):
    """Task assignment schema."""

    assignee_id: UUID = PDField(..., description="ID of the user to assign the task to")


# Import User and Project for relationships
if TYPE_CHECKING:
    from app.models.user import User, UserRead
    from app.models.project import Project
