"""Agent orchestrator for TeamFlow AI Chatbot.

This module provides:
- Agent initialization with OpenAI Agents SDK and Gemini
- Tool injection from MCP server
- Conversation history retrieval and management
- Message processing with streaming responses
- Clarification prompts for ambiguous inputs

Handles orchestration between:
- OpenAI Agents SDK (Gemini 2.0 Flash)
- MCP server tools (task management, analytics)
- ChatService (conversation persistence)
- RAG service (knowledge base queries)
"""
import asyncio
from typing import AsyncIterator, Optional, Any
from agents import Agent, Runner, RunConfig, ModelResponse
from openai import AsyncOpenAI

from app.agents.client import initialize_gemini_client
from app.agents.prompts import (
    build_context_prompt,
    detect_language,
    Language,
)
from app.agents.chatbot import create_chatbot_agent
from app.mcp.server import mcp
from app.services.chat_service import ChatService
from app.models.chat import Message


class AgentOrchestrator:
    """
    Orchestrates Agent interactions with MCP tools and conversation context.

    The orchestrator:
    1. Initializes the Agent with Gemini client
    2. Injects tools from MCP server
    3. Retrieves conversation history for context
    4. Processes user messages and streams responses
    5. Handles tool calls and their results
    6. Manages clarification prompts for ambiguous inputs
    """

    def __init__(
        self,
        chat_service: ChatService,
        model: str = "gemini-2.0-flash-exp",
        max_history_turns: int = 10,
    ):
        """Initialize the agent orchestrator.

        Args:
            chat_service: Service for conversation/message persistence
            model: Gemini model to use (default: gemini-2.0-flash-exp)
            max_history_turns: Maximum conversation turns to include in context
        """
        self.chat_service = chat_service
        self.model = model
        self.max_history_turns = max_history_turns
        self._agent: Optional[Agent] = None

    def get_agent(self) -> Agent:
        """Get or create the Agent instance.

        Returns:
            Configured Agent with MCP tools
        """
        if self._agent is None:
            # Initialize Gemini client (sets default for Agents SDK)
            initialize_gemini_client()

            # Create agent with custom instructions
            instructions = self._build_agent_instructions()
            self._agent = Agent(
                name="teamflow-assistant",
                instructions=instructions,
                mcp_tools=mcp.get_tools(),  # Inject tools from MCP server
                model=self.model,
            )

        return self._agent

    def _build_agent_instructions(self) -> str:
        """Build agent instructions with language awareness.

        Returns:
            System prompt for the agent
        """
        # Base instructions from prompts module
        from app.agents.prompts import _get_english_system_prompt
        return _get_english_system_prompt()

    async def get_history(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> list[Message]:
        """
        Retrieve conversation history for context.

        Args:
            conversation_id: UUID of the conversation
            limit: Maximum number of recent messages to retrieve

        Returns:
            List of Message objects, newest first
        """
        conversation = await self.chat_service.get_conversation(conversation_id)
        if not conversation:
            return []

        messages = await self.chat_service.get_messages(conversation_id, limit=limit)
        return messages

    async def _build_conversation_context(
        self,
        conversation_id: Optional[str],
    ) -> tuple[list[dict], Language]:
        """
        Build conversation context for the agent.

        Args:
            conversation_id: Optional conversation ID for history

        Returns:
            Tuple of (conversation_history, detected_language)
        """
        history = []
        language = "en"

        if conversation_id:
            # Retrieve conversation history
            messages = await self.get_history(conversation_id, limit=self.max_history_turns)

            # Detect language from recent messages
            for msg in reversed(messages):  # Check newest first
                if msg.content:
                    language = detect_language(msg.content)
                    break

            # Format for agent context
            for msg in reversed(messages):  # Oldest to newest
                history.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        return history, language

    def _needs_clarification(self, user_message: str, context: dict) -> tuple[bool, str]:
        """
        Check if user input is ambiguous and needs clarification.

        Args:
            user_message: The user's input message
            context: Additional context (conversation state, available info)

        Returns:
            Tuple of (needs_clarification, clarification_prompt)
        """
        message_lower = user_message.lower().strip()

        # Check for empty or very short messages
        if len(message_lower) < 5:
            return True, "Could you please provide more details about what you'd like to do?"

        # Check for vague task creation
        vague_task_patterns = [
            "create a task",
            "make a task",
            "add a task",
            "new task",
            "task bananao",  # Urdu
            "task banaiye",
        ]

        for pattern in vague_task_patterns:
            if pattern in message_lower:
                # Check if essential details are missing
                missing = []
                if not any(word in message_lower for word in ["title", "called", "name", "for"]):
                    missing.append("task title")
                if not any(word in message_lower for word in ["project", "agency"]):
                    missing.append("project/agency")

                if missing:
                    return True, f"I'd be happy to create a task. Could you please provide: {', '.join(missing)}?"

        # Check for vague assignment
        if "assign" in message_lower and not any(word in message_lower for word in ["to", "ko", "ke liye"]):
            return True, "Who would you like to assign the task to?"

        # Check for queries without specific target
        vague_query_patterns = [
            "show tasks",
            "what tasks",
            "list tasks",
            "kuch tasks",
            "tasks dikhao",
        ]

        for pattern in vague_query_patterns:
            if pattern == message_lower.strip():
                return True, "Which tasks would you like to see? (e.g., 'show high priority tasks' or 'list my tasks')"

        return False, ""

    async def process_message(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        stream: bool = True,
    ) -> AsyncIterator[dict]:
        """
        Process a user message through the Agent with streaming response.

        This method:
        1. Retrieves conversation history for context
        2. Detects language (English/Urdu)
        3. Checks if clarification is needed
        4. Runs the Agent with tools
        5. Streams response events (tokens, tool calls, results)

        Args:
            user_message: The user's input message
            conversation_id: Optional existing conversation ID
            user_id: Optional user ID for RBAC
            stream: Whether to stream the response

        Yields:
            Event dictionaries with format:
            {
                "type": "token" | "tool_call" | "tool_result" | "error" | "done",
                "data": <event-specific data>
            }
        """
        try:
            # Get or create conversation
            if not conversation_id:
                conversation = await self.chat_service.create_conversation(user_id)
                conversation_id = conversation.id
                yield {"type": "conversation_created", "data": {"id": conversation_id}}

            # Build conversation context
            history, language = await self._build_conversation_context(conversation_id)

            # Check for clarification needs
            needs_clarification, clarification_prompt = self._needs_clarification(
                user_message,
                {"conversation_id": conversation_id, "user_id": user_id}
            )

            if needs_clarification:
                yield {"type": "clarification_needed", "data": {"prompt": clarification_prompt}}
                yield {"type": "done", "data": {"reason": "clarification"}}
                return

            # Save user message to conversation
            await self.chat_service.add_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
            )

            # Get agent and run
            agent = self.get_agent()

            # Build context message
            context_prompt = build_context_prompt(
                user_message=user_message,
                conversation_history=history,
                language_override=language,
            )

            # Run agent with streaming
            if stream:
                async for event in self._run_agent_stream(agent, context_prompt, conversation_id):
                    yield event
            else:
                # Non-streaming mode (for testing)
                result = await Runner.run(agent, context_prompt)
                response_content = result.final_output

                # Save assistant response
                await self.chat_service.add_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_content,
                )

                yield {"type": "response", "data": {"content": response_content}}
                yield {"type": "done", "data": {}}

        except Exception as e:
            yield {
                "type": "error",
                "data": {
                    "message": str(e),
                    "type": type(e).__name__,
                }
            }

    async def _run_agent_stream(
        self,
        agent: Agent,
        message: str,
        conversation_id: str,
    ) -> AsyncIterator[dict]:
        """
        Run agent with streaming response.

        Args:
            agent: The Agent instance
            message: The message to process
            conversation_id: Conversation ID for saving responses

        Yields:
            Stream events
        """
        # Run the agent
        result = await Runner.run(agent, message)

        # Stream the response
        response_text = result.final_output or ""

        # Token-by-token streaming simulation
        # (The actual Agents SDK returns complete responses, so we chunk for UX)
        words = response_text.split()
        accumulated = ""

        for word in words:
            accumulated += word + " "
            yield {"type": "token", "data": {"content": word + " "}}

        # Save complete response to conversation
        if response_text:
            await self.chat_service.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
            )

        yield {"type": "done", "data": {}}

    async def process_with_rag(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        use_knowledge_base: bool = True,
    ) -> AsyncIterator[dict]:
        """
        Process message with optional RAG knowledge base integration.

        This is used for User Story 2 (Knowledge Base Queries).

        Args:
            user_message: The user's input
            conversation_id: Optional conversation ID
            user_id: Optional user ID
            use_knowledge_base: Whether to query Qdrant for context

        Yields:
            Stream events
        """
        if use_knowledge_base:
            # Import RAG service
            from app.services.rag_service import rag_service

            # Search knowledge base
            search_results = await rag_service.search_knowledge_base(
                query=user_message,
                limit=3,
            )

            if search_results:
                # Add RAG context to message
                kb_context = "\n\n**Relevant Knowledge Base Articles:**\n"
                for i, result in enumerate(search_results, 1):
                    kb_context += f"\n{i. {result.payload.get('title', 'Unknown')}"
                    kb_context += f"\n   Source: {result.payload.get('source', 'N/A')}"
                    kb_context += f"\n   {result.payload.get('text', '')[:200]}...\n"

                enhanced_message = user_message + kb_context
                async for event in self.process_message(enhanced_message, conversation_id, user_id):
                    yield event
                return

        # Fallback to normal processing
        async for event in self.process_message(user_message, conversation_id, user_id):
            yield event


# Singleton instance for easy import
orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator(chat_service: Optional[ChatService] = None) -> AgentOrchestrator:
    """Get or create the singleton orchestrator instance.

    Args:
        chat_service: Optional ChatService (uses existing if orchestrator already created)

    Returns:
        AgentOrchestrator instance
    """
    global orchestrator

    if orchestrator is None:
        if chat_service is None:
            from app.services.chat_service import chat_service as default_service
            chat_service = default_service

        orchestrator = AgentOrchestrator(chat_service=chat_service)

    return orchestrator
