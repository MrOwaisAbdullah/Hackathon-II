# TeamFlow AI Chatbot Agent - API Reference

Complete API reference for the TeamFlow AI Chatbot agent implementation.

## Table of Contents

- [Module: `app.agents.client`](#module-appagentsclient)
- [Module: `app.agents.chatbot`](#module-appagentschatbot)
- [Module: `app.agents`](#module-appagents)
- [Type Definitions](#type-definitions)
- [Examples](#examples)

---

## Module: `app.agents.client`

Gemini AsyncOpenAI client configuration and initialization.

### Functions

#### `initialize_gemini_client()`

Initialize and configure AsyncOpenAI client for Gemini.

**Returns:** `AsyncOpenAI`

**Raises:** `ValueError` - If GEMINI_API_KEY is not configured

**Example:**
```python
from app.agents.client import initialize_gemini_client

client = initialize_gemini_client()
response = await client.chat.completions.create(
    model="gemini-2.0-flash-exp",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Configuration:**
- Base URL: `https://generativelanguage.googleapis.com/v1beta/`
- API Key: Retrieved from `settings.gemini_api_key`
- Singleton pattern: Client created once and reused

---

#### `get_gemini_client()`

Get or initialize the Gemini AsyncOpenAI client (singleton pattern).

**Returns:** `AsyncOpenAI`

**Raises:** `ValueError` - If GEMINI_API_KEY is not configured

**Example:**
```python
from app.agents.client import get_gemini_client

client = get_gemini_client()
# Use client for API calls
```

---

## Module: `app.agents.chatbot`

TeamFlow AI Chatbot agent implementation.

### Constants

#### `TEAMFLOW_AGENT_INSTRUCTIONS`

Default instructions for the TeamFlow AI agent.

**Type:** `str`

**Default Value:**
```python
"""You are TeamFlow AI, an intelligent assistant for agency project
management and team collaboration.

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
"""
```

---

### Functions

#### `create_chatbot_agent()`

Create a TeamFlow chatbot agent with MCP tools.

**Parameters:**
- `instructions` (`str | None`) - Custom agent instructions. Defaults to `TEAMFLOW_AGENT_INSTRUCTIONS`
- `model` (`str`) - Model identifier. Defaults to `"gemini-2.0-flash-exp"`

**Returns:** `Agent` - Configured Agent instance ready to run

**Available Models:**
- `"gemini-2.0-flash-exp"` (default) - Fast, efficient for most tasks
- `"gemini-2.0-flash-thinking-exp"` - Enhanced reasoning
- `"gemini-exp-1206"` - Latest experimental model

**Example:**
```python
from app.agents import create_chatbot_agent

# Default configuration
agent = create_chatbot_agent()

# Custom instructions
agent = create_chatbot_agent(
    instructions="You are an agile project management expert."
)

# Different model
agent = create_chatbot_agent(model="gemini-2.0-flash-thinking-exp")
```

---

#### `run_chatbot_stream()`

Run the chatbot agent with streaming responses.

**Parameters:**
- `agent` (`Agent`) - Agent instance from `create_chatbot_agent()`
- `message` (`str`) - User message/input to process
- `max_turns` (`int`) - Maximum number of agent turns (default: `5`)

**Yields:** `str` - Response chunks as they are generated

**Example:**
```python
from app.agents import create_chatbot_agent, run_chatbot_stream

agent = create_chatbot_agent()
message = "Create a task for fixing the navbar bug"

async for chunk in run_chatbot_stream(agent, message):
    print(chunk, end="")
```

**Streaming Behavior:**
- Provides immediate feedback as the agent processes requests
- Progressive rendering of responses
- Real-time tool usage visibility
- Continues until agent completes or max_turns reached

---

#### `run_chatbot_stream_events()`

Run the chatbot agent with full event streaming (advanced).

**Parameters:**
- `agent` (`Agent`) - Agent instance from `create_chatbot_agent()`
- `message` (`str`) - User message/input to process
- `max_turns` (`int`) - Maximum number of agent turns (default: `5`)

**Yields:** `ModelResponse` - Agent events including tokens, tool calls, and results

**Example:**
```python
from app.agents import create_chatbot_agent, run_chatbot_stream_events

agent = create_chatbot_agent()
message = "What's the workload summary?"

async for event in run_chatbot_stream_events(agent, message):
    if event.type == "tokens":
        print(event.content, end="")
    elif event.type == "tool_call":
        print(f"[Calling tool: {event.tool_name}]")
```

**Note:** This is a placeholder for the actual streaming implementation. The OpenAI Agents SDK's streaming API may differ slightly.

---

## Module: `app.agents`

Package exports for convenient importing.

### Exports

```python
from app.agents.client import get_gemini_client, initialize_gemini_client
from app.agents.chatbot import create_chatbot_agent, run_chatbot_stream
```

### Usage

```python
# Import all at once
from app.agents import (
    get_gemini_client,
    initialize_gemini_client,
    create_chatbot_agent,
    run_chatbot_stream,
)

# Use imports
agent = create_chatbot_agent()
async for chunk in run_chatbot_stream(agent, "Hello!"):
    print(chunk)
```

---

## Type Definitions

### `Agent`

OpenAI Agents SDK Agent instance.

**Source:** `agents.Agent`

**Methods:**
- Tool invocation via MCP server
- Handoffs to other agents (future)
- Context management
- Instruction following

---

### `AsyncOpenAI`

OpenAI Python SDK async client.

**Source:** `openai.AsyncOpenAI`

**Configuration:**
- Base URL: Custom Gemini endpoint
- API Key: From environment
- HTTP Client: httpx-based async client

---

### `AsyncIterator[str]`

Async iterator yielding string chunks.

**Used by:** `run_chatbot_stream()`

**Example:**
```python
async def process_stream(iterator: AsyncIterator[str]) -> str:
    result = ""
    async for chunk in iterator:
        result += chunk
    return result
```

---

### `ModelResponse`

Agent response event from streaming.

**Source:** `agents.ModelResponse`

**Properties:**
- `type` - Event type (tokens, tool_call, tool_result, etc.)
- `content` - Response content
- `tool_name` - Tool being called (if applicable)
- `tool_result` - Tool execution result (if applicable)

---

## Examples

### Basic Chat

```python
import asyncio
from app.agents import create_chatbot_agent, run_chatbot_stream

async def main():
    agent = create_chatbot_agent()

    async for chunk in run_chatbot_stream(agent, "Hello!"):
        print(chunk, end="")

    print()  # New line

asyncio.run(main())
```

### Task Management

```python
async def create_task():
    agent = create_chatbot_agent()

    message = """
    Create a task for fixing the navbar responsive bug.
    Set priority to HIGH and assign it to the frontend team.
    """

    async for chunk in run_chatbot_stream(agent, message):
        print(chunk, end="")
```

### Analytics Query

```python
async def get_profitability():
    agent = create_chatbot_agent()

    message = """
    Can you get the profitability analysis for project XYZ?
    I need to see revenue, costs, and profit margins.
    """

    async for chunk in run_chatbot_stream(agent, message):
        print(chunk, end="")
```

### FastAPI Integration

```python
from fastapi import APIRouter, HTTPException
from app.agents import create_chatbot_agent, run_chatbot_stream

router = APIRouter()

@router.post("/api/v1/chat")
async def chat_endpoint(message: str):
    """Chat with TeamFlow AI."""
    try:
        agent = create_chatbot_agent()

        response_chunks = []
        async for chunk in run_chatbot_stream(agent, message):
            response_chunks.append(chunk)

        return {"response": "".join(response_chunks)}

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Streaming with SSE

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.agents import create_chatbot_agent, run_chatbot_stream

router = APIRouter()

@router.get("/api/v1/chat/stream")
async def chat_stream_endpoint(message: str):
    """Stream chat responses via Server-Sent Events."""
    agent = create_chatbot_agent()

    async def generate():
        async for chunk in run_chatbot_stream(agent, message):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

### Custom Configuration

```python
from app.agents import create_chatbot_agent, run_chatbot_stream

# Custom instructions
custom_instructions = """
You are an agile project management expert.
Focus on sprint planning, velocity tracking, and burndown charts.
Always provide actionable metrics.
"""

agent = create_chatbot_agent(
    instructions=custom_instructions,
    model="gemini-2.0-flash-thinking-exp"
)

async for chunk in run_chatbot_stream(agent, "Analyze our sprint velocity"):
    print(chunk, end="")
```

### Error Handling

```python
import asyncio
from app.agents import create_chatbot_agent, run_chatbot_stream

async def safe_chat(message: str):
    """Chat with comprehensive error handling."""
    try:
        agent = create_chatbot_agent()

        response_chunks = []
        async for chunk in run_chatbot_stream(agent, message):
            response_chunks.append(chunk)

        return "".join(response_chunks)

    except ValueError as e:
        # Configuration error (e.g., missing API key)
        return f"Configuration error: {e}"

    except Exception as e:
        # Agent execution error
        return f"Agent error: {e}"

# Usage
response = asyncio.run(safe_chat("Hello!"))
print(response)
```

---

## MCP Tools Reference

The agent has access to these tools from the MCP server:

### Task Management Tools

#### `add_task`

Create a new task in TeamFlow.

**Parameters:**
- `title` (str) - Task title
- `description` (str, optional) - Task description
- `project_id` (str, optional) - Project ID
- `assignee_id` (str, optional) - User ID to assign
- `priority` (str, optional) - Priority: LOW, MEDIUM, HIGH
- `status` (str, optional) - Status: TODO, DOING, REVIEW, DONE

**Returns:** Confirmation message with task ID

#### `list_tasks`

List tasks with optional filters.

**Parameters:**
- `project_id` (str, optional) - Filter by project
- `assignee_id` (str, optional) - Filter by assignee
- `status` (str, optional) - Filter by status
- `limit` (int) - Max tasks to return (default: 50)

**Returns:** List of tasks with details

#### `assign_task`

Assign a task to a user.

**Parameters:**
- `task_id` (str) - Task ID to reassign
- `assignee_id` (str) - User ID to assign to

**Returns:** Confirmation with new assignment

#### `complete_task`

Mark a task as complete.

**Parameters:**
- `task_id` (str) - Task ID to complete

**Returns:** Confirmation message

### Analytics Tools

#### `get_profitability`

Get profitability analysis for a project.

**Parameters:**
- `project_id` (str) - Project ID to analyze

**Returns:** Profitability metrics (revenue, cost, profit, margin)

#### `workload_summary`

Get workload summary for an agency.

**Parameters:**
- `agency_id` (str) - Agency ID to analyze

**Returns:** Workload summary with team utilization

### AI Recommendation Tools

#### `suggest_assignee`

Suggest the best assignee for a task.

**Parameters:**
- `task_id` (str) - Task ID to find assignee for

**Returns:** Recommended assignee with reasoning

---

## Error Handling

### Common Exceptions

#### `ValueError: GEMINI_API_KEY is not set`

**Cause:** API key not configured in environment

**Solution:** Set `GEMINI_API_KEY` in `.env` file

```python
# .env
GEMINI_API_KEY=your_actual_api_key_here
```

#### `ModuleNotFoundError: No module named 'agents'`

**Cause:** OpenAI Agents SDK not installed

**Solution:** Install dependencies

```bash
uv sync
```

#### `openai.APIConnectionError`

**Cause:** Connection to Gemini API failed

**Solution:** Check internet connection and API status

---

## Best Practices

### 1. Always Use Async

```python
# Good
async for chunk in run_chatbot_stream(agent, message):
    print(chunk)

# Bad (will block)
response = await run_chatbot_stream(agent, message).asend(None)
```

### 2. Handle Errors Gracefully

```python
try:
    agent = create_chatbot_agent()
    async for chunk in run_chatbot_stream(agent, message):
        print(chunk)
except ValueError as e:
    logger.error(f"Config error: {e}")
except Exception as e:
    logger.error(f"Agent error: {e}")
```

### 3. Use Streaming for UX

```python
# Good: Streaming provides immediate feedback
async for chunk in run_chatbot_stream(agent, message):
    print(chunk, end="", flush=True)

# Avoid: Waiting for complete response blocks UI
response = await run_chatbot_stream(agent, message)
```

### 4. Configure Max Turns Appropriately

```python
# Simple tasks: fewer turns
async for chunk in run_chatbot_stream(agent, "Hello!", max_turns=2):
    print(chunk)

# Complex tasks: more turns
async for chunk in run_chatbot_stream(
    agent,
    "Analyze project profitability and suggest improvements",
    max_turns=10
):
    print(chunk)
```

### 5. Customize Instructions for Context

```python
# Generic agent
agent = create_chatbot_agent()

# Context-specific agent
agent = create_chatbot_agent(
    instructions="You are a senior project manager focusing on risk mitigation."
)
```

---

## Performance Considerations

### Client Reuse

The client uses singleton pattern - it's created once and reused:

```python
from app.agents import get_gemini_client

# First call: creates client
client1 = get_gemini_client()

# Subsequent calls: reuses client
client2 = get_gemini_client()

assert client1 is client2  # True
```

### Streaming Efficiency

Streaming is more efficient than waiting for complete responses:

- **Lower latency**: First chunk arrives quickly
- **Better UX**: Progressive rendering
- **Memory efficient**: No need to buffer complete response

### Model Selection

Choose models based on task complexity:

```python
# Simple tasks: use faster model
agent = create_chatbot_agent(model="gemini-2.0-flash-exp")

# Complex reasoning: use thinking model
agent = create_chatbot_agent(model="gemini-2.0-flash-thinking-exp")
```

---

## References

- [OpenAI Agents SDK Documentation](https://github.com/openai/openai-agents-python)
- [OpenAI Python SDK Documentation](https://github.com/openai/openai-python)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
