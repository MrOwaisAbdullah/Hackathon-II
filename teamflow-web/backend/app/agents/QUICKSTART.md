# TeamFlow AI Chatbot - Quick Start Guide

This guide will help you get the TeamFlow AI Chatbot agent running with Gemini 2.0 Flash model in under 5 minutes.

## Prerequisites

- Python 3.13+
- Gemini API key (get one at https://ai.google.dev/)
- Git clone of the TeamFlow repository

## Step 1: Install Dependencies

```bash
cd /mnt/d/GIAIC/Quarter 4/Hackathon II/teamflow-web/backend
uv sync
```

This installs:
- `openai>=1.60.0` - AsyncOpenAI client
- `openai-agents>=0.1.0` - OpenAI Agents SDK
- `mcp>=0.1.0` - MCP Python SDK

## Step 2: Configure Environment

Create or edit `.env` file in the backend directory:

```bash
# Required: Gemini API Key
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional: OpenAI API Key (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Qdrant (for RAG)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key
```

**Get Gemini API Key:**
1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create a new project or select existing
4. Copy the API key

## Step 3: Validate Implementation

```bash
python -m app.agents.validate
```

Expected output:
```
============================================================
TeamFlow AI Chatbot - Implementation Validation
============================================================
...
✓ All syntax checks passed!
============================================================
```

## Step 4: Run Example

```bash
python -m app.agents.example
```

This will:
1. Initialize the agent with Gemini 2.0 Flash
2. Run example interactions
3. Start interactive mode

Example output:
```
============================================================
TeamFlow AI Chatbot - Example Usage
============================================================

Initializing TeamFlow AI agent...
Agent ready!

------------------------------------------------------------
Example 1: Simple greeting
------------------------------------------------------------
User: Hello!
Agent: Hello! I'm TeamFlow AI, your intelligent assistant for
agency project management. How can I help you today?
```

## Step 5: Integrate with Your API

### Basic Endpoint

```python
from fastapi import APIRouter
from app.agents import create_chatbot_agent, run_chatbot_stream

router = APIRouter()

@router.post("/api/v1/chat")
async def chat(message: str):
    """Chat with TeamFlow AI."""
    agent = create_chatbot_agent()

    response_chunks = []
    async for chunk in run_chatbot_stream(agent, message):
        response_chunks.append(chunk)

    return {"response": "".join(response_chunks)}
```

### Streaming Endpoint (SSE)

```python
from fastapi.responses import StreamingResponse

@router.get("/api/v1/chat/stream")
async def chat_stream(message: str):
    """Stream chat responses via Server-Sent Events."""
    agent = create_chatbot_agent()

    async def generate():
        async for chunk in run_chatbot_stream(agent, message):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Available Agent Capabilities

The agent has access to these tools:

### Task Management
- **Create tasks**: "Add a task for fixing the navbar bug"
- **List tasks**: "Show me all high priority tasks"
- **Assign tasks**: "Assign the API task to John"
- **Complete tasks**: "Mark task #123 as complete"

### Analytics
- **Profitability**: "What's the profit margin for Project X?"
- **Workload**: "Show me the team's workload summary"

### AI Recommendations
- **Suggest assignee**: "Who should handle the database migration?"

## Customization

### Change Model

```python
agent = create_chatbot_agent(model="gemini-2.0-flash-thinking-exp")
```

Available models:
- `gemini-2.0-flash-exp` (default, fastest)
- `gemini-2.0-flash-thinking-exp` (enhanced reasoning)
- `gemini-exp-1206` (latest experimental)

### Custom Instructions

```python
agent = create_chatbot_agent(
    instructions="You are an agile project management expert. "
                 "Focus on sprint planning and velocity tracking."
)
```

### Adjust Max Turns

```python
async for chunk in run_chatbot_stream(agent, message, max_turns=10):
    print(chunk)
```

## Troubleshooting

### Error: `GEMINI_API_KEY is not set`

**Solution:** Add `GEMINI_API_KEY=...` to `.env` file

### Error: `ModuleNotFoundError: No module named 'agents'`

**Solution:** Run `uv sync` to install dependencies

### Error: `openai.APIConnectionError`

**Solution:** Check internet connection and Gemini API status

### Error: `ImportError: cannot import name 'Agent'`

**Solution:** Ensure `openai-agents>=0.1.0` is installed:
```bash
uv pip install --upgrade "openai-agents>=0.1.0"
```

## Architecture Overview

```
User Request
    ↓
FastAPI Endpoint
    ↓
Agent (create_chatbot_agent)
    ↓
OpenAI Agents SDK (Runner)
    ↓
Gemini API (OpenAI-compatible endpoint)
    ↓
MCP Tools (Task Management, Analytics, Recommendations)
    ↓
Response Stream
```

## Next Steps

1. **Implement MCP Tools**: Complete the tool implementations in `/app/mcp/tools.py`
2. **Add RAG**: Integrate Qdrant for knowledge base queries
3. **Add Auth**: Integrate with Better Auth for user-specific responses
4. **Add Monitoring**: Implement logging and metrics
5. **Deploy**: Deploy to production with proper error handling

## Reference Documentation

- Full README: `/app/agents/README.md`
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
- Gemini API: https://ai.google.dev/gemini-api/docs
- MCP Protocol: https://modelcontextprotocol.io/

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `/app/agents/README.md`
3. Check the example code in `/app/agents/example.py`
4. Run validation: `python -m app.agents.validate`
