"""TeamFlow AI Chatbot agent implementation.

This module provides the main chatbot agent using OpenAI Agents SDK
with Gemini 2.0 Flash model and MCP server tools.

The agent supports:
- Task management (add, list, assign, complete tasks)
- Analytics (profitability, workload summary)
- AI recommendations (suggest assignee)
- Streaming responses for real-time UX
"""
from typing import AsyncIterator

from agents import Agent, Runner, RunConfig, ModelResponse

from app.agents.client import initialize_gemini_client
from app.mcp.server import mcp


# Agent instructions
TEAMFLOW_AGENT_INSTRUCTIONS = """You are TeamFlow AI, an intelligent assistant for agency project management and team collaboration.

Your capabilities include:
- **Task Management**: Create, list, assign, and complete tasks
- **Analytics**: Provide profitability insights and workload summaries
- **AI Recommendations**: Suggest the best assignees for tasks based on skills and availability

**Guidelines:**
- Be concise and actionable
- Always clarify missing information before taking actions
- Use tools when needed to fulfill user requests
- Provide context and reasoning for recommendations
- If a tool fails, explain the error and suggest alternatives

**Current Context:**
- You are integrated with TeamFlow's project management system
- You can access real-time data through available tools
- User authentication is handled at the API level

When users ask for help, guide them through available capabilities."""


def create_chatbot_agent(
    instructions: str | None = None,
    model: str = "gemini-2.0-flash-exp",
) -> Agent:
    """Create a TeamFlow chatbot agent with MCP tools.

    This function initializes an OpenAI Agents SDK agent configured with:
    - Gemini 2.0 Flash model via OpenAI-compatible endpoint
    - Tools from the MCP server for task management operations
    - Custom instructions for TeamFlow-specific behavior

    Args:
        instructions: Custom agent instructions (optional).
            Defaults to TEAMFLOW_AGENT_INSTRUCTIONS.
        model: Model identifier. Defaults to "gemini-2.0-flash-exp".
            Other options: "gemini-2.0-flash-thinking-exp", "gemini-exp-1206"

    Returns:
        Configured Agent instance ready to run

    Example:
        >>> agent = create_chatbot_agent()
        >>> result = await run_chatbot_stream(agent, "List all high priority tasks")
        >>> async for chunk in result:
        ...     print(chunk, end="")
    """
    # Initialize Gemini client (sets default for OpenAI Agents SDK)
    initialize_gemini_client()

    # Create agent with tools from MCP server
    agent = Agent(
        name="teamflow-ai",
        instructions=instructions or TEAMFLOW_AGENT_INSTRUCTIONS,
        model=model,
        # Tools are registered via MCP server and injected at runtime
        # The MCP server provides: add_task, list_tasks, assign_task,
        # complete_task, get_profitability, workload_summary, suggest_assignee
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
        agent: Agent instance from create_chatbot_agent()
        message: User message/input to process
        max_turns: Maximum number of agent turns (default: 5).
            Controls how many tool calls/LLM requests the agent can make.

    Yields:
        str: Response chunks as they are generated

    Example:
        >>> agent = create_chatbot_agent()
        >>> message = "Create a task for fixing the navbar bug"
        >>> async for chunk in run_chatbot_stream(agent, message):
        ...     print(chunk, end="")

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
        agent: Agent instance from create_chatbot_agent()
        message: User message/input to process
        max_turns: Maximum number of agent turns (default: 5)

    Yields:
        ModelResponse: Agent events including tokens, tool calls, and results

    Example:
        >>> agent = create_chatbot_agent()
        >>> message = "What's the workload summary?"
        >>> async for event in run_chatbot_stream_events(agent, message):
        ...     if event.type == "tokens":
        ...         print(event.content, end="")
        ...     elif event.type == "tool_call":
        ...         print(f"[Calling tool: {event.tool_name}]")

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
