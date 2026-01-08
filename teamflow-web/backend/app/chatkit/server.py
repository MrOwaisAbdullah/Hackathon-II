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
from typing import AsyncIterator, Any, Optional
from pathlib import Path
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
from chatkit.agents import (
    simple_to_agent_input,
    stream_agent_response,
    AgentContext,
)
from chatkit.store import Store as StoreClass, Page, ThreadItem
from datetime import datetime
from dataclasses import dataclass, field
from typing import AsyncIterator, Dict, List

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
    """In-memory store for ChatKit threads and items.

    Simple thread-safe implementation using dictionaries.
    Non-persistent - data is lost on restart.
    """

    def __init__(self) -> None:
        self._threads: Dict[str, _ThreadState] = {}
        self._items_map: Dict[str, ThreadItem] = {}

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
        """Add an item to a thread."""
        state = self._threads.get(thread_id)
        if state:
            state.items.append(item)
        self._items_map[item.id] = item

    async def save_item(
        self,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Save an item (for updates)."""
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
        item_id: str,
        context: dict,
    ) -> ThreadItem | None:
        """Load an item by ID."""
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
        """Delete an item from a thread."""
        state = self._threads.get(thread_id)
        if state:
            state.items = [i for i in state.items if i.id != item_id]

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

        # Initialize agent
        self._init_agent()

    def _init_agent(self):
        """Initialize the chatbot agent."""
        # Create agent with system instructions
        # Using OpenRouter models with OpenAIChatCompletionsModel wrapper
        self.assistant_agent = create_chatbot_agent(
            model="mistralai/devstral-2512:free",
        )

        # Initialize orchestrator if chat_service is available
        if self.chat_service:
            self.orchestrator = AgentOrchestrator(
                chat_service=self.chat_service,
                model="mistralai/devstral-2512:free",
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

        Args:
            thread: ChatKit thread metadata
            input: User message or client tool output
            context: Request context (user_id, session, etc.)

        Yields:
            ThreadStreamEvent objects for ChatKit
        """
        try:
            # Extract user message content
            if isinstance(input, UserMessageItem):
                user_message = self._extract_message_content(input.content)
            elif isinstance(input, ClientToolCallItem):
                user_message = f"Tool output: {input.output}"
            else:
                yield ErrorEvent(
                    error_code="unknown_input_type",
                    message=f"Unknown input type: {type(input)}"
                )
                return

            # Load recent thread history for context
            items_page = await self.store.load_thread_items(
                thread.id,
                after=None,
                limit=20,
                order="asc",
                context=context or {},
            )

            # Convert thread items to agent input format
            input_items = await simple_to_agent_input(items_page.data)

            # Create agent context
            agent_context = AgentContext(
                thread=thread,
                store=self.store,
                request_context=context or {}
            )

            # Run the agent and stream the response
            # IMPORTANT: Pass input_items (conversation history) NOT just the user_message
            # The agent needs the full conversation context to respond properly
            result = Runner.run_streamed(
                self.assistant_agent,
                input_items,  # Pass conversation history, not just message string
                context=agent_context
            )

            # Stream the agent response as ChatKit events
            async for event in stream_agent_response(agent_context, result):
                yield event

        except Exception as e:
            # Log error
            import logging
            logger = logging.getLogger(__name__)
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
        try:
            # Example: Handle "add_to_todo" action
            if action_name == "add_to_todo":
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

    def _extract_message_content(self, content: Any) -> str:
        """Extract text content from ChatKit message content.

        Args:
            content: ChatKit message content (text, parts, etc.)

        Returns:
            Extracted text string
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            # Handle multi-part content (text, images, files)
            text_parts = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict):
                    if part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    # Handle images/files as needed
            return " ".join(text_parts)
        else:
            return str(content)

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
