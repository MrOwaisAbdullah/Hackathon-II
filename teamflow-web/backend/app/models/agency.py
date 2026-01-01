"""Agency models."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from pydantic import Field as PDField
from sqlmodel import Field, SQLModel


class Agency(SQLModel, table=True):
    """Agency database table model."""

    __tablename__ = "agencies"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    email: EmailStr = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


# Pydantic schemas for API operations
class AgencyBase(SQLModel):
    """Base agency schema."""

    name: str = PDField(..., min_length=1, max_length=100)
    email: EmailStr


class AgencyCreate(AgencyBase):
    """Agency creation schema."""

    pass


class AgencyRead(AgencyBase):
    """Agency read/response schema."""

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
