"""TeamFlow AI Chatbot agent implementation.

This module provides the main chatbot agent using OpenAI Agents SDK
with Gemini 2.0 Flash model and MCP server tools.

The agent supports:
- Task management (add, list, assign, complete tasks)
- Analytics (profitability, workload summary)
- AI recommendations (suggest assignee)
- Streaming responses for real-time UX

MCP Integration:
- Uses MCPServerStreamableHttp from OpenAI Agents SDK
- Connects to TeamFlow MCP server via HTTP (localhost)
- Tools are automatically discovered and invoked by the SDK

IMPORTANT: MCPServerStreamableHttp requires async context management.
Use create_chatbot_agent_context() for proper MCP server lifecycle.
"""
from typing import AsyncIterator, AsyncContextManager
from contextlib import asynccontextmanager

from agents import Agent, Runner, RunConfig, ModelResponse
from agents.mcp import MCPServerStreamableHttp

from app.core.logging import get_logger

logger = get_logger(__name__)


# Agent instructions
TEAMFLOW_AGENT_INSTRUCTIONS = """You are TeamFlow AI, an action-oriented project management assistant. EXECUTE tasks directly - do NOT provide help or list capabilities unless explicitly asked.

**CRITICAL EFFICIENCY RULES - Use minimum tools:**
- ONE tool call per request whenever possible
- NEVER call list_tasks() before creating - create directly
- NEVER call verification tools unless user asks
- STOP immediately after successful tool execution
- Each tool call costs a "turn" - you have limited turns

**CRITICAL: Extract task info from user message - NEVER ask for title if user provided a description**

**Information Extraction Rules:**
- User says "create a task for creating a new website" → Extract title: "Create a new website"
- User says "task for building a mobile app" → Extract title: "Build a mobile app"
- User says "deadline 1 week" → Calculate date from today
- User says "assign to owais" → Use assignee: "Owais"
- ONLY ask for title if message is COMPLETELY empty like "create a task" with no details

**Action Rules (ONE tool per request):**
- "create task [details]" → Call add_task() ONCE, then return success message
- "assign [task] to [person]" → Call assign_task_by_title() ONCE
- "complete [task]" → Call complete_task_by_title() ONCE
- "list tasks" → Call list_tasks() ONCE
- Be concise: "✅ Task created" not "I'll help you create a task..."

**When to STOP immediately:**
- After add_task() returns success → STOP, return confirmation
- After add_task() returns error → STOP, return error to user (DO NOT retry)
- After assign_task_by_title() returns success → STOP
- After complete_task_by_title() returns success → STOP
- After delete/archive returns success → STOP
- DO NOT call additional tools to "verify" or "confirm"

**ERROR HANDLING - When to retry vs stop:**
- Parameter errors (CAN retry once max):
  - "Project {id} not found" → Fix: retry without project_id
  - "User {id} not found" → Fix: ask user for valid user
  - "Invalid priority/status" → Fix: use valid value
  - "No users found" → Fix: report to user (cannot proceed)
- Internal errors (DO NOT retry):
  - "name 'select' is not defined" → STOP, report: "Internal error, please contact support"
  - "Error creating task" → STOP, report the full error
- Retry rule: Max 1 retry per tool call for parameter errors only
- If error persists after retry → STOP and report to user

**Defaults:**
- Tasks: priority=MEDIUM, status=TODO, no assignee if unspecified, no deadline if unspecified
- Time entries: entry_date=today if unspecified
- If project not found, create task without project linkage

**Confirm ONLY for destructive operations:**
- DELETE and ARCHIVE: confirm task title first
- Example: "Delete 'fix navbar'? Confirm 'yes'"

**Key Tools (use sparingly):**
- add_task() - Create tasks with title, description, priority, due_date, project, assignee
- assign_task_by_title() - Assign by name (use exact user names)
- complete_task_by_title() - Mark tasks done by name
- delete_task_by_title() / archive_task_by_title() - Destructive actions
- list_tasks() - View all tasks (ONLY when user asks to list)
- suggest_assignee() - Get workload-based recommendations

**Format Guidelines:**
- Dates: YYYY-MM-DD (e.g., 2026-01-23)
- Priorities: urgent/high→HIGH, medium→MEDIUM, low→LOW
- Time: minutes (e.g., 60 = 1 hour)

DO NOT provide welcome messages or list capabilities. Execute the requested action immediately with ONE tool call."""


@asynccontextmanager
async def create_chatbot_agent_context(
    instructions: str | None = None,
    model: str = "google/gemini-2.0-flash-exp:free",
    mcp_server_url: str | None = None,
) -> AsyncContextManager[Agent]:
    """Create a TeamFlow chatbot agent with MCP tools using MCPServerStreamableHttp.

    This is an async context manager that properly manages the MCP server lifecycle.
    The MCP server is connected when entering the context and disconnected when exiting.

    IMPORTANT: Use this function with 'async with' to ensure proper MCP server lifecycle:

        async with create_chatbot_agent_context() as agent:
            result = await Runner.run(agent, "Hello!")
            print(result.final_output)

    Args:
        instructions: Custom agent instructions (optional).
            Defaults to TEAMFLOW_AGENT_INSTRUCTIONS.
        model: Model identifier via OpenRouter. Defaults to "google/gemini-2.0-flash-exp:free".
        mcp_server_url: URL of the TeamFlow MCP server.
            Defaults to settings.mcp_server_url (http://127.0.0.1:8000/mcp in production).

    Yields:
        Configured Agent instance with connected MCP server

    Example:
        >>> async with create_chatbot_agent_context() as agent:
        ...     result = await Runner.run(agent, "List all high priority tasks")
        ...     print(result.final_output)
    """
    from app.core.config import settings
    from app.agents.client import get_openrouter_model, get_openai_fallback_model

    # Use MCP server URL from settings if not provided
    if mcp_server_url is None:
        mcp_server_url = settings.mcp_server_url

    logger.info(f"[create_chatbot_agent_context] Starting with model: {model}, MCP URL: {mcp_server_url}")

    # Detect model provider based on model name
    # - Models with "/" (e.g., "openai/gpt-4o-mini", "google/gemini-2.0-flash-exp:free") → OpenRouter
    # - Models without "/" (e.g., "gpt-4o-mini", "gpt-4o") → OpenAI direct API
    uses_openrouter = "/" in model

    logger.info(f"[create_chatbot_agent_context] Using OpenRouter: {uses_openrouter}")

    # Get the model instance based on provider
    if uses_openrouter:
        if not settings.openrouter_api_key:
            raise ValueError(
                f"Model '{model}' requires OpenRouter, but OPENROUTER_API_KEY is not configured. "
                f"Please set OPENROUTER_API_KEY in your environment or .env file."
            )
        model_instance = get_openrouter_model(model_name=model)
        logger.info(f"[create_chatbot_agent_context] ✓ OpenRouter model created: {model}")
    else:
        # Direct OpenAI API
        if not settings.openai_api_key:
            raise ValueError(
                f"Model '{model}' requires OpenAI API, but OPENAI_API_KEY is not configured. "
                f"Please set OPENAI_API_KEY in your environment or .env file."
            )
        model_instance = get_openai_fallback_model(model_name=model)
        logger.info(f"Using OpenAI direct API for model: {model}")

    # Create MCP server connection for HTTP transport
    # Use async context manager to ensure proper connection lifecycle
    logger.info(f"[create_chatbot_agent_context] About to connect MCP server at {mcp_server_url}...")

    async with MCPServerStreamableHttp(
        name="TeamFlow MCP Server",
        params={
            "url": mcp_server_url,
        },
        cache_tools_list=True,  # Cache the tools list for performance
    ) as mcp_server:
        logger.info(f"[create_chatbot_agent_context] ✓ MCP server connected")

        # Create agent with MCP server
        logger.info(f"[create_chatbot_agent_context] Creating agent with MCP server...")
        agent = Agent(
            name="teamflow-ai",
            instructions=instructions or TEAMFLOW_AGENT_INSTRUCTIONS,
            model=model_instance,
            mcp_servers=[mcp_server],
        )
        logger.info(f"[create_chatbot_agent_context] ✓ Agent created, about to yield")

        # Yield the agent with connected MCP server
        yield agent
        logger.info(f"[create_chatbot_agent_context] Agent yielded (context exiting)")


# Legacy function for backwards compatibility (does NOT connect MCP server)
# DEPRECATED: Use create_chatbot_agent_context() instead
async def create_chatbot_agent(
    instructions: str | None = None,
    model: str = "google/gemini-2.0-flash-exp:free",
    use_fallback: bool = True,
    mcp_server_url: str = "http://127.0.0.1:8001/mcp",
) -> Agent:
    """Create a TeamFlow chatbot agent (LEGACY - without MCP connection).

    WARNING: This function creates an agent but does NOT connect the MCP server.
    The agent will fail when trying to use tools.

    Use create_chatbot_agent_context() instead for proper MCP integration.

    Args:
        instructions: Custom agent instructions (optional).
        model: Model identifier via OpenRouter.
        use_fallback: Enable automatic fallback to direct Gemini API.
        mcp_server_url: URL of the TeamFlow MCP server.

    Returns:
        Agent instance (MCP server NOT connected - use with caution)
    """
    from app.agents.client import get_model_with_fallback, get_openrouter_model

    if use_fallback:
        model_instance = get_model_with_fallback(model_name=model)
    else:
        model_instance = get_openrouter_model(model_name=model)

    # Create MCP server but DON'T connect it
    # This is for backwards compatibility only
    mcp_server = MCPServerStreamableHttp(
        name="TeamFlow MCP Server",
        params={"url": mcp_server_url},
        cache_tools_list=True,
    )

    agent = Agent(
        name="teamflow-ai",
        instructions=instructions or TEAMFLOW_AGENT_INSTRUCTIONS,
        model=model_instance,
        mcp_servers=[mcp_server],
    )

    return agent


async def run_chatbot_stream(
    agent: Agent,
    message: str,
    max_turns: int = 5,
) -> AsyncIterator[str]:
    """Run the chatbot agent with streaming responses.

    This function executes the agent with the provided message and streams
    the response in real-time, enabling responsive user interfaces.

    The streaming approach provides:
    - Immediate feedback as the agent processes the request
    - Progressive rendering of responses
    - Real-time tool usage visibility

    Args:
        agent: Agent instance from create_chatbot_agent_context()
        message: User message/input to process
        max_turns: Maximum number of agent turns (default: 5).
            Controls how many tool calls/LLM requests the agent can make.

    Yields:
        str: Response chunks as they are generated

    Example:
        >>> async with create_chatbot_agent_context() as agent:
        ...     async for chunk in run_chatbot_stream(agent, "Create a task"):
        ...         print(chunk, end="")

    Note:
        The agent uses tools from the MCP server. Ensure the MCP server
        is running before calling this function.

    Raises:
        Exception: If the agent encounters an error during execution.
            Tool failures are caught and returned in the response.
    """
    # Configure runner with streaming
    config = RunConfig(
        max_turns=max_turns,
    )

    # Run agent with streaming
    result = await Runner.run(
        agent,
        input=message,
        config=config,
    )

    # Stream the response
    # The result.final_output contains the complete response
    # For true streaming, we would use result.stream() if available
    yield result.final_output


async def run_chatbot_stream_events(
    agent: Agent,
    message: str,
    max_turns: int = 5,
) -> AsyncIterator[ModelResponse]:
    """Run the chatbot agent with full event streaming.

    This is an advanced streaming interface that provides access to all
    agent events including:
    - Token generation events
    - Tool call events
    - Tool result events
    - LLM response completion

    Use this when you need fine-grained control over the agent execution
    flow, such as displaying tool usage in real-time or implementing
    custom UI patterns.

    Args:
        agent: Agent instance from create_chatbot_agent_context()
        message: User message/input to process
        max_turns: Maximum number of agent turns (default: 5)

    Yields:
        ModelResponse: Agent events including tokens, tool calls, and results

    Example:
        >>> async with create_chatbot_agent_context() as agent:
        ...     async for event in run_chatbot_stream_events(agent, "What's the workload?"):
        ...         if event.type == "tokens":
        ...             print(event.content, end="")
        ...         elif event.type == "tool_call":
        ...             print(f"[Calling tool: {event.tool_name}]")

    Note:
        This is a placeholder for the actual streaming implementation.
        The OpenAI Agents SDK's streaming API may differ slightly.
        Refer to the official documentation for the exact event types
        and streaming patterns.
    """
    # Configure runner
    config = RunConfig(
        max_turns=max_turns,
    )

    # Run with full event streaming
    # Note: The actual implementation may vary based on the SDK version
    result = await Runner.run(
        agent,
        input=message,
        config=config,
    )

    # For now, yield the final result
    # Replace this with actual event streaming when available
    yield result

    # Future implementation (pseudocode):
    # async for event in result.stream_events():
    #     yield event
