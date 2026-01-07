# TeamFlow AI Chatbot Agent

OpenAI Agents SDK integration with Gemini 2.0 Flash model for TeamFlow AI Chatbot.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            /app/agents/                               │   │
│  │                                                         │   │
│  │  ┌─────────────────┐      ┌────────────────────┐     │   │
│  │  │   client.py     │      │    chatbot.py      │     │   │
│  │  │                 │      │                    │     │   │
│  │  │ - AsyncOpenAI   │─────>│ - Agent creation   │     │   │
│  │  │ - Gemini config │      │ - Streaming runner │     │   │
│  │  │ - Singleton     │      │ - Tool injection   │     │   │
│  │  └─────────────────┘      └────────────────────┘     │   │
│  │           │                           │               │   │
│  └───────────┼───────────────────────────┼───────────────┘   │
│              │                           │                   │
│              v                           v                   │
│  ┌─────────────────────┐    ┌──────────────────────┐        │
│  │   Gemini API        │    │   MCP Server         │        │
│  │   (OpenAI-compatible│    │   (/app/mcp/)        │        │
│  │    endpoint)        │    │                      │        │
│  │                     │    │ - add_task           │        │
│  │ - gemini-2.0-flash  │    │ - list_tasks         │        │
│  │ - Streaming         │    │ - assign_task        │        │
│  └─────────────────────┘    │ - complete_task      │        │
│                              │ - get_profitability  │        │
│                              │ - workload_summary   │        │
│                              └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# Gemini API Key (required)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API Key (for embeddings, optional)
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant (for RAG, optional)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key
```

### Client Configuration

The AsyncOpenAI client is configured in `/app/agents/client.py`:

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client
from app.core.config import settings

client = AsyncOpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/",
    api_key=settings.gemini_api_key,
)

set_default_openai_client(client, use_for_tracing=True)
```

## Usage

### Basic Agent Creation

```python
from app.agents import create_chatbot_agent, run_chatbot_stream

# Create agent
agent = create_chatbot_agent()

# Run with streaming
async for chunk in run_chatbot_stream(agent, "List all high priority tasks"):
    print(chunk, end="")
```

### Custom Instructions

```python
agent = create_chatbot_agent(
    instructions="You are a project management expert focused on agile methodologies.",
    model="gemini-2.0-flash-exp"
)
```

### Full Example with Error Handling

```python
import asyncio
from app.agents import create_chatbot_agent, run_chatbot_stream

async def chat():
    try:
        agent = create_chatbot_agent()

        async for chunk in run_chatbot_stream(
            agent,
            "Create a task for API integration"
        ):
            print(chunk, end="")

    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Agent error: {e}")

asyncio.run(chat())
```

## Available Models

The agent supports these Gemini models via OpenAI-compatible endpoint:

- `gemini-2.0-flash-exp` (default) - Fast, efficient for most tasks
- `gemini-2.0-flash-thinking-exp` - Enhanced reasoning
- `gemini-exp-1206` - Latest experimental model

## MCP Tools Integration

The agent has access to these tools from the MCP server:

### Task Management (T018)
- `add_task` - Create new tasks
- `list_tasks` - List tasks with filters
- `assign_task` - Reassign tasks
- `complete_task` - Mark tasks complete

### Analytics (T019)
- `get_profitability` - Project profitability analysis
- `workload_summary` - Team workload overview

### AI Recommendations (T020)
- `suggest_assignee` - AI-powered assignee suggestions

## API Integration

### FastAPI Endpoint Example

```python
from fastapi import APIRouter, HTTPException
from app.agents import create_chatbot_agent, run_chatbot_stream

router = APIRouter()

@router.post("/chat")
async def chat(message: str):
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

### Streaming Endpoint (Server-Sent Events)

```python
from fastapi import Response
from fastapi.responses import StreamingResponse

@router.get("/chat/stream")
async def chat_stream(message: str):
    """Stream chat responses via SSE."""
    agent = create_chatbot_agent()

    async def generate():
        async for chunk in run_chatbot_stream(agent, message):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## Testing

Run the example script:

```bash
cd /mnt/d/GIAIC/Quarter 4/Hackathon II/teamflow-web/backend
python -m app.agents.example
```

## Troubleshooting

### Common Issues

**1. API Key Not Found**
```
ValueError: GEMINI_API_KEY is not set
```
Solution: Set `GEMINI_API_KEY` in `.env` file

**2. Import Errors**
```
ModuleNotFoundError: No module named 'agents'
```
Solution: Install dependencies: `uv sync`

**3. Connection Errors**
```
openai.APIConnectionError: Connection error
```
Solution: Check internet connection and Gemini API status

## Dependencies

Required packages (from `pyproject.toml`):

```toml
"openai>=1.60.0",           # AsyncOpenAI client
"openai-agents>=0.1.0",     # OpenAI Agents SDK
"mcp>=0.1.0",               # MCP Python SDK
"python-dotenv>=1.0.0",     # Environment loading
```

## References

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [MCP Protocol](https://modelcontextprotocol.io/)
