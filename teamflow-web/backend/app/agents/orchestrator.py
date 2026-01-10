"""Agent orchestrator for TeamFlow AI Chatbot.

This module provides:
- Agent initialization with OpenAI Agents SDK and Gemini
- Tool injection for task management and analytics
- Conversation history retrieval and management
- Message processing with streaming responses
- Clarification prompts for ambiguous inputs

Handles orchestration between:
- OpenAI Agents SDK (Gemini 2.0 Flash)
- TeamFlow tools (task management, analytics)
- ChatService (conversation persistence)
- RAG service (knowledge base queries)
"""
import asyncio
from typing import AsyncIterator, Optional, Any
from agents import Agent, Runner, RunConfig, ModelResponse
from openai import AsyncOpenAI

from app.agents.prompts import (
    build_context_prompt,
    detect_language,
    Language,
)
from app.agents.chatbot import create_chatbot_agent
from app.agents.tools import TEAMFLOW_TOOLS
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

    Enhanced for:
    - T050: Context management across 5+ related queries
    - T051: Follow-up question handling
    - T052: Context window management with pruning
    """

    def __init__(
        self,
        chat_service: ChatService,
        model: str = "google/gemini-2.0-flash-exp:free",
        max_history_turns: int = 10,
        max_context_tokens: int = 8000,  # T052: Context window limit
        min_context_queries: int = 5,  # T050: Minimum related queries to maintain
    ):
        """Initialize the agent orchestrator.

        Args:
            chat_service: Service for conversation/message persistence
            model: Model to use via OpenRouter (default: google/gemini-2.0-flash-exp:free)
            max_history_turns: Maximum conversation turns to include in context
            max_context_tokens: Maximum context tokens before pruning (T052)
            min_context_queries: Minimum related queries to maintain (T050)
        """
        self.chat_service = chat_service
        self.model = model
        self.max_history_turns = max_history_turns
        self.max_context_tokens = max_context_tokens
        self.min_context_queries = min_context_queries
        self._agent: Optional[Agent] = None
        self._fallback_agent: Optional[Agent] = None  # Fallback agent for runtime errors

    def get_agent(self) -> Agent:
        """Get or create the Agent instance with fallback support.

        Uses create_chatbot_agent which provides:
        - Primary: OpenRouter with Gemini 2.0 Flash
        - Fallback: Direct Gemini API when OpenRouter fails

        Returns:
            Configured Agent with TeamFlow tools
        """
        if self._agent is None:
            # Use create_chatbot_agent for fallback support
            instructions = self._build_agent_instructions()
            self._agent = create_chatbot_agent(
                instructions=instructions,
                model=self.model,
                use_fallback=True,  # Enable automatic fallback
            )

        return self._agent

    def get_fallback_agent(self) -> Agent:
        """Get or create the fallback Agent using direct OpenAI API.

        This is used when the primary agent encounters runtime errors
        (e.g., 429 rate limit from OpenRouter).

        Returns:
            Configured Agent with TeamFlow tools using direct OpenAI API
        """
        if self._fallback_agent is None:
            from app.agents.client import get_openai_fallback_model
            from agents import Agent

            # Map OpenRouter model to OpenAI model
            openai_model_map = {
                "google/gemini-2.0-flash-exp:free": "gpt-5-nano-2025-08-07",
                "google/gemini-2.0-flash-exp": "gpt-5-nano-2025-08-07",
                "google/gemini-flash-1.5": "gpt-4o-mini",
                "google/gemini-2.5-flash": "gpt-4o-mini",
                "google/gemini-2.5-pro": "gpt-4o",
            }
            openai_model = openai_model_map.get(self.model, "gpt-5-nano-2025-08-07")

            # Create direct OpenAI model
            model_instance = get_openai_fallback_model(openai_model)

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

            # Create fallback agent
            instructions = self._build_agent_instructions()
            self._fallback_agent = Agent(
                name="teamflow-assistant-fallback",
                instructions=instructions,
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
            logging.info(f"Created fallback agent using direct OpenAI API: {openai_model}")

        return self._fallback_agent

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
        user_id: str,
        limit: int = 10,
    ) -> list[Message]:
        """
        Retrieve conversation history for context.

        Args:
            conversation_id: UUID of the conversation
            user_id: UUID of the user
            limit: Maximum number of recent messages to retrieve

        Returns:
            List of Message objects, newest first
        """
        conversation = await self.chat_service.get_conversation_internal(
            conversation_id, user_id
        )
        if not conversation:
            return []

        messages = await self.chat_service.get_messages_internal(
            conversation_id, limit=limit
        )
        return messages

    async def _build_conversation_context(
        self,
        conversation_id: Optional[str],
        user_id: Optional[str] = None,
    ) -> tuple[list[dict], Language, list[dict]]:
        """
        Build conversation context for the agent.

        Enhanced for:
        - T050: Maintain context across at least 5 related queries
        - T051: Detect and handle follow-up questions
        - T052: Prune old messages when context limit approached

        Args:
            conversation_id: Optional conversation ID for history
            user_id: Optional user ID for authorization

        Returns:
            Tuple of (conversation_history, detected_language, follow_up_context)
        """
        history = []
        language = "en"
        follow_up_context = []  # T051: Track potential follow-up questions

        if conversation_id and user_id:
            # T050: Retrieve conversation history with minimum query guarantee
            messages = await self.get_history(
                conversation_id,
                user_id,
                limit=max(self.max_history_turns, self.min_context_queries)
            )

            # Detect language from recent messages
            for msg in reversed(messages):  # Check newest first
                if msg.content:
                    language = detect_language(msg.content)
                    break

            # T052: Estimate token count and prune if necessary
            estimated_tokens = sum(len(msg.content or "") // 4 for msg in messages)
            if estimated_tokens > self.max_context_tokens:
                # Prune oldest messages while keeping minimum context (T050, T052)
                keep_count = max(self.min_context_queries, self.max_context_tokens * 4 // 100)
                messages = messages[-keep_count:]

            # T051: Detect follow-up indicators in recent messages
            recent_user_msgs = [m for m in messages if m.role == "user"][-3:]
            follow_up_patterns = [
                "what about", "how do i", "tell me more", "explain",
                "and then", "but what", "why", "how does",
                "kya", "kaisay", "batayein",  # Urdu
            ]
            for msg in recent_user_msgs:
                if msg.content and any(p in msg.content.lower() for p in follow_up_patterns):
                    follow_up_context.append({
                        "is_follow_up": True,
                        "previous_query": msg.content,
                    })
                    break

            # Format for agent context
            for msg in reversed(messages):  # Oldest to newest
                history.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        return history, language, follow_up_context

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
                conversation = await self.chat_service.create_conversation_internal(user_id)
                conversation_id = str(conversation.id)
                yield {"type": "conversation_created", "data": {"id": conversation_id}}

            # Build conversation context
            history, language, follow_up_context = await self._build_conversation_context(
                conversation_id, user_id
            )

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
            await self.chat_service.add_message_internal(
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
                result = await Runner.run(agent, input=context_prompt)
                response_content = result.final_output

                # Save assistant response
                await self.chat_service.add_message_internal(
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
        Run agent with streaming response and automatic fallback on errors.

        This method implements runtime fallback:
        1. Tries the primary agent first
        2. On 429 rate limit or similar errors, retries with fallback agent (direct Gemini)
        3. Streams the response token-by-token

        Args:
            agent: The Agent instance
            message: The message to process
            conversation_id: Conversation ID for saving responses

        Yields:
            Stream events (token, fallback_triggered, error, done)
        """
        import logging

        try:
            # Try running with the primary agent
            result = await Runner.run(agent, input=message)
        except Exception as primary_error:
            error_str = str(primary_error).lower()
            error_code = getattr(primary_error, 'code', None)

            # Check if this is a 429 rate limit or similar error that warrants fallback
            is_rate_limit = (
                '429' in error_str or
                error_code == 429 or
                'rate limit' in error_str or
                'rate-limited' in error_str or
                'provider returned error' in error_str
            )

            if is_rate_limit:
                logging.warning(f"Primary agent hit rate limit (429): {primary_error}. Using fallback agent...")

                # Yield fallback event so UI can inform user
                yield {
                    "type": "fallback_triggered",
                    "data": {
                        "reason": "rate_limit",
                        "message": "Primary API rate limited. Switching to direct Gemini API..."
                    }
                }

                try:
                    # Retry with fallback agent
                    fallback_agent = self.get_fallback_agent()
                    result = await Runner.run(fallback_agent, input=message)
                    logging.info("Fallback agent succeeded")
                except Exception as fallback_error:
                    logging.error(f"Fallback agent also failed: {fallback_error}")
                    yield {
                        "type": "error",
                        "data": {
                            "message": f"Primary API rate limited and fallback failed: {str(fallback_error)}",
                            "type": type(fallback_error).__name__,
                        }
                    }
                    return
            else:
                # Not a rate limit error - just surface the original error
                logging.error(f"Agent execution failed: {primary_error}")
                yield {
                    "type": "error",
                    "data": {
                        "message": str(primary_error),
                        "type": type(primary_error).__name__,
                    }
                }
                return

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
            await self.chat_service.add_message_internal(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
            )

        yield {"type": "done", "data": {}}

    def _should_skip_rag_for_greeting(self, user_message: str) -> bool:
        """Simple check to skip RAG for greetings to save tokens.

        The Agent SDK's LLM is smart enough to decide when to use tools.
        This is just a token-saving optimization for obvious greetings.

        Args:
            user_message: The user's input message

        Returns:
            True if this is obviously a greeting (skip RAG)
        """
        message_lower = user_message.lower().strip()

        # Skip very short messages
        if len(message_lower) < 8:
            return True

        # Skip common greetings
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon",
            "good evening", "how are you", "how's it going",
            "thanks", "thank you", "bye", "goodbye",
        ]
        return any(greeting == message_lower or message_lower.startswith(greeting + " ")
                   for greeting in greetings)

    async def process_with_rag(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        use_knowledge_base: bool = True,
    ) -> AsyncIterator[dict]:
        """
        Process message with optional RAG knowledge base integration.

        The Agent SDK's LLM decides when to use the search_knowledge_base tool.
        This method only skips processing for obvious greetings to save tokens.

        Args:
            user_message: The user's input
            conversation_id: Optional conversation ID
            user_id: Optional user ID
            use_knowledge_base: Whether RAG tools are available (always True when called)

        Yields:
            Stream events from agent processing
        """
        # The agent has the search_knowledge_base tool and will decide when to use it
        # Just delegate to normal processing
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
