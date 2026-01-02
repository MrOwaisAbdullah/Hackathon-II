"""All database models and Pydantic schemas."""

# Import all models to ensure they're registered with SQLModel.metadata
from app.models.agency import (
    Agency,
    AgencyCreate,
    AgencyRead,
    AgencyBase,
)
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
    ProjectBase,
)
from app.models.task import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TaskBase,
    TaskPriority,
    TaskStatus,
)
from app.models.time_entry import (
    TimeEntry,
    TimeEntryCreate,
    TimeEntryUpdate,
    TimeEntryRead,
    TimeEntryBase,
)
from app.models.user import (
    User,
    UserCreate,
    UserLogin,
    UserRead,
    UserRole,
    UserBase,
)

__all__ = [
    # Agency models
    "Agency",
    "AgencyCreate",
    "AgencyRead",
    "AgencyBase",
    # User models
    "User",
    "UserCreate",
    "UserLogin",
    "UserRead",
    "UserRole",
    "UserBase",
    # Task models
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskRead",
    "TaskBase",
    "TaskStatus",
    "TaskPriority",
    # Project models
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectRead",
    "ProjectBase",
    # Time Entry models
    "TimeEntry",
    "TimeEntryCreate",
    "TimeEntryUpdate",
    "TimeEntryRead",
    "TimeEntryBase",
]
