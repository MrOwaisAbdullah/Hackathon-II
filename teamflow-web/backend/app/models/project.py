"""Project models."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import Field as PDField, field_validator
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
    status: Optional[Union[ProjectStatus, str]] = None
    hourly_rate: Optional[int] = None

    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v: Any) -> Optional[ProjectStatus]:
        """Validate and convert status string to ProjectStatus enum."""
        if v is None:
            return None
        if isinstance(v, ProjectStatus):
            return v
        # If it's a string, convert to enum
        if isinstance(v, str):
            try:
                return ProjectStatus(v)
            except ValueError:
                raise ValueError(f"Invalid status value: {v}. Must be one of: {', '.join([s.value for s in ProjectStatus])}")
        raise ValueError(f"Status must be a string or ProjectStatus enum, got {type(v)}")


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
