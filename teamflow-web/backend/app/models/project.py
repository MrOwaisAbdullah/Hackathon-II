"""Project models."""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import Field as PDField
from sqlmodel import Field, Relationship, SQLModel


class ProjectStatus(str, Enum):
    """Project status enum."""
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    archived = "archived"


class Project(SQLModel, table=True):
    """Project database table model."""

    __tablename__ = "projects"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.active, index=True)
    hourly_rate: Optional[int] = Field(default=None)  # For profitability tracking
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="project")


# Pydantic schemas for API operations
class ProjectBase(SQLModel):
    """Base project schema."""

    name: str = PDField(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: ProjectStatus = Field(default=ProjectStatus.active)
    hourly_rate: Optional[int] = None


class ProjectCreate(ProjectBase):
    """Project creation schema."""

    pass


class ProjectUpdate(SQLModel):
    """Project update schema."""

    name: Optional[str] = PDField(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    hourly_rate: Optional[int] = None


class ProjectRead(ProjectBase):
    """Project read/response schema."""

    id: UUID
    agency_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


# Import Task for relationships
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.task import Task
