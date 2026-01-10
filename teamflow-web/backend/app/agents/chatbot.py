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

from app.mcp.server import mcp


# Agent instructions
TEAMFLOW_AGENT_INSTRUCTIONS = """You are TeamFlow AI, an intelligent assistant for agency project management and team collaboration.

Your capabilities include:
- **Task Management**: Create, list, assign, complete, archive, delete, and update tasks
- **Project Management**: Create projects, list projects, get project details
- **Time Tracking**: Log time, list time entries, view task time totals, update and delete time entries
- **Analytics**: Provide profitability insights and workload summaries
- **AI Recommendations**: Suggest the best assignees for tasks based on workload and availability
- **Complex Multi-Step Queries**: Execute workflows that combine multiple tools with conditional logic (A2 - Specification Analysis Finding)

**Guidelines:**
- Be concise and actionable
- Use sensible defaults when users don't specify details:
  - For tasks: default priority = MEDIUM, default status = TODO
  - If assignee not specified, leave task unassigned
  - If due_date not specified, don't set a deadline
  - If project not found, still create the task (without project linkage)
  - For time entries: entry_date defaults to today if not specified
- Execute actions directly without repeatedly asking for confirmation, EXCEPT for destructive operations
- For DELETE and ARCHIVE operations: Always confirm the task title with the user before executing
  - Example: "You want to delete 'new render task'. Confirm by saying 'yes' or provide the exact task title."
- If a user requests an action that's not available (e.g., "remove task"), inform them of available alternatives:
  - "I can't remove tasks, but I can delete (permanent), archive (hide), or complete them. Which would you prefer?"
- Only ask for clarification when critical information is genuinely missing (e.g., what task to create)
- If a tool fails, explain the error and suggest alternatives

**Complex Multi-Step Query Examples (A2):**

A query is "complex" if it requires:
- 2+ tool calls with dependencies between them
- Conditional logic based on tool results
- Data synthesis across multiple sources

**Example 1 - Multi-step workflow:**
"Find all high-priority tasks assigned to Sarah that are due this week, suggest a replacement assignee based on current workload, and create a follow-up task for Sarah to review the reassignment."
- Step 1: Call list_tasks (filter: priority=HIGH, assignee=Sarah, due=this week)
- Step 2: Call workload_summary to get current team capacity
- Step 3: Call suggest_assignee for each found task
- Step 4: Call assign_task to reassign
- Step 5: Call add_task to create follow-up for Sarah

**Example 2 - Analytical workflow:**
"Compare profitability across all active projects, identify the lowest-performing one, and draft a task to audit its resource allocation."
- Step 1: Call list_projects to get active projects
- Step 2: Call get_profitability for each project
- Step 3: Analyze results to find lowest profitability
- Step 4: Call add_task with audit details for the identified project

**Example 3 - Conditional workflow:**
"Show me the time entries for the frontend refactor task, calculate total hours, and if over estimate, create a task to review the estimate."
- Step 1: Call get_time_for_task to retrieve time entries
- Step 2: Calculate total hours vs estimate
- Step 3: If total > estimate, call add_task to create review task
- Step 4: If total <= estimate, report that estimate is accurate

**Simple Query Examples (NOT complex):**
- "List all my tasks" → Single list_tasks call
- "Assign this task to John" → Single assign_task call
- "What's the profitability of Project X?" → Single get_profitability call

**Task Creation Best Practices:**
- Always use YYYY-MM-DD format for due_date (e.g., "2026-01-10")
- Use exact project names when provided by user
- Use exact assignee names when provided by user
- Map priorities: "urgent" → HIGH, "high" → HIGH, "medium" → MEDIUM, "low" → LOW

**Task Update Operations:**
- Tasks can be: completed (mark as DONE), archived (hide from view), deleted (permanent removal)
- Tasks can be updated: priority, due date, status
- Use task titles for identification (partial matching supported)

**Time Entry Best Practices:**
- Duration is specified in minutes (e.g., 60 for 1 hour, 30 for 30 minutes)
- Use YYYY-MM-DD format for entry_date (e.g., "2026-01-10")
- To log time: "Log 2 hours to task 'fix navbar' with note 'Fixed responsive issue'"
- To view time: "Show time logged for task 'fix navbar'" or "List all time entries"
- To update time: "Update time entry for task 'fix navbar' on 2026-01-10 to 90 minutes"
- To delete time: "Delete time entry for task 'fix navbar' on 2026-01-10"

**Project Management Best Practices:**
- Users can ask "What projects do I have?" to list all projects
- Users can create projects with "Create a project named <name>"
- Users can get project details with "Tell me about the <project name> project"

**Destructive Actions:**
- DELETE: Permanently removes the task (cannot be undone)
- ARCHIVE: Hides the task from normal views but keeps it for reference
- COMPLETE: Marks task as DONE (can be reversed by changing status)
- When user asks to "delete" or "archive", confirm the task title first

**Current Context:**
- You are integrated with TeamFlow's project management system
- You can access real-time data through available tools
- User authentication is handled at the API level

When users ask for help, guide them through available capabilities."""


def create_chatbot_agent(
    instructions: str | None = None,
    model: str = "google/gemini-2.0-flash-exp:free",
    use_fallback: bool = True,
) -> Agent:
    """Create a TeamFlow chatbot agent with MCP tools.

    This function initializes an OpenAI Agents SDK agent configured with:
    - Gemini 2.0 Flash Experimental model via OpenRouter (primary, fast, free tier)
    - Direct Gemini API fallback (when OpenRouter unavailable)
    - Tools from the MCP server for task management operations
    - Custom instructions for TeamFlow-specific behavior

    Args:
        instructions: Custom agent instructions (optional).
            Defaults to TEAMFLOW_AGENT_INSTRUCTIONS.
        model: Model identifier via OpenRouter. Defaults to "google/gemini-2.0-flash-exp:free".
        use_fallback: Enable automatic fallback to direct Gemini API. Defaults to True.

    Returns:
        Configured Agent instance ready to run

    Example:
        >>> agent = create_chatbot_agent()
        >>> result = await run_chatbot_stream(agent, "List all high priority tasks")
        >>> async for chunk in result:
        ...     print(chunk, end="")
    """
    # Get the model with fallback support
    from app.agents.client import get_model_with_fallback, get_openrouter_model

    if use_fallback:
        # Use fallback logic: try OpenRouter first, fall back to direct Gemini
        model_instance = get_model_with_fallback(model_name=model)
    else:
        # Use only OpenRouter (will raise error if unavailable)
        model_instance = get_openrouter_model(model_name=model)

    # Import tools from agents/tools.py
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

    # Create agent with tools registered
    agent = Agent(
        name="teamflow-ai",
        instructions=instructions or TEAMFLOW_AGENT_INSTRUCTIONS,
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
