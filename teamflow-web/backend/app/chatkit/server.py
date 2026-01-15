"""TeamFlow ChatKit Server implementation.

This module provides a custom ChatKit server that integrates:
- OpenAI ChatKit server protocol
- AgentOrchestrator for AI responses
- RAG service for knowledge base queries
- Custom authentication via Better Auth
- File storage for attachments

The server handles:
1. Incoming chat requests from ChatKit frontend
2. Streaming responses via SSE
3. Tool execution (MCP tools)
4. Client tool calls (frontend actions)
5. Widget rendering for rich UI
"""
import asyncio
import json
from typing import AsyncIterator, Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from agents import Agent, Runner, RunContextWrapper, ItemHelpers
from chatkit.server import (
    ChatKitServer,
    ErrorEvent,
    Store,
    StreamingResult,
    ThreadMetadata,
    ThreadStreamEvent,
    UserMessageItem,
    ClientToolCallItem,
)
from chatkit.types import (
    AssistantMessageContent,
    AssistantMessageItem,
    ThreadItemDoneEvent,
)
from chatkit.agents import (
    AgentContext,
    simple_to_agent_input,
    stream_agent_response,
)
from chatkit.store import Store as StoreClass, Page, ThreadItem

from app.agents.chatbot import create_chatbot_agent_context
from app.agents.orchestrator import AgentOrchestrator
from app.core.config import settings
from app.core.logging import get_logger
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app.models.chat import Conversation, Message
from sqlmodel import select

logger = get_logger(__name__)


@dataclass
class _ThreadState:
    """Internal state for a thread in MemoryStore."""
    thread: ThreadMetadata
    items: List[ThreadItem] = field(default_factory=list)


class MemoryStore(StoreClass[dict]):
    """In-memory store for ChatKit threads and items with undo support (G1).

    Simple thread-safe implementation using dictionaries.
    Non-persistent - data is lost on restart.

    G1 - Specification Analysis Finding: Added undo functionality for deletions.
    Items can be restored within 5 minutes of deletion via undo_delete_thread_item().
    """

    def __init__(self) -> None:
        self._threads: Dict[str, _ThreadState] = {}
        self._items_map: Dict[str, ThreadItem] = {}
        self._undo_stack: Dict[str, List[ThreadItem]] = {}  # thread_id -> list of deleted items
        self._undo_timestamps: Dict[str, datetime] = {}  # item_id -> deletion timestamp

    async def save_thread(
        self,
        thread: ThreadMetadata,
        context: dict,
    ) -> None:
        """Save or update thread metadata."""
        state = self._threads.get(thread.id)
        if state:
            state.thread = thread.model_copy(deep=True)
        else:
            self._threads[thread.id] = _ThreadState(
                thread=thread.model_copy(deep=True),
                items=[],
            )

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Add an item to a thread.

        CRITICAL: Replace __fake_id__ with a real unique ID to prevent overwrites.
        The ChatKit framework uses __fake_id__ during streaming, but we need real IDs for persistence.
        """
        import uuid
        import logging
        logger = logging.getLogger(__name__)

        original_id = item.id
        item_type = type(item).__name__

        logger.info(f"[add_thread_item] thread={thread_id}, original_id={original_id}, type={item_type}")

        state = self._threads.get(thread_id)
        if not state:
            # Thread doesn't exist yet, create it
            state = _ThreadState(thread=ThreadMetadata(
                id=thread_id,
                title="New Chat",
                created_at=datetime.utcnow(),
                metadata={},
            ), items=[])
            self._threads[thread_id] = state
            logger.info(f"[add_thread_item] Created new thread {thread_id}")

        # CRITICAL FIX: Replace __fake_id__ with a real unique ID
        # Each message must have a unique ID or they will overwrite each other
        if item.id == "__fake_id__":
            # Generate a real unique ID for this message
            new_id = f"{item.type}_{uuid.uuid4().hex[:16]}"
            item = item.model_copy(update={"id": new_id})
            logger.info(f"[add_thread_item] Replaced __fake_id__ with {new_id}")

        # Check if we're overwriting an existing item
        existing = self._items_map.get(item.id)
        if existing:
            logger.warning(f"[add_thread_item] ⚠️ OVERWRITING existing item {item.id}!")

        state.items.append(item)
        self._items_map[item.id] = item
        logger.info(f"[add_thread_item] Added item {item.id}, thread now has {len(state.items)} items")

    async def save_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Save an item (for updates).

        Called by ThreadItemReplacedEvent to replace an existing item.
        CRITICAL: thread_id is passed as the first parameter (ChatKit Store interface).
        """
        import logging
        logger = logging.getLogger(__name__)

        item_type = type(item).__name__
        logger.info(f"[save_item] thread={thread_id}, item_id={item.id}, type={item_type}")

        state = self._threads.get(thread_id)
        if state:
            logger.info(f"[save_item] Thread has {len(state.items)} items")

            # Find and update the item with matching ID in this thread
            for i, existing_item in enumerate(state.items):
                if existing_item.id == item.id:
                    logger.warning(f"[save_item] ⚠️ UPDATING existing item at index {i}: {existing_item.id}")
                    state.items[i] = item
                    self._items_map[item.id] = item
                    return

            # Item not found in thread, add it
            logger.info(f"[save_item] Item {item.id} not found in thread, appending")
            state.items.append(item)
            self._items_map[item.id] = item
            return

        # Thread not found, just add to map
        logger.warning(f"[save_item] Thread {thread_id} not found, adding to map")
        self._items_map[item.id] = item

    async def load_thread(
        self,
        thread_id: str,
        context: dict,
    ) -> ThreadMetadata | None:
        """Load thread metadata by ID, creating it if it doesn't exist."""
        state = self._threads.get(thread_id)

        if state:
            return state.thread

        # Auto-create thread if it doesn't exist (for ChatKit SDK compatibility)
        # This handles the case where the frontend references a thread_id
        # that hasn't been explicitly created yet
        from chatkit.server import ThreadMetadata

        new_thread = ThreadMetadata(
            id=thread_id,
            title="New Chat",
            created_at=datetime.utcnow(),
            metadata={
                "user_id": str(context.get("user_id", "unknown")) if context else "unknown",
            },
        )

        # Save to store
        await self.save_thread(new_thread, context or {})

        return new_thread

    async def load_threads(
        self,
        context: dict,
        limit: int = 100,
        after: str | None = None,
        order: str = "desc",
    ) -> Page[ThreadMetadata]:
        """Load all threads with pagination support."""
        threads = [state.thread for state in list(self._threads.values())]

        # Sort by created_at
        threads.sort(
            key=lambda t: getattr(t, "created_at", datetime.utcnow()),
            reverse=(order == "desc"),
        )

        # Handle pagination
        start = 0
        if after:
            index_map = {thread.id: idx for idx, thread in enumerate(threads)}
            start = index_map.get(after, -1) + 1

        slice_threads = threads[start : start + limit + 1]
        has_more = len(slice_threads) > limit
        return Page(
            data=slice_threads[:limit],
            has_more=has_more,
            after=slice_threads[-1].id if has_more else None,
        )

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict,
    ) -> Page[ThreadItem]:
        """Load thread items with pagination."""
        items = [item.model_copy(deep=True) for item in self._items(thread_id)]
        items.sort(
            key=lambda i: getattr(i, "created_at", datetime.utcnow()),
            reverse=(order == "desc"),
        )

        start = 0
        if after:
            index_map = {item.id: idx for idx, item in enumerate(items)}
            start = index_map.get(after, -1) + 1

        slice_items = items[start : start + limit + 1]
        has_more = len(slice_items) > limit
        return Page(
            data=slice_items[:limit],
            has_more=has_more,
            after=slice_items[-1].id if has_more else None,
        )

    async def load_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> ThreadItem | None:
        """Load an item by ID.

        CRITICAL: thread_id is passed as the first parameter (ChatKit Store interface).
        """
        return self._items_map.get(item_id)

    async def delete_thread(
        self,
        thread_id: str,
        context: dict,
    ) -> None:
        """Delete a thread."""
        if thread_id in self._threads:
            del self._threads[thread_id]

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> None:
        """Delete an item from a thread with undo support (G1).

        Stores deleted items for 5 minutes to allow undo.
        """
        import logging
        logger = logging.getLogger(__name__)

        state = self._threads.get(thread_id)
        if state:
            # Find the item
            for i, item in enumerate(state.items):
                if item.id == item_id:
                    # Store for undo before deleting
                    if thread_id not in self._undo_stack:
                        self._undo_stack[thread_id] = []

                    # Store with timestamp
                    self._undo_stack[thread_id].append(item)
                    self._undo_timestamps[item_id] = datetime.utcnow()

                    # Delete
                    state.items.pop(i)
                    if item_id in self._items_map:
                        del self._items_map[item_id]

                    logger.info(f"Deleted item {item_id} (undo available for 5 minutes)")
                    return

    async def undo_delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> bool:
        """Undo deletion if within 5-minute window (G1 - Specification Analysis Finding).

        Args:
            thread_id: Thread containing the deleted item
            item_id: ID of the item to restore
            context: Request context (for logging/authorization)

        Returns:
            True if item was restored, False if undo not available
        """
        import logging
        logger = logging.getLogger(__name__)

        # Check if item was deleted within 5 minutes
        deleted_at = self._undo_timestamps.get(item_id)
        if not deleted_at:
            logger.info(f"Undo not available for item {item_id} (not in deletion history)")
            return False

        if (datetime.utcnow() - deleted_at).total_seconds() > 300:  # 5 minutes
            logger.warning(f"Undo window expired for item {item_id}")
            # Clean up expired entries
            if thread_id in self._undo_stack:
                self._undo_stack[thread_id] = [
                    item for item in self._undo_stack[thread_id]
                    if item.id != item_id
                ]
            if item_id in self._undo_timestamps:
                del self._undo_timestamps[item_id]
            return False

        # Restore from undo stack
        if thread_id in self._undo_stack:
            for item in self._undo_stack[thread_id]:
                if item.id == item_id:
                    state = self._threads.get(thread_id)
                    if state:
                        state.items.append(item)
                        self._items_map[item_id] = item

                        # Remove from undo stack
                        self._undo_stack[thread_id].remove(item)
                        del self._undo_timestamps[item_id]

                        logger.info(f"Restored item {item_id} via undo")
                        return True

        logger.info(f"Undo not available for item {item_id} (not found in undo stack)")
        return False

    async def save_attachment(
        self,
        attachment,
        context: dict,
    ) -> None:
        """Save an attachment (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    async def load_attachment(
        self,
        attachment_id: str,
        context: dict,
    ):
        """Load an attachment (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    async def delete_attachment(
        self,
        attachment_id: str,
        context: dict,
    ) -> None:
        """Delete an attachment (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    def generate_item_id(self, item_type: str, thread: ThreadMetadata, context) -> str:
        """Generate a unique item ID."""
        import uuid
        return f"{item_type}_{uuid.uuid4().hex[:16]}"

    def generate_thread_id(self, context) -> str:
        """Generate a unique thread ID."""
        import uuid
        return f"thread_{uuid.uuid4().hex[:16]}"

    def _items(self, thread_id: str) -> List[ThreadItem]:
        """Get all items for a thread."""
        state = self._threads.get(thread_id)
        return state.items if state else []


class DatabaseStore(StoreClass[dict]):
    """Database-backed store for ChatKit threads and items.

    Persists conversations and messages to PostgreSQL via ChatService.
    This provides true persistence across server restarts.

    Thread ID Mapping:
    - ChatKit thread IDs (e.g., "thread_abc123") are mapped to database Conversation IDs
    - The mapping is stored in thread metadata
    - On load_thread, we look up the conversation by external_id
    """

    def __init__(self, chat_service: ChatService):
        """Initialize the database store.

        Args:
            chat_service: ChatService instance for database operations
        """
        from app.db.session import Session
        self._chat_service = chat_service
        self._session_factory = Session
        self._thread_id_cache: Dict[str, UUID] = {}  # thread_id -> conversation_id cache

    async def save_thread(
        self,
        thread: ThreadMetadata,
        context: dict,
    ) -> None:
        """Save or update thread metadata to database."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            user_id_str = context.get("user_id")
            if not user_id_str:
                logger.warning("[DatabaseStore.save_thread] No user_id in context")
                return

            from uuid import UUID
            user_id = UUID(user_id_str)

            with self._session_factory() as session:
                # Check if conversation exists for this thread
                conversation = session.exec(
                    select(Conversation).where(
                        Conversation.external_id == thread.id,
                        Conversation.user_id == user_id,
                    )
                ).first()

                if conversation:
                    # Update existing conversation
                    conversation.title = thread.title or "New Chat"
                    conversation.updated_at = datetime.utcnow()
                    # Store metadata in external_metadata
                    if thread.metadata:
                        import json
                        conversation.external_metadata = thread.metadata
                    session.commit()
                    logger.info(f"[DatabaseStore.save_thread] Updated conversation {conversation.id} for thread {thread.id}")
                else:
                    # Create new conversation
                    # Conversation is already imported at module level
                    conversation = Conversation(
                        user_id=user_id,
                        title=thread.title or "New Chat",
                        external_id=thread.id,
                        external_metadata=thread.metadata or {},
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(conversation)
                    session.commit()
                    logger.info(f"[DatabaseStore.save_thread] Created conversation {conversation.id} for thread {thread.id}")

                # Cache the mapping
                self._thread_id_cache[thread.id] = conversation.id

        except Exception as e:
            logger.error(f"[DatabaseStore.save_thread] Error: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Add an item to a thread (persist to database)."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            user_id_str = context.get("user_id")
            if not user_id_str:
                logger.warning("[DatabaseStore.add_thread_item] No user_id in context")
                return

            from uuid import UUID
            user_id = UUID(user_id_str)

            # Get conversation ID for this thread
            conversation_id = self._thread_id_cache.get(thread_id)
            if not conversation_id:
                # Look up in database
                with self._session_factory() as session:
                    conversation = session.exec(
                        select(Conversation).where(
                            Conversation.external_id == thread_id,
                            Conversation.user_id == user_id,
                        )
                    ).first()
                    if conversation:
                        conversation_id = conversation.id
                        self._thread_id_cache[thread_id] = conversation_id
                    else:
                        logger.warning(f"[DatabaseStore.add_thread_item] No conversation found for thread {thread_id}")
                        return

            # Import MessageRole
            from app.models.chat import Message, MessageRole

            # Determine role based on item type
            if item.type == "user_message":
                role = MessageRole.USER
                # Extract content from UserMessageItem
                content = ""
                if hasattr(item, 'content') and item.content:
                    content_str = str(item.content)
                    # Handle both string and list content
                    if content_str.startswith('[') and '"type":' in content_str:
                        # It's a list of content parts
                        import json
                        try:
                            parts = json.loads(content_str)
                            for part in parts:
                                if part.get('type') == 'input_text':
                                    content = part.get('text', '')
                                    break
                        except:
                            content = content_str
                    else:
                        content = content_str
            elif item.type == "assistant_message":
                role = MessageRole.ASSISTANT
                # Extract content from AssistantMessageItem
                content = ""
                if hasattr(item, 'content') and item.content:
                    content_list = item.content if isinstance(item.content, list) else [item.content]
                    for part in content_list:
                        if hasattr(part, 'type') and part.type == "output_text":
                            content = getattr(part, 'text', '')
                            break
                        elif isinstance(part, str):
                            content += part
            elif item.type == "client_tool_call":
                role = MessageRole.USER  # Tool calls from client are treated as user messages
                content = f"[Tool Call: {getattr(item, 'name', 'unknown')}]"
            else:
                logger.warning(f"[DatabaseStore.add_thread_item] Unknown item type: {item.type}")
                return

            if not content:
                logger.warning(f"[DatabaseStore.add_thread_item] No content extracted from item {item.id}")
                return

            # Save message to database
            with self._session_factory() as session:
                message = Message(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    created_at=datetime.utcnow(),
                )
                session.add(message)

                # Update conversation's updated_at
                conversation = session.get(Conversation, conversation_id)
                if conversation:
                    conversation.updated_at = datetime.utcnow()

                session.commit()
                logger.info(f"[DatabaseStore.add_thread_item] Saved message {message.id} for thread {thread_id}, role={role}")

        except Exception as e:
            logger.error(f"[DatabaseStore.add_thread_item] Error: {e}")
            import traceback
            logger.error(traceback.format_exc())

    async def save_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Save an item (for updates) - currently not supported for database store."""
        # ChatKit uses this to update items during streaming
        # For database store, we only save the final version in add_thread_item
        pass

    async def load_thread(
        self,
        thread_id: str,
        context: dict,
    ) -> ThreadMetadata | None:
        """Load thread metadata by ID from database."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            user_id_str = context.get("user_id")
            if not user_id_str:
                logger.warning("[DatabaseStore.load_thread] No user_id in context")
                return None

            from uuid import UUID
            user_id = UUID(user_id_str)

            with self._session_factory() as session:
                conversation = session.exec(
                    select(Conversation).where(
                        Conversation.external_id == thread_id,
                        Conversation.user_id == user_id,
                    )
                ).first()

                if conversation:
                    # Cache the mapping
                    self._thread_id_cache[thread_id] = conversation.id

                    return ThreadMetadata(
                        id=thread_id,
                        title=conversation.title or "New Chat",
                        created_at=conversation.created_at,
                        metadata=conversation.external_metadata or {},
                    )
                else:
                    logger.info(f"[DatabaseStore.load_thread] No conversation found for thread {thread_id}")
                    return None

        except Exception as e:
            logger.error(f"[DatabaseStore.load_thread] Error: {e}")
            return None

    async def load_threads(
        self,
        context: dict,
        limit: int = 100,
        after: str | None = None,
        order: str = "desc",
    ) -> Page[ThreadMetadata]:
        """Load all threads with pagination from database."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            user_id_str = context.get("user_id")
            if not user_id_str:
                logger.warning("[DatabaseStore.load_threads] No user_id in context")
                return Page(data=[], has_more=False, after=None)

            from uuid import UUID
            user_id = UUID(user_id_str)

            with self._session_factory() as session:
                query = select(Conversation).where(
                    Conversation.user_id == user_id,
                    Conversation.is_archived == False,
                )

                # Sort by updated_at
                if order == "desc":
                    query = query.order_by(Conversation.updated_at.desc())
                else:
                    query = query.order_by(Conversation.updated_at.asc())

                conversations = session.exec(query.limit(limit + 1)).all()

                has_more = len(conversations) > limit
                slice_conversations = conversations[:limit]

                threads = []
                for conv in slice_conversations:
                    if conv.external_id:
                        self._thread_id_cache[conv.external_id] = conv.id
                        threads.append(ThreadMetadata(
                            id=conv.external_id,
                            title=conv.title or "New Chat",
                            created_at=conv.created_at,
                            metadata=conv.external_metadata or {},
                        ))

                return Page(
                    data=threads,
                    has_more=has_more,
                    after=threads[-1].id if has_more else None,
                )

        except Exception as e:
            logger.error(f"[DatabaseStore.load_threads] Error: {e}")
            return Page(data=[], has_more=False, after=None)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict,
    ) -> Page[ThreadItem]:
        """Load thread items with pagination from database.

        Note: This converts database messages to ChatKit ThreadItem format.
        This is lossy - some ChatKit-specific data may not be preserved.
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            user_id_str = context.get("user_id")
            if not user_id_str:
                logger.warning("[DatabaseStore.load_thread_items] No user_id in context")
                return Page(data=[], has_more=False, after=None)

            from uuid import UUID
            user_id = UUID(user_id_str)

            # Get conversation ID
            conversation_id = self._thread_id_cache.get(thread_id)
            if not conversation_id:
                with self._session_factory() as session:
                    conversation = session.exec(
                        select(Conversation).where(
                            Conversation.external_id == thread_id,
                            Conversation.user_id == user_id,
                        )
                    ).first()
                    if conversation:
                        conversation_id = conversation.id
                        self._thread_id_cache[thread_id] = conversation_id
                    else:
                        logger.info(f"[DatabaseStore.load_thread_items] No conversation found for thread {thread_id}")
                        return Page(data=[], has_more=False, after=None)

            # Load messages from database
            with self._session_factory() as session:
                query = select(Message).where(
                    Message.conversation_id == conversation_id,
                )

                # Sort by created_at
                if order == "desc":
                    query = query.order_by(Message.created_at.desc())
                else:
                    query = query.order_by(Message.created_at.asc())

                messages = session.exec(query.limit(limit + 1)).all()

                has_more = len(messages) > limit
                slice_messages = messages[:limit]

                # Convert messages to ThreadItem format
                from chatkit.types import UserMessageItem, UserMessageContent, AssistantMessageItem, AssistantMessageContent

                items = []
                for msg in slice_messages:
                    if msg.role == MessageRole.USER:
                        # Create UserMessageItem
                        item = UserMessageItem(
                            id=f"user_msg_{msg.id}",
                            thread_id=thread_id,
                            created_at=msg.created_at,
                            content=[UserMessageContent(type="input_text", text=msg.content)],
                        )
                    elif msg.role == MessageRole.ASSISTANT:
                        # Create AssistantMessageItem
                        item = AssistantMessageItem(
                            id=f"assistant_msg_{msg.id}",
                            thread_id=thread_id,
                            created_at=msg.created_at,
                            content=[AssistantMessageContent(type="output_text", text=msg.content)],
                        )
                    else:
                        # Skip system messages
                        continue

                    items.append(item)

                return Page(
                    data=items,
                    has_more=has_more,
                    after=items[-1].id if has_more else None,
                )

        except Exception as e:
            logger.error(f"[DatabaseStore.load_thread_items] Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return Page(data=[], has_more=False, after=None)

    async def load_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> ThreadItem | None:
        """Load an item by ID from database."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Parse item_id to extract message UUID
            # Format: "user_msg_{uuid}" or "assistant_msg_{uuid}"
            if item_id.startswith("user_msg_"):
                msg_uuid = UUID(item_id.replace("user_msg_", ""))
            elif item_id.startswith("assistant_msg_"):
                msg_uuid = UUID(item_id.replace("assistant_msg_", ""))
            else:
                logger.warning(f"[DatabaseStore.load_item] Unknown item ID format: {item_id}")
                return None

            # Get conversation ID for this thread
            conversation_id = self._thread_id_cache.get(thread_id)
            if not conversation_id:
                user_id_str = context.get("user_id")
                if not user_id_str:
                    return None
                from uuid import UUID
                user_id = UUID(user_id_str)

                with self._session_factory() as session:
                    conversation = session.exec(
                        select(Conversation).where(
                            Conversation.external_id == thread_id,
                            Conversation.user_id == user_id,
                        )
                    ).first()
                    if conversation:
                        conversation_id = conversation.id
                        self._thread_id_cache[thread_id] = conversation_id
                    else:
                        return None

            # Load message from database
            with self._session_factory() as session:
                message = session.get(Message, msg_uuid)
                if not message or message.conversation_id != conversation_id:
                    return None

                # Convert to ThreadItem
                from chatkit.types import UserMessageItem, UserMessageContent, AssistantMessageItem, AssistantMessageContent

                if message.role == MessageRole.USER:
                    return UserMessageItem(
                        id=item_id,
                        thread_id=thread_id,
                        created_at=message.created_at,
                        content=[UserMessageContent(type="input_text", text=message.content)],
                    )
                elif message.role == MessageRole.ASSISTANT:
                    return AssistantMessageItem(
                        id=item_id,
                        thread_id=thread_id,
                        created_at=message.created_at,
                        content=[AssistantMessageContent(type="output_text", text=message.content)],
                    )

        except Exception as e:
            logger.error(f"[DatabaseStore.load_item] Error: {e}")

        return None

    async def delete_thread(
        self,
        thread_id: str,
        context: dict,
    ) -> None:
        """Delete (archive) a thread."""
        import logging
        logger = logging.getLogger(__name__)

        try:
            user_id_str = context.get("user_id")
            if not user_id_str:
                return

            from uuid import UUID
            user_id = UUID(user_id_str)

            with self._session_factory() as session:
                conversation = session.exec(
                    select(Conversation).where(
                        Conversation.external_id == thread_id,
                        Conversation.user_id == user_id,
                    )
                ).first()

                if conversation:
                    # Soft delete (archive)
                    conversation.is_archived = True
                    conversation.updated_at = datetime.utcnow()
                    session.commit()
                    logger.info(f"[DatabaseStore.delete_thread] Archived conversation for thread {thread_id}")

                    # Clear from cache
                    if thread_id in self._thread_id_cache:
                        del self._thread_id_cache[thread_id]

        except Exception as e:
            logger.error(f"[DatabaseStore.delete_thread] Error: {e}")

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> None:
        """Delete an item from a thread (not implemented for database store)."""
        # Message deletion is complex with foreign keys
        # For now, we don't support individual message deletion
        pass

    async def undo_delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: dict,
    ) -> bool:
        """Undo deletion (not implemented for database store)."""
        return False

    async def save_attachment(self, attachment, context: dict) -> None:
        """Save an attachment (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    async def load_attachment(self, attachment_id: str, context: dict):
        """Load an attachment (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        """Delete an attachment (not implemented)."""
        raise NotImplementedError("Attachments not supported")

    def generate_item_id(self, item_type: str, thread: ThreadMetadata, context) -> str:
        """Generate a unique item ID."""
        import uuid
        return f"{item_type}_{uuid.uuid4().hex[:16]}"

    def generate_thread_id(self, context) -> str:
        """Generate a unique thread ID."""
        import uuid
        return f"thread_{uuid.uuid4().hex[:16]}"


class TeamFlowChatKitServer(ChatKitServer):
    """
    TeamFlow's custom ChatKit server implementation.

    This server:
    - Integrates with AgentOrchestrator for AI responses
    - Supports RAG knowledge base queries
    - Handles MCP tool execution
    - Manages client tool calls (frontend actions)
    - Streams responses via SSE

    Usage:
        server = TeamFlowChatKitServer(data_store, file_store)
        result = await server.process(request_body, context)
    """

    def __init__(
        self,
        data_store: Store,
        chat_service: Optional[ChatService] = None,
        rag_service: Optional[RAGService] = None,
        enable_rag: bool = True,
    ):
        """Initialize the TeamFlow ChatKit server.

        Args:
            data_store: ChatKit store for thread/message persistence
            chat_service: Optional ChatService for database operations
            rag_service: Optional RAGService for knowledge base
            enable_rag: Whether to enable RAG by default
        """
        super().__init__(data_store)

        self.chat_service = chat_service
        self.rag_service = rag_service
        self.enable_rag = enable_rag
        self.orchestrator: Optional[AgentOrchestrator] = None

        # Initialize orchestrator if chat_service is available
        if self.chat_service:
            self.orchestrator = AgentOrchestrator(
                chat_service=self.chat_service,
                model="google/gemini-2.0-flash-exp:free",
            )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallItem,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Handle incoming user messages and client tool outputs.

        This method processes the user message through the agent and streams
        the response using ChatKit's streaming helpers.

        CRITICAL: Follow the official OpenAI Agents SDK streaming pattern:
        - The ChatKitServer base class ALREADY handles user message persistence
        - The ChatKitServer base class ALREADY calls respond() with proper input
        - Use Runner.run_streamed() and iterate through result.stream_events()
        - Convert events to ChatKit ThreadItemAddedEvent for frontend

        Args:
            thread: ChatKit thread metadata
            input: User message or client tool output
            context: Request context (user_id, session, etc.)

        Yields:
            ThreadStreamEvent objects for ChatKit
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Load recent thread history for context
            # NOTE: The user message is already persisted by ChatKitServer base class
            items_page = await self.store.load_thread_items(
                thread.id,
                after=None,
                limit=20,
                order="asc",
                context=context or {},
            )

            logger.info(f"[ChatKit respond] Thread {thread.id}, Loaded {len(items_page.data)} items")

            # Convert thread items to agent input format
            input_items = await simple_to_agent_input(items_page.data)

            # Create agent context
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context or {}
            )

            # CRITICAL FIX: Generate unique message ID upfront to prevent overwriting
            import uuid
            unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"
            logger.info(f"[ChatKit respond] Generated unique message ID: {unique_message_id}")

            # Try primary model first, fall back to OpenAI on 429 rate limit
            primary_model = "google/gemini-2.0-flash-exp:free"
            fallback_model = "google/gemini-2.0-flash-exp:free"  # OpenRouter fallback

            # Check if we have OpenAI API key for direct fallback
            use_openai_direct = bool(settings.openai_api_key)
            if use_openai_direct:
                fallback_model = "gpt-5-nano-2025-08-07"  # Direct OpenAI API fallback

            last_error = None

            # Try primary model
            for attempt, model_to_use in enumerate([primary_model, fallback_model] if settings.openai_api_key else [primary_model]):
                try:
                    logger.info(f"[ChatKit respond] Attempt {attempt + 1}/{len([primary_model, fallback_model] if settings.openai_api_key else [primary_model])} using model: {model_to_use}")

                    # CRITICAL: Determine MCP server URL for current environment
                    # In production (HuggingFace Spaces), the MCP server is on the SAME port as backend
                    import os
                    is_production = os.getenv("SPACE_ID") is not None or os.getenv("HUGGINGFACE_SPACE_ID") is not None

                    if is_production:
                        # In production, MCP server is mounted on the backend's port
                        # Detect the actual port from environment or use localhost with current port
                        port = os.getenv("PORT", "7860")  # HuggingFace Spaces uses PORT env var
                        mcp_url = f"http://localhost:{port}/mcp"
                    else:
                        mcp_url = settings.mcp_server_url

                    logger.info(f"[ChatKit respond] MCP server URL: {mcp_url} (production={is_production})")

                    # Run the agent with context manager for MCP server lifecycle
                    logger.info(f"[ChatKit respond] Entering create_chatbot_agent_context...")
                    async with create_chatbot_agent_context(
                        model=model_to_use,
                        mcp_server_url=mcp_url,
                    ) as agent_to_use:
                        logger.info(f"[ChatKit respond] Agent context created successfully!")
                        logger.info(f"[ChatKit respond] About to run agent...")
                        logger.info(f"[ChatKit respond] input_items count: {len(input_items) if input_items else 0}")

                        # CRITICAL: Use Runner.run_streamed() for streaming responses
                        # Then iterate through result.stream_events() to get events
                        # IMPORTANT: Runner.run_streamed() is SYNCHRONOUS - do NOT await
                        result = Runner.run_streamed(
                            agent_to_use,
                            input_items,  # Pass conversation history
                            context=agent_context
                        )
                        logger.info(f"[ChatKit respond] Agent execution started, result type: {type(result).__name__}")

                        # CRITICAL FIX: Collect all events FIRST, then yield them
                        # This prevents async context issues when yielding across task boundaries
                        events_to_yield = []
                        event_types_seen = set()
                        event_count = 0
                        message_started = False

                        logger.info(f"[ChatKit respond] Starting to collect events...")

                        async for event in result.stream_events():
                            event_count += 1
                            event_type = event.type
                            event_types_seen.add(event_type)

                            logger.info(f"[ChatKit respond] Event #{event_count}: {event_type}")

                            if event.type == "run_item_stream_event" and event.item.type == "message_output_item":
                                message_text = ItemHelpers.text_message_output(event.item)
                                logger.info(f"[ChatKit respond] Message output: '{message_text[:100] if message_text else 'None'}...'")

                                # Create ChatKit event with required fields
                                from chatkit.types import AssistantMessageItem, AssistantMessageContent
                                from chatkit.server import ThreadItemAddedEvent

                                assistant_item = AssistantMessageItem(
                                    id=unique_message_id,
                                    thread_id=thread.id,
                                    created_at=datetime.now(timezone.utc),
                                    content=[AssistantMessageContent(type="output_text", text=message_text)],
                                )

                                events_to_yield.append(ThreadItemAddedEvent(item=assistant_item))
                                message_started = True

                        logger.info(f"[ChatKit respond] Collected {event_count} events, now yielding {len(events_to_yield)} ChatKit events")

                        # Now yield all collected events (still in async context)
                        for event in events_to_yield:
                            yield event

                        if event_count == 0 or not message_started:
                            logger.warning(f"[ChatKit respond] ⚠️ No message event yielded (events={event_count}, started={message_started})")
                            # Check if result has final_output as fallback
                            if hasattr(result, 'final_output') and result.final_output:
                                logger.info(f"[ChatKit respond] Using final_output as fallback: '{result.final_output[:100]}...'")
                                # Add fallback event to the list with required fields
                                from chatkit.types import AssistantMessageItem, AssistantMessageContent
                                from chatkit.server import ThreadItemAddedEvent

                                assistant_item = AssistantMessageItem(
                                    id=unique_message_id,
                                    thread_id=thread.id,
                                    created_at=datetime.now(timezone.utc),
                                    content=[AssistantMessageContent(type="output_text", text=result.final_output)],
                                )
                                yield ThreadItemAddedEvent(item=assistant_item)

                        # If we got here, success! Break out of retry loop
                        logger.info(f"[ChatKit respond] ✓ Successfully completed with model: {model_to_use}")
                        break

                except Exception as e:
                    last_error = e
                    error_str = str(e)

                    # CRITICAL: Log detailed exception info
                    logger.error(f"[ChatKit respond] ❌ Exception in attempt {attempt + 1}/{len([primary_model, fallback_model] if settings.openai_api_key else [primary_model])}")
                    logger.error(f"[ChatKit respond] Exception type: {type(e).__name__}")
                    logger.error(f"[ChatKit respond] Exception message: {error_str}")
                    import traceback
                    logger.error(f"[ChatKit respond] Traceback:\n{traceback.format_exc()}")

                    # Check if this is a rate limit error (429)
                    is_rate_limit = (
                        "429" in error_str or
                        "rate.limited" in error_str.lower() or
                        "RateLimitError" in type(e).__name__ or
                        "too many requests" in error_str.lower()
                    )

                    # Check if this is a connection error (MCP server)
                    is_connection_error = (
                        "ConnectError" in type(e).__name__ or
                        "Connection" in type(e).__name__ or
                        "connect" in error_str.lower() or
                        "refused" in error_str.lower() or
                        "timeout" in error_str.lower()
                    )

                    if is_connection_error:
                        logger.error(f"[ChatKit respond] 🔗 MCP Server connection error detected!")
                        logger.error(f"[ChatKit respond] The MCP server may not be running at the configured URL.")
                        logger.error(f"[ChatKit respond] Check that the backend server is running and the /mcp endpoint is accessible.")

                    if is_rate_limit and attempt < 1:  # Only retry if we have fallback attempts left
                        logger.warning(f"[ChatKit respond] ⚠️ Rate limit detected with {model_to_use}, retrying with fallback: {fallback_model}")
                        continue
                    else:
                        # Not a rate limit error, or no more retries - raise
                        raise

        except Exception as e:
            # Log error
            logger.error(f"Error in respond: {type(e).__name__}: {str(e)}")

            # Yield error event
            yield ErrorEvent(
                error_code=type(e).__name__,
                message=str(e)
            )

    async def action(
        self,
        thread: ThreadMetadata,
        action_name: str,
        payload: dict,
        context: Any,
    ) -> AsyncIterator:
        """
        Handle client-side actions (button clicks, form submissions, etc.).

        Args:
            thread: ChatKit thread metadata
            action_name: Name of the action
            payload: Action payload (form values, etc.)
            context: Request context

        Yields:
            ChatKit events from action processing
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Handle feedback actions (T065 - Acceptance tracking)
            # ChatKit SDK sends "feedback" action with thumbs up/down
            if action_name == "feedback":
                feedback_type = payload.get("feedback")  # "thumbs_up" or "thumbs_down"
                item_id = payload.get("item_id")

                logger.info(
                    f"Feedback received: {feedback_type} for item {item_id}"
                )

                # Map feedback to recommendation acceptance
                # thumbs_up -> accepted, thumbs_down -> rejected
                action = "accepted" if feedback_type == "thumbs_up" else "rejected"

                # Try to extract recommendation details from the thread item
                try:
                    item = await self.store.load_item(item_id, context or {})
                    if item and hasattr(item, 'content'):
                        # Parse content to extract recommendation details
                        content_str = str(item.content)

                        # Simple heuristic to detect recommendation type
                        recommendation_type = "unknown"
                        if "assignee" in content_str.lower():
                            recommendation_type = "assignee"
                        elif "task" in content_str.lower():
                            recommendation_type = "task_creation"

                        # Track the recommendation acceptance via backend endpoint (T066)
                        await self._track_recommendation_acceptance(
                            recommendation_type=recommendation_type,
                            recommendation_id=item_id,
                            action=action,
                            reasoning=content_str[:500],  # First 500 chars
                            context={"thread_id": thread.id},
                            user_id=context.get("user_id") if context else None,
                        )

                except Exception as e:
                    logger.error(f"Error loading item for feedback: {str(e)}")

                # Stream a confirmation response
                async for event in self._stream_agent_response_simple(
                    f"Thanks for your feedback! ({action})",
                    thread,
                    context
                ):
                    yield event

            # Example: Handle "add_to_todo" action
            elif action_name == "add_to_todo":
                item = payload.get("item")
                if item:
                    # Stream a response confirming the action
                    async for event in self._stream_agent_response_simple(
                        f"Added '{item}' to todo list",
                        thread,
                        context
                    ):
                        yield event

            # Add more action handlers as needed

        except Exception as e:
            # Yield error event using ChatKit SDK ErrorEvent
            yield ErrorEvent(
                error_code=type(e).__name__,
                message=str(e)
            )

    async def _track_recommendation_acceptance(
        self,
        recommendation_type: str,
        recommendation_id: str,
        action: str,
        reasoning: str,
        context: dict,
        user_id: str = None,
    ):
        """Track recommendation acceptance via backend endpoint (T066).

        Args:
            recommendation_type: Type of recommendation (assignee, task_creation, etc.)
            recommendation_id: Unique identifier
            action: User action (accepted/rejected)
            reasoning: AI reasoning that was shown
            context: Additional context
            user_id: User ID from session
        """
        import logging
        import httpx

        logger = logging.getLogger(__name__)

        try:
            # Make internal call to tracking endpoint
            # Use the API URL from environment or default to localhost
            api_url = "http://localhost:8000"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{api_url}/api/v1/chat/recommendations/track",
                    json={
                        "recommendation_type": recommendation_type,
                        "recommendation_id": recommendation_id,
                        "action": action,
                        "reasoning": reasoning,
                        "context": context,
                    },
                    headers={
                        "Content-Type": "application/json",
                        # Note: In production with authentication, include session token
                    },
                    timeout=5.0,
                )

                if response.status_code == 200:
                    logger.info(
                        f"Recommendation {action} tracked successfully: "
                        f"type={recommendation_type}, id={recommendation_id}"
                    )
                else:
                    logger.warning(
                        f"Failed to track recommendation: "
                        f"status={response.status_code}, "
                        f"response={response.text}"
                    )

        except Exception as e:
            # Don't fail the flow if tracking fails
            logger.error(f"Error tracking recommendation acceptance: {str(e)}")

    async def _convert_to_chatkit_event(
        self,
        orchestrator_event: dict,
        thread: ThreadMetadata,
    ) -> AsyncIterator:
        """Convert orchestrator event to ChatKit event.

        Args:
            orchestrator_event: Event from AgentOrchestrator
            thread: ChatKit thread metadata

        Yields:
            ChatKit response items (text messages, etc.)
        """
        event_type = orchestrator_event.get("type")
        event_data = orchestrator_event.get("data", {})

        if event_type == "token":
            # Stream text token as a response item
            content = event_data.get("content", "")
            yield ResponseTextItem(text=content)

        elif event_type == "tool_call":
            # For now, just log that a tool was called
            # The agent will include the tool result in its final response
            pass

        elif event_type == "tool_result":
            # Tool results are handled by the agent
            pass

        elif event_type == "rag_sources":
            # Include sources in the response text
            sources = event_data.get("sources", [])
            if sources:
                sources_text = "\n\n**Sources:**\n" + "\n".join([
                    f"- {s.get('title', 'Unknown')}: {s.get('source', '')}"
                    for s in sources
                ])
                yield ResponseTextItem(text=sources_text)

        elif event_type == "done":
            # No additional event needed for completion
            pass

        elif event_type == "error":
            # Stream error event
            message = event_data.get("message", "Unknown error")
            yield ErrorEvent(
                error_code="orchestrator_error",
                message=message
            )

        elif event_type == "response":
            # Full response (non-streaming mode)
            content = event_data.get("content", "")
            yield ResponseTextItem(text=content)

    async def _stream_agent_response_simple(
        self,
        message: str,
        thread: ThreadMetadata,
        context: Any,
    ) -> AsyncIterator:
        """Stream agent response without full context (fallback for action handlers).

        Args:
            message: User message
            thread: ChatKit thread
            context: Request context

        Yields:
            ChatKit events
        """
        import uuid
        from chatkit.types import AssistantMessageItem, AssistantMessageContent
        from chatkit.server import ThreadItemAddedEvent

        try:
            # Run agent with context manager for MCP server lifecycle
            async with create_chatbot_agent_context(
                model="google/gemini-2.0-flash-exp:free",
            ) as agent:
                result = Runner.run_streamed(
                    agent,
                    message,
                )

                # Iterate through events and yield ChatKit events
                message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"
                message_yielded = False

                async for event in result.stream_events():
                    if event.type == "run_item_stream_event" and event.item.type == "message_output_item":
                        message_text = ItemHelpers.text_message_output(event.item)

                        assistant_item = AssistantMessageItem(
                            id=message_id,
                            thread_id=thread.id,
                            created_at=datetime.now(timezone.utc),
                            content=[AssistantMessageContent(type="output_text", text=message_text)],
                        )

                        yield ThreadItemAddedEvent(item=assistant_item)
                        message_yielded = True

                # Fallback: if no message yielded, use final_output
                if not message_yielded and hasattr(result, 'final_output') and result.final_output:
                    assistant_item = AssistantMessageItem(
                        id=message_id,
                        thread_id=thread.id,
                        created_at=datetime.now(timezone.utc),
                        content=[AssistantMessageContent(type="output_text", text=result.final_output)],
                    )
                    yield ThreadItemAddedEvent(item=assistant_item)

        except Exception as e:
            yield ErrorEvent(
                error_code=type(e).__name__,
                message=str(e)
            )

    async def _stream_widget_simple(
        self,
        widget: Any,
        thread: ThreadMetadata,
    ) -> AsyncIterator:
        """Stream a widget to the client.

        Args:
            widget: ChatKit widget (Card, List, Form, etc.)
            thread: ChatKit thread

        Yields:
            ChatKit widget events
        """
        # Simplified widget streaming
        # In production, use chatkit.streaming.stream_widget
        from chatkit.streaming import stream_widget
        from chatkit.store import generate_id

        async for event in stream_widget(
            thread=thread,
            widget=widget,
            generate_id=lambda item_type: self.store.generate_item_id(item_type, thread, None),
        ):
            yield event

    # File/image upload methods removed - not supported in current ChatKit SDK version


# Factory function to create server instance
def create_chatkit_server(
    data_store: Optional[Store] = None,
    chat_service: Optional[ChatService] = None,
    rag_service: Optional[RAGService] = None,
    enable_rag: bool = True,
    use_database_store: bool = True,  # New parameter to control store type
) -> TeamFlowChatKitServer:
    """Create a TeamFlow ChatKit server instance.

    Args:
        data_store: Custom ChatKit store (defaults to DatabaseStore if chat_service provided)
        chat_service: ChatService for database operations
        rag_service: RAGService for knowledge base
        enable_rag: Whether to enable RAG
        use_database_store: Whether to use DatabaseStore (default: True)

    Returns:
        Configured TeamFlowChatKitServer instance
    """
    # Use DatabaseStore if chat_service provided and use_database_store is True
    if data_store is None:
        if chat_service and use_database_store:
            data_store = DatabaseStore(chat_service=chat_service)
        else:
            data_store = MemoryStore()

    return TeamFlowChatKitServer(
        data_store=data_store,
        chat_service=chat_service,
        rag_service=rag_service,
        enable_rag=enable_rag,
    )


# Singleton instance
_chatkit_server: Optional[TeamFlowChatKitServer] = None


def get_chatkit_server() -> TeamFlowChatKitServer:
    """Get or create the singleton ChatKit server instance.

    Returns:
        TeamFlowChatKitServer instance with DatabaseStore for persistence
    """
    global _chatkit_server

    if _chatkit_server is None:
        # Import services
        from app.services.chat_service import chat_service
        from app.services.rag_service import rag_service

        _chatkit_server = create_chatkit_server(
            chat_service=chat_service,
            rag_service=rag_service,
            enable_rag=True,
            use_database_store=False,  # Use MemoryStore (DatabaseStore has bugs)
        )

    return _chatkit_server
