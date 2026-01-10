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
import uuid
from typing import AsyncIterator, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
from uuid import UUID

from agents import Agent, Runner, RunContextWrapper
from chatkit.server import (
    ChatKitServer,
    Store,
    ThreadMetadata,
    UserMessageItem,
    ClientToolCallItem,
    StreamingResult,
    ErrorEvent,
    ThreadStreamEvent,
)
from chatkit.types import (
    AssistantMessageItem,
    AssistantMessageContent,
    ThreadItemDoneEvent,
)
from chatkit.agents import (
    simple_to_agent_input,
    stream_agent_response,
    AgentContext,
)
from chatkit.store import Store as StoreClass, Page, ThreadItem
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import AsyncIterator, Dict, List
import uuid

from app.agents.orchestrator import AgentOrchestrator
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app.agents.chatbot import create_chatbot_agent


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
        self._fallback_agent: Optional[Agent] = None  # Fallback agent for runtime errors

        # Initialize agent
        self._init_agent()

    def _init_agent(self):
        """Initialize the chatbot agent."""
        # Create agent with system instructions
        # Using OpenRouter models with OpenAIChatCompletionsModel wrapper
        self.assistant_agent = create_chatbot_agent(
            model="google/gemini-2.0-flash-exp:free",
        )

        # Initialize orchestrator if chat_service is available
        if self.chat_service:
            self.orchestrator = AgentOrchestrator(
                chat_service=self.chat_service,
                model="google/gemini-2.0-flash-exp:free",
            )

    def _get_fallback_agent(self) -> Agent:
        """Get or create the fallback Agent using direct OpenAI API.

        This is used when the primary agent encounters runtime errors
        (e.g., 429 rate limit from OpenRouter).

        Returns:
            Configured Agent with TeamFlow tools using direct OpenAI API
        """
        if self._fallback_agent is None:
            from app.agents.client import get_openai_fallback_model
            from agents import Agent

            # Create direct OpenAI model
            model_instance = get_openai_fallback_model("gpt-5-nano-2025-08-07")

            # Import tools
            from app.agents.tools import (
                search_knowledge_base,
                add_task,
                list_tasks,
                assign_task,
                complete_task,
                delete_task,
                archive_task,
                update_task_priority,
                update_task_due_date,
                update_task_status,
                list_projects,
                create_project,
                get_project_details,
                get_profitability,
                workload_summary,
                suggest_assignee,
                add_time_entry,
                list_time_entries,
                get_time_for_task,
                update_time_entry,
                delete_time_entry,
            )

            # Create fallback agent with same instructions
            from app.agents.chatbot import TEAMFLOW_AGENT_INSTRUCTIONS
            self._fallback_agent = Agent(
                name="teamflow-assistant-fallback",
                instructions=TEAMFLOW_AGENT_INSTRUCTIONS,
                model=model_instance,
                tools=[
                    search_knowledge_base,
                    add_task,
                    list_tasks,
                    assign_task,
                    complete_task,
                    delete_task,
                    archive_task,
                    update_task_priority,
                    update_task_due_date,
                    update_task_status,
                    list_projects,
                    create_project,
                    get_project_details,
                    get_profitability,
                    workload_summary,
                    suggest_assignee,
                    add_time_entry,
                    list_time_entries,
                    get_time_for_task,
                    update_time_entry,
                    delete_time_entry,
                ],
            )

            import logging
            logging.info("[ChatKit] Created fallback agent using direct OpenAI API: gpt-5-nano-2025-08-07")

        return self._fallback_agent

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

        CRITICAL: Follow the official ChatKit pattern:
        - The ChatKitServer base class ALREADY handles user message persistence
        - The ChatKitServer base class ALREADY calls respond() with proper input
        - We just need to run the agent and yield events from stream_agent_response()

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

            # Run the agent and stream the response
            agent_to_use = self.assistant_agent
            result = None
            used_fallback = False

            try:
                result = Runner.run_streamed(
                    agent_to_use,
                    input_items,  # Pass conversation history
                    context=agent_context
                )
                logger.info(f"[ChatKit respond] Agent execution started (primary), streaming response...")
            except Exception as primary_error:
                error_str = str(primary_error).lower()
                error_code = getattr(primary_error, 'code', None)

                # Check if this is a 429 rate limit or similar error
                is_rate_limit = (
                    '429' in error_str or
                    error_code == 429 or
                    'rate limit' in error_str or
                    'rate-limited' in error_str or
                    'provider returned error' in error_str
                )

                if is_rate_limit:
                    logger.warning(f"[ChatKit respond] Primary agent hit rate limit (429): {primary_error}. Using fallback agent...")

                    # Retry with fallback agent
                    fallback_agent = self._get_fallback_agent()
                    agent_to_use = fallback_agent
                    used_fallback = True

                    result = Runner.run_streamed(
                        agent_to_use,
                        input_items,
                        context=agent_context
                    )
                    logger.info(f"[ChatKit respond] Fallback agent execution started, streaming response...")
                else:
                    # Not a rate limit error - re-raise
                    raise

            # CRITICAL FIX: Generate unique message ID upfront to prevent overwriting
            # The stream_agent_response() helper uses __fake_id__ during streaming,
            # which causes the frontend to update the same message repeatedly.
            # We generate a unique ID now and ensure all events for this response use it.
            import uuid
            unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"
            logger.info(f"[ChatKit respond] Generated unique message ID: {unique_message_id}")

            # Stream the agent response using ChatKit's helper
            # The helper handles all ChatKit events including ThreadItemDoneEvent for persistence
            # We just need to yield events as-is for proper streaming and persistence
            logger.info(f"[ChatKit respond] Starting agent response streaming for thread {thread.id}")

            event_types_seen = set()
            event_count = 0
            message_started = False

            try:
                async for event in stream_agent_response(agent_context, result):
                    event_count += 1
                    event_type = type(event).__name__
                    event_types_seen.add(event_type)

                    # CRITICAL: Ensure unique ID for assistant messages
                    # When we see an assistant message event with __fake_id__, replace it with our unique ID
                    # This prevents the frontend from overwriting previous messages
                    if hasattr(event, 'item'):
                        item = event.item
                        if hasattr(item, 'id') and item.id == "__fake_id__":
                            # Replace __fake_id__ with our unique ID
                            new_item = item.model_copy(update={"id": unique_message_id})
                            event = event.model_copy(update={"item": new_item})
                            logger.info(f"[ChatKit respond] Replaced __fake_id__ with {unique_message_id} in {event_type}")
                            message_started = True

                    # CRITICAL: Log event details to debug message overwriting
                    event_id = getattr(event, 'id', None)
                    event_item_id = getattr(event, 'item', None)
                    if event_item_id:
                        event_item_id = getattr(event_item_id, 'id', None)

                    # Use print to ensure output is visible
                    print(f"[ChatKit respond] Event #{event_count}: {event_type}, id={event_id}, item.id={event_item_id}")
                    logger.info(f"[ChatKit respond] Event #{event_count}: {event_type}, id={event_id}, item.id={event_item_id}")

                    # Check for ThreadItemReplacedEvent which would cause overwriting
                    if event_type == 'ThreadItemReplacedEvent':
                        logger.warning(f"[ChatKit respond] ⚠️ ThreadItemReplacedEvent detected! item.id={event_item_id}")

                    # Check for ThreadItemDoneEvent to verify persistence
                    if event_type == 'ThreadItemDoneEvent':
                        item = getattr(event, 'item', None)
                        if item:
                            logger.info(f"[ChatKit respond] ✓ ThreadItemDoneEvent with item.id={item.id}")

                    # Yield all events - with fixed unique ID for assistant messages
                    yield event

            except Exception as streaming_error:
                error_str = str(streaming_error).lower()
                error_code = getattr(streaming_error, 'code', None)

                # Check if this is a 429 rate limit error during streaming
                is_rate_limit = (
                    '429' in error_str or
                    error_code == 429 or
                    'rate limit' in error_str or
                    'rate-limited' in error_str or
                    'provider returned error' in error_str
                )

                # If we hit rate limit during streaming and haven't used fallback yet
                if is_rate_limit and not used_fallback:
                    logger.warning(f"[ChatKit respond] Rate limit during streaming: {streaming_error}. Retrying with fallback...")

                    # Retry with fallback agent
                    fallback_agent = self._get_fallback_agent()

                    result = Runner.run_streamed(
                        fallback_agent,
                        input_items,
                        context=agent_context
                    )
                    logger.info(f"[ChatKit respond] Fallback agent execution started, streaming response...")

                    # CRITICAL: Generate new unique message ID for fallback response
                    unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"
                    logger.info(f"[ChatKit respond] Generated unique message ID for fallback: {unique_message_id}")

                    # Stream the fallback response
                    async for event in stream_agent_response(agent_context, result):
                        event_type = type(event).__name__
                        event_types_seen.add(event_type)
                        logger.debug(f"[ChatKit respond] Event (fallback): {event_type}")

                        # CRITICAL: Ensure unique ID for assistant messages in fallback
                        if hasattr(event, 'item'):
                            item = event.item
                            if hasattr(item, 'id') and item.id == "__fake_id__":
                                # Replace __fake_id__ with our unique ID
                                new_item = item.model_copy(update={"id": unique_message_id})
                                event = event.model_copy(update={"item": new_item})
                                logger.info(f"[ChatKit respond] Replaced __fake_id__ with {unique_message_id} in fallback {event_type}")

                        # Yield all events with fixed unique ID
                        yield event
                else:
                    # Either not a rate limit error, or we already tried fallback
                    logger.error(f"[ChatKit respond] Error during streaming: {streaming_error}")
                    yield ErrorEvent(
                        error_code=type(streaming_error).__name__,
                        message=str(streaming_error)
                    )

            logger.info(f"[ChatKit respond] Response streaming completed for thread {thread.id}. Total events: {event_count}, Event types seen: {event_types_seen}")

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
        """Stream agent response without orchestrator (fallback).

        Args:
            message: User message
            thread: ChatKit thread
            context: Request context

        Yields:
            ChatKit events
        """
        try:
            # Run agent with streaming
            # Note: run_streamed() is sync and returns RunResultStreaming immediately
            result = Runner.run_streamed(
                self.assistant_agent,
                message,
            )

            # Stream response events using stream_events()
            async for event in result.stream_events():
                # Process events here if needed
                # For now, we'll let the ChatKit SDK handle the streaming
                pass

            # ChatKit SDK handles completion automatically
            pass

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
) -> TeamFlowChatKitServer:
    """Create a TeamFlow ChatKit server instance.

    Args:
        data_store: Custom ChatKit store (defaults to MemoryStore)
        chat_service: ChatService for database operations
        rag_service: RAGService for knowledge base
        enable_rag: Whether to enable RAG

    Returns:
        Configured TeamFlowChatKitServer instance
    """
    # Use default in-memory store if not provided
    if data_store is None:
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
        TeamFlowChatKitServer instance
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
        )

    return _chatkit_server
