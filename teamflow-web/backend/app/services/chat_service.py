"""Chat service for conversation and message CRUD operations (T011)."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from contextlib import contextmanager

from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.chat import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    Message,
    MessageCreate,
    MessageRole,
)
from app.models.preferences import UserChatPreference, UserChatPreferenceUpdate
from app.models.user import User
from app.db.session import engine


class ChatService:
    """Service for chat operations (conversations, messages, preferences)."""

    @contextmanager
    def _get_session(self):
        """Get a database session for internal use."""
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()

    # Conversation methods

    def create_conversation(
        self,
        user_id: UUID,
        session: Session,
        title: Optional[str] = None,
    ) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    def get_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        session: Session,
    ) -> Optional[Conversation]:
        """Get a conversation by ID (scoped to user)."""
        return session.exec(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.is_archived == False,  # Only return active conversations
            )
        ).first()

    def list_conversations(
        self,
        user_id: UUID,
        session: Session,
        include_archived: bool = False,
        limit: int = 50,
    ) -> List[Conversation]:
        """List all conversations for a user, ordered by updated_at DESC."""
        query = select(Conversation).where(Conversation.user_id == user_id)

        if not include_archived:
            query = query.where(Conversation.is_archived == False)

        return session.exec(
            query.order_by(Conversation.updated_at.desc()).limit(limit)
        ).all()

    def update_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        update_data: ConversationUpdate,
        session: Session,
    ) -> Optional[Conversation]:
        """Update a conversation (title, archived status)."""
        conversation = self.get_conversation(conversation_id, user_id, session)
        if not conversation:
            return None

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(conversation, field, value)

        conversation.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(conversation)
        return conversation

    def archive_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        session: Session,
    ) -> Optional[Conversation]:
        """Archive (soft delete) a conversation."""
        conversation = self.get_conversation(conversation_id, user_id, session)
        if not conversation:
            return None

        conversation.is_archived = True
        conversation.updated_at = datetime.utcnow()
        session.commit()
        return conversation

    # Message methods

    def add_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        role: MessageRole,
        content: str,
        session: Session,
        tool_calls: Optional[dict] = None,
    ) -> Optional[Message]:
        """Add a message to a conversation."""
        # Verify conversation exists and belongs to user
        conversation = self.get_conversation(conversation_id, user_id, session)
        if not conversation:
            return None

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            created_at=datetime.utcnow(),
        )
        session.add(message)

        # Update conversation's updated_at timestamp
        conversation.updated_at = datetime.utcnow()

        session.commit()
        session.refresh(message)
        return message

    def get_messages(
        self,
        conversation_id: UUID,
        user_id: UUID,
        session: Session,
        limit: int = 100,
        before_id: Optional[UUID] = None,
    ) -> List[Message]:
        """Get messages for a conversation with pagination."""
        # Verify conversation exists and belongs to user
        conversation = self.get_conversation(conversation_id, user_id, session)
        if not conversation:
            return []

        query = select(Message).where(Message.conversation_id == conversation_id)

        if before_id:
            # Get messages before a specific message ID (for pagination)
            before_message = session.get(Message, before_id)
            if before_message:
                query = query.where(Message.created_at < before_message.created_at)

        return session.exec(
            query.order_by(Message.created_at.asc()).limit(limit)
        ).all()

    # Preference methods

    def get_user_preferences(
        self,
        user_id: UUID,
        session: Session,
    ) -> Optional[UserChatPreference]:
        """Get chat preferences for a user."""
        return session.get(UserChatPreference, user_id)

    def upsert_user_preferences(
        self,
        user_id: UUID,
        update_data: UserChatPreferenceUpdate,
        session: Session,
    ) -> UserChatPreference:
        """Create or update user chat preferences."""
        preferences = self.get_user_preferences(user_id, session)

        if preferences:
            # Update existing preferences
            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(preferences, field, value)
            preferences.updated_at = datetime.utcnow()
        else:
            # Create new preferences with defaults
            preferences = UserChatPreference(
                user_id=user_id,
                **update_data.model_dump(exclude_unset=True),
            )
            session.add(preferences)

        session.commit()
        session.refresh(preferences)
        return preferences

    # Internal methods (manage their own sessions)

    async def create_conversation_internal(
        self,
        user_id: str | UUID,
        title: Optional[str] = None,
    ) -> Conversation:
        """Create a conversation with internal session management."""
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        with self._get_session() as session:
            return self.create_conversation(user_id, session, title)

    async def get_conversation_internal(
        self,
        conversation_id: str | UUID,
        user_id: str | UUID,
    ) -> Optional[Conversation]:
        """Get a conversation with internal session management."""
        try:
            if isinstance(conversation_id, str):
                # Skip if this is a ChatKit thread ID (not a UUID)
                if conversation_id.startswith("thread_"):
                    return None
                conversation_id = UUID(conversation_id)
            if isinstance(user_id, str):
                user_id = UUID(user_id)

            with self._get_session() as session:
                return self.get_conversation(conversation_id, user_id, session)
        except ValueError:
            # Invalid UUID format (e.g., ChatKit thread ID)
            return None

    async def get_messages_internal(
        self,
        conversation_id: str | UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Message]:
        """Get messages with internal session management."""
        try:
            if isinstance(conversation_id, str):
                # Skip if this is a ChatKit thread ID
                if conversation_id.startswith("thread_"):
                    return []
                conversation_id = UUID(conversation_id)

            with self._get_session() as session:
                return self.get_messages(conversation_id, session, limit, offset)
        except ValueError:
            # Invalid UUID format
            return []

    async def add_message_internal(
        self,
        conversation_id: str | UUID,
        role: str,
        content: str,
    ) -> Optional[Message]:
        """Add a message with internal session management."""
        try:
            if isinstance(conversation_id, str):
                # Skip if this is a ChatKit thread ID
                if conversation_id.startswith("thread_"):
                    return None
                conversation_id = UUID(conversation_id)

            with self._get_session() as session:
                return self.add_message(conversation_id, role, content, session)
        except (ValueError, Exception):
            # Invalid UUID or other error - return None
            return None


# Singleton instance for dependency injection
chat_service = ChatService()
