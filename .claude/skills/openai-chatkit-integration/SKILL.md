---
name: openai-chatkit-integration
description: Implement OpenAI ChatKit with a custom backend using Python (FastAPI), OpenAI Agents SDK, and alternative LLMs (Gemini/OpenRouter/Ollama). This skill provides production-ready templates and battle-tested patterns learned from real-world integration issues.
---

# OpenAI ChatKit Integration (Custom Backend)

## Overview

This skill guides you through implementing a **production-ready** custom backend for OpenAI ChatKit, based on real-world debugging and integration experience. It bypasses OpenAI's hosted services to use alternative LLMs and custom tool integration.

**Key Components:**
- **Frontend**: `@openai/chatkit-react` (React/Next.js)
- **Backend**: FastAPI + `openai-chatkit` (Python SDK)
- **Agent Framework**: OpenAI Agents SDK with custom LLM providers
- **Storage**: Custom Store implementation (in-memory or database)

## Required Clarifications

Before generating code, ask:
1. **LLM Provider**: "Which LLM provider will you use? (Gemini, OpenRouter, Local/Ollama, OpenAI?)"
2. **Storage**: "Do you need persistent chat history? (PostgreSQL, MongoDB, or in-memory for testing?)"
3. **Frontend Framework**: "Are you using Next.js (App Router or Pages Router) or pure React?"
4. **Tools/RAG**: "Do you need MCP tool integration or RAG knowledge base?"

## Pre-flight Checklist

### Must Have
- [ ] **API Keys**: LLM provider key (OpenRouter/Gemini/OpenAI)
- [ ] **Python 3.13+**: For modern type hints and async features
- [ ] **Node.js 20+**: For ChatKit React frontend
- [ ] **Dependency Manager**: `uv` recommended for Python, `npm`/`pnpm` for Node

### Must Avoid
- [ ] **clientSecret**: Do NOT use `clientSecret` in frontend; use custom `api.url`
- [ ] **Wrong imports**: Use `from chatkit.*` not `from openai_chatkit.*`
- [ ] **litellm prefix**: Do NOT use `litellm/openrouter/...` model names
- [ ] **Direct model strings**: Wrap clients with `OpenAIChatCompletionsModel`

## Implementation Guide

See **`assets/IMPLEMENTATION_GUIDE.md`** for the complete step-by-step guide with code examples.

## Quick Start

### 1. Backend Setup (FastAPI + ChatKit Python SDK)

```bash
# Install dependencies
cd backend
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
uv run uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup (ChatKit React)

```bash
# Install ChatKit React
npm install @openai/chatkit-react

# Configure ChatKit provider (see assets/frontend/ChatPage.tsx)
npm run dev
```

## Common Pitfalls & Solutions

### ❌ Pitfall #1: Wrong ChatKit SDK Imports

**Problem:**
```python
# WRONG - These imports don't exist or are outdated
from openai_chatkit import ChatKitServer
from chatkit_sdk import Server
```

**Solution:**
```python
# CORRECT
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import Store, Page, ThreadItem
from chatkit.agents import stream_agent_response, simple_to_agent_input, AgentContext
```

---

### ❌ Pitfall #2: Using litellm Prefix for OpenRouter

**Problem:**
```python
# WRONG - Agent SDK doesn't recognize litellm prefix
model = "litellm/openrouter/mistralai/devstral-2512:free"
# Error: "Unknown prefix: litellm"
```

**Solution:**
```python
# CORRECT - Use OpenAIChatCompletionsModel wrapper
from agents import OpenAIChatCompletionsModel, set_default_openai_api
from openai import AsyncOpenAI

# 1. Configure API type for OpenRouter compatibility
set_default_openai_api("chat_completions")

# 2. Create custom OpenAI client
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

# 3. Wrap with OpenAIChatCompletionsModel
model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="mistralai/devstral-2512:free",  # Clean model name
)
```

---

### ❌ Pitfall #3: Wrong Store Method Signature

**Problem:**
```python
# WRONG - Missing required parameters
async def load_threads(
    self,
    context: dict,
    limit: int = 100,
) -> Page[ThreadMetadata]:
    ...
```

**Error:**
```
TypeError: load_threads() got an unexpected keyword argument 'after'
```

**Solution:**
```python
# CORRECT - Must include 'after' and 'order' parameters
async def load_threads(
    self,
    context: dict,
    limit: int = 100,
    after: str | None = None,  # REQUIRED
    order: str = "desc",       # REQUIRED
) -> Page[ThreadMetadata]:
    ...
```

---

### ❌ Pitfall #4: Not Passing Conversation History to Agent

**Problem:**
```python
# WRONG - Agent only responds to greetings, not real questions
result = Runner.run_streamed(
    self.assistant_agent,
    user_message,  # ❌ Just a string, no context
    context=agent_context
)
```

**Symptoms:**
- Agent responds to "hi" but not "what can you do?"
- Agent doesn't remember previous messages
- Context is lost between messages

**Solution:**
```python
# CORRECT - Pass full conversation history
from chatkit.agents import simple_to_agent_input

# Load conversation history
items_page = await self.store.load_thread_items(
    thread.id,
    after=None,
    limit=20,
    order="asc",
    context=context,
)

# Convert to agent input format
input_items = await simple_to_agent_input(items_page.data)

# Pass conversation history, not just message
result = Runner.run_streamed(
    self.assistant_agent,
    input_items,  # ✅ Full conversation context
    context=agent_context
)
```

---

### ❌ Pitfall #5: Store Doesn't Auto-Create Threads

**Problem:**
```python
# WRONG - Returns None if thread doesn't exist
async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata | None:
    state = self._threads.get(thread_id)
    if state:
        return state.thread
    return None  # ❌ ChatKit SDK expects threads to be created
```

**Error:**
```
AttributeError: 'NoneType' object has no attribute 'id'
```

**Solution:**
```python
# CORRECT - Auto-create thread for ChatKit SDK compatibility
async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata | None:
    state = self._threads.get(thread_id)

    if state:
        return state.thread

    # Auto-create thread if it doesn't exist
    # ChatKit SDK expects this behavior
    from chatkit.server import ThreadMetadata
    from datetime import datetime

    new_thread = ThreadMetadata(
        id=thread_id,
        title="New Chat",
        created_at=datetime.utcnow(),
        metadata={
            "user_id": str(context.get("user_id", "unknown")),
        },
    )

    await self.save_thread(new_thread, context or {})
    return new_thread
```

---

### ❌ Pitfall #6: Using Wrong API Endpoint Type

**Problem:**
```python
# Default uses Responses API (not supported by OpenRouter)
# Error: 404 Not Found or "method not supported"
```

**Solution:**
```python
# For OpenRouter, Gemini, and other non-OpenAI providers:
from agents import set_default_openai_api

set_default_openai_api("chat_completions")  # ✅ Use Chat Completions API
```

---

### ❌ Pitfall #7: Custom respond() Method Instead of server.process()

**Problem:**
```python
# WRONG - Implementing custom endpoint logic
@app.post("/chatkit/respond")
async def handle_respond(request: Request):
    body = await request.json()
    # Custom logic...
    return await custom_respond(body.get("message_id"))
```

**Error:**
```
Frontend can't connect, protocol mismatch
```

**Solution:**
```python
# CORRECT - Use ChatKit SDK's built-in server.process()
from chatkit.server import StreamingResult

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    # Get raw request body (required by ChatKit SDK)
    payload = await request.body()

    # Pass context (user_id, session, etc.)
    context = {
        "user_id": get_user_id(request),
    }

    # Let ChatKit SDK handle routing and protocol
    result = await server.process(payload, context)

    # Return appropriate response
    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            }
        )

    # Handle JSON responses
    return Response(content=result.json, media_type="application/json")
```

---

### ❌ Pitfall #8: Missing Page Object Return Type

**Problem:**
```python
# WRONG - Returning list instead of Page object
async def load_threads(self, context, limit, after, order) -> Page[ThreadMetadata]:
    threads = list(self._threads.values())
    return threads  # ❌ Should be Page object
```

**Solution:**
```python
# CORRECT - Return Page with pagination info
from chatkit.store import Page

async def load_threads(self, context, limit, after, order) -> Page[ThreadMetadata]:
    threads = list(self._threads.values())
    threads.sort(key=lambda t: t.created_at, reverse=(order == "desc"))

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
```

---

## Reference Material

| Resource | Description |
|----------|-------------|
| `assets/IMPLEMENTATION_GUIDE.md` | **Complete step-by-step guide** - START HERE |
| `assets/backend/server.py` | Production-ready ChatKit server template |
| `assets/backend/pyproject.toml` | Dependencies configuration |
| `references/architecture.md` | Data flow and component overview |
| `references/chatkit-protocol.md` | NDJSON event types and API endpoints |
| `references/advanced-agent.md` | Structured output, tools, and handoffs |

## Official Documentation

| Resource | URL |
|----------|-----|
| ChatKit Python SDK | https://github.com/openai/chatkit-python |
| ChatKit React | https://github.com/openai/chatkit-js |
| OpenAI Agents SDK | https://github.com/openai/openai-agents-python |

## Troubleshooting Checklist

If you encounter issues, check these in order:

1. **Imports**: Are you using `from chatkit.*` imports?
2. **Store**: Did you implement ALL abstract methods with correct signatures?
3. **Model**: Are you using `OpenAIChatCompletionsModel` wrapper?
4. **API Type**: Did you call `set_default_openai_api("chat_completions")`?
5. **Context**: Are you passing `input_items` (not `user_message`) to `Runner.run_streamed()`?
6. **Threads**: Does your `load_thread()` auto-create threads?
7. **Endpoint**: Are you using `server.process()` not custom logic?

## Still Stuck?

Check the logs for:
- `TypeError` → Usually wrong method signature
- `AttributeError` → Usually missing return value or wrong type
- `Unknown prefix` → Usually litellm prefix or wrong model format
- `404 Not Found` → Usually wrong API type or base_url
