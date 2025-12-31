"""Agency models."""
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


class Agency(BaseModel):
    """Agency model."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class AgencyCreate(BaseModel):
    """Agency creation model."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class AgencyRead(BaseModel):
    """Agency read model."""

    id: UUID
    name: str
    email: EmailStr
