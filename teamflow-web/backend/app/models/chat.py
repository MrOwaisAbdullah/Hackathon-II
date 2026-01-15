"""Chat models for Phase 3 AI Chatbot."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from pydantic import Field as PDField
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class MessageRole(str, Enum):
    """Message role types."""

    user = "user"
    assistant = "assistant"
    system = "system"


class Conversation(SQLModel, table=True):
    """Conversation database table model (T009)."""

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    is_archived: bool = Field(default=False, index=True)

    # External system integration (for ChatKit thread mapping)
    external_id: Optional[str] = Field(default=None, max_length=255, index=True)  # ChatKit thread ID
    external_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """Message database table model (T009)."""

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    role: MessageRole = Field(index=True)
    content: str = Field(..., max_length=65535)  # TEXT type
    tool_calls: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")


# Pydantic schemas for API operations


class ConversationBase(SQLModel):
    """Base conversation schema."""

    title: Optional[str] = PDField(None, max_length=255)


class ConversationCreate(ConversationBase):
    """Conversation creation schema."""

    pass


class ConversationRead(ConversationBase):
    """Conversation read/response schema."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_archived: bool = False

    class Config:
        from_attributes = True


class ConversationUpdate(SQLModel):
    """Conversation update schema."""

    title: Optional[str] = PDField(None, max_length=255)
    is_archived: Optional[bool] = None


class MessageBase(SQLModel):
    """Base message schema."""

    role: MessageRole
    content: str = PDField(..., max_length=65535)


class MessageCreate(MessageBase):
    """Message creation schema."""

    conversation_id: UUID
    tool_calls: Optional[dict] = None


class MessageRead(MessageBase):
    """Message read/response schema."""

    id: UUID
    conversation_id: UUID
    tool_calls: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
