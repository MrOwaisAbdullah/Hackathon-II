"""User models."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import EmailStr, Field as PDField
from sqlalchemy import Enum as SQLEnum
from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, Enum):
    """User roles."""

    admin = "admin"
    member = "member"
    client = "client"


class User(SQLModel, table=True):
    """User database table model."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.member)
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    # Relationships
    assigned_tasks: List["Task"] = Relationship(back_populates="assignee")


# Pydantic schemas for API operations
class UserBase(SQLModel):
    """Base user schema."""

    email: EmailStr
    name: str = PDField(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = PDField(..., min_length=8)
    role: UserRole = PDField(default=UserRole.member)


class UserLogin(SQLModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserRead(UserBase):
    """User read/response schema."""

    id: UUID
    role: UserRole
    agency_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
