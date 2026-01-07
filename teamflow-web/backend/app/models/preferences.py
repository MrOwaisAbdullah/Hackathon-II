"""User chat preference models for Phase 3 AI Chatbot."""
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import Field as PDField
from sqlmodel import Field, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class ChatLanguage(str, Enum):
    """Chat language options."""

    english = "en"
    urdu = "ur"


class UserChatPreference(SQLModel, table=True):
    """User chat preference database table model (T010)."""

    __tablename__ = "user_chat_preferences"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    language: ChatLanguage = Field(default=ChatLanguage.english)
    voice_enabled: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Pydantic schemas for API operations


class UserChatPreferenceBase(SQLModel):
    """Base user chat preference schema."""

    language: ChatLanguage = PDField(default=ChatLanguage.english)
    voice_enabled: bool = PDField(default=False)


class UserChatPreferenceCreate(UserChatPreferenceBase):
    """User chat preference creation schema."""

    pass


class UserChatPreferenceRead(UserChatPreferenceBase):
    """User chat preference read/response schema."""

    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserChatPreferenceUpdate(SQLModel):
    """User chat preference update schema."""

    language: ChatLanguage = None
    voice_enabled: bool = None
