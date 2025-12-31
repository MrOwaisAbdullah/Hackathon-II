"""User models."""
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """User roles."""

    ADMIN = "admin"
    MEMBER = "member"
    CLIENT = "client"


class User(BaseModel):
    """User model."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    hashed_password: str
    role: UserRole = Field(default=UserRole.MEMBER)
    agency_id: UUID


class UserCreate(BaseModel):
    """User creation model."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.MEMBER)


class UserLogin(BaseModel):
    """User login model."""

    email: EmailStr
    password: str


class UserRead(BaseModel):
    """User read model."""

    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    agency_id: UUID
