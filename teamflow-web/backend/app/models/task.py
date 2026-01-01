"""Task models."""
from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import Field as PDField
from sqlmodel import Field, Relationship, SQLModel


class TaskStatus(str, Enum):
    """Task status values."""

    TODO = "todo"
    DOING = "doing"
    REVIEW = "review"
    DONE = "done"


class TaskPriority(str, Enum):
    """Task priority values."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


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


# Import User and Project for relationships
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
