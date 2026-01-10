# ChatKit Integration - Key Learnings & Pitfalls

This document summarizes the critical lessons learned from implementing ChatKit integration with OpenAI Agents SDK and alternative LLM providers.

## Executive Summary

After extensive debugging and research, we successfully integrated ChatKit JS (frontend) + ChatKit Python SDK (backend) + OpenAI Agents SDK + OpenRouter. This document captures the most common pitfalls and their solutions to save you hours of debugging.

## The 9 Critical Pitfalls

### 1. Wrong ChatKit SDK Imports

**Symptom:** `ImportError: cannot import name 'ChatKitServer' from 'openai_chatkit'`

**Solution:**
```python
# CORRECT imports
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.store import Store, Page, ThreadItem
from chatkit.agents import stream_agent_response, simple_to_agent_input, AgentContext
```

**Key Point:** The package is `openai-chatkit` but imports are from `chatkit.*`

---

### 2. Using litellm Prefix for OpenRouter

**Symptom:** `ValueError: Unknown prefix: litellm` or `Unknown prefix: openrouter`

**Solution:**
```python
from agents import OpenAIChatCompletionsModel, set_default_openai_api
from openai import AsyncOpenAI

# Step 1: Configure API type for OpenRouter
set_default_openai_api("chat_completions")

# Step 2: Create custom OpenAI client
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

# Step 3: Wrap with OpenAIChatCompletionsModel
model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="mistralai/devstral-2512:free",  # Clean model name
)
```

**Key Point:** Never use litellm prefixes. Always wrap the client with `OpenAIChatCompletionsModel`.

---

### 3. Wrong Store Method Signature

**Symptom:** `TypeError: load_threads() got an unexpected keyword argument 'after'`

**Solution:**
```python
# Must include 'after' and 'order' parameters
async def load_threads(
    self,
    context: dict,
    limit: int = 100,
    after: str | None = None,  # REQUIRED
    order: str = "desc",       # REQUIRED
) -> Page[ThreadMetadata]:
    ...
```

**Key Point:** The ChatKit SDK requires `after` and `order` parameters for pagination.

---

### 4. Not Passing Conversation History to Agent ⭐ MOST CRITICAL

**Symptom:** Agent only responds to "hi" but not "what can you do?" or other questions

**Solution:**
```python
# WRONG - Causes agent to lose context
result = Runner.run_streamed(
    self.assistant_agent,
    user_message,  # ❌ Just a string
    context=agent_context
)

# CORRECT - Agent has full conversation context
items_page = await self.store.load_thread_items(...)
input_items = await simple_to_agent_input(items_page.data)

result = Runner.run_streamed(
    self.assistant_agent,
    input_items,  # ✅ Full conversation history
    context=agent_context
)
```

**Key Point:** This is the #1 mistake. Always pass `input_items` (from `simple_to_agent_input()`), not just the message string.

---

### 5. Store Doesn't Auto-Create Threads

**Symptom:** `AttributeError: 'NoneType' object has no attribute 'id'`

**Solution:**
```python
async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata | None:
    state = self._threads.get(thread_id)
    if state:
        return state.thread

    # Auto-create thread for ChatKit SDK compatibility
    new_thread = ThreadMetadata(
        id=thread_id,
        title="New Chat",
        created_at=datetime.utcnow(),
        metadata={"user_id": str(context.get("user_id", "unknown"))},
    )

    await self.save_thread(new_thread, context or {})
    return new_thread
```

**Key Point:** ChatKit SDK expects `load_thread()` to auto-create threads if they don't exist.

---

### 6. Using Wrong API Endpoint Type

**Symptom:** `404 Not Found` or "method not supported" errors

**Solution:**
```python
from agents import set_default_openai_api

# For OpenRouter, Gemini, and other non-OpenAI providers:
set_default_openai_api("chat_completions")  # NOT "responses"
```

**Key Point:** OpenRouter doesn't support the Responses API, only Chat Completions.

---

### 7. Custom respond() Method Instead of server.process()

**Symptom:** Frontend can't connect, protocol mismatch errors

**Solution:**
```python
@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    # Get raw request body (required by ChatKit SDK)
    payload = await request.body()

    # Pass context (user_id, session, etc.)
    context = {"user_id": get_user_id(request)}

    # Let ChatKit SDK handle routing and protocol
    result = await server.process(payload, context)

    # Return appropriate response
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream", ...)
```

**Key Point:** Use `server.process()` from ChatKit SDK, don't implement custom endpoint logic.

---

### 8. Missing Page Object Return Type

**Symptom:** `TypeError: Object of type list is not JSON serializable`

**Solution:**
```python
from chatkit.store import Page

async def load_threads(self, context, limit, after, order) -> Page[ThreadMetadata]:
    threads = list(self._threads.values())
    # ... sort and pagination logic ...

    return Page(
        data=slice_threads[:limit],
        has_more=has_more,
        after=slice_threads[-1].id if has_more else None,
    )
```

**Key Point:** Store methods must return `Page` objects, not plain lists.

---

### 9. Messages Overwriting Each Other (CRITICAL) 🆕

**Symptom:**
- First AI response appears correctly
- Second AI response **overwrites** the first instead of appearing below it
- Third AI response overwrites the second
- Chat history restore shows messages correctly (so it's a live streaming issue only)

**Root Cause:**
The `stream_agent_response()` helper uses `__fake_id__` as a temporary placeholder during streaming. When multiple messages are sent, they all use the same `__fake_id__`, causing the frontend ChatKit client to update the same message component instead of creating new ones.

**Solution:**
```python
# WRONG - Causes message overwriting
async for event in stream_agent_response(agent_context, result):
    yield event  # ❌ All messages use same __fake_id__

# CORRECT - Generate unique ID and replace __fake_id__
import uuid

# Generate unique message ID BEFORE streaming
unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"

async for event in stream_agent_response(agent_context, result):
    # CRITICAL: Replace __fake_id__ with our unique ID
    if hasattr(event, 'item'):
        item = event.item
        if hasattr(item, 'id') and item.id == "__fake_id__":
            # Replace __fake_id__ with our unique ID
            new_item = item.model_copy(update={"id": unique_message_id})
            event = event.model_copy(update={"item": new_item})
            logger.info(f"Replaced __fake_id__ with {unique_message_id} in {type(event).__name__}")

    yield event
```

**Key Point:** Generate a unique message ID upfront and replace `__fake_id__` in all streaming events. This ensures each AI response gets a distinct ID that prevents the frontend from overwriting previous messages.

**Related Issues:**
- GitHub: https://github.com/openai/openai-agents-python/issues/1485
- GitHub: https://github.com/openai/openai-chatkit-advanced-samples/issues/6

---

## The Correct Implementation Pattern

Here's the complete, correct pattern for the `respond()` method:

```python
async def respond(
    self,
    thread: ThreadMetadata,
    input: UserMessageItem | ClientToolCallItem,
    context: Any,
) -> AsyncIterator[ThreadStreamEvent]:
    try:
        # 1. Extract user message
        if isinstance(input, UserMessageItem):
            user_message = self._extract_message_content(input.content)
        elif isinstance(input, ClientToolCallItem):
            user_message = f"Tool output: {input.output}"
        else:
            yield ErrorEvent(error_code="unknown_input_type", message=f"Unknown input type: {type(input)}")
            return

        # 2. Load conversation history
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=20,
            order="asc",
            context=context or {},
        )

        # 3. Convert to agent input format
        input_items = await simple_to_agent_input(items_page.data)

        # 4. Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context or {}
        )

        # 5. Run agent with conversation history (NOT just user_message!)
        result = Runner.run_streamed(
            self.assistant_agent,
            input_items,  # ✅ Full conversation context
            context=agent_context
        )

        # 6. Generate unique message ID (CRITICAL for preventing overwriting)
        import uuid
        unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"

        # 7. Stream response as ChatKit events
        async for event in stream_agent_response(agent_context, result):
            # CRITICAL: Replace __fake_id__ with our unique ID
            # This prevents the frontend from overwriting previous messages
            if hasattr(event, 'item'):
                item = event.item
                if hasattr(item, 'id') and item.id == "__fake_id__":
                    new_item = item.model_copy(update={"id": unique_message_id})
                    event = event.model_copy(update={"item": new_item})

            yield event

    except Exception as e:
        logger.error(f"Error in respond: {type(e).__name__}: {str(e)}")
        yield ErrorEvent(error_code=type(e).__name__, message=str(e))
```

---

## Quick Reference Checklist

Before deploying, verify:

- [ ] Using `from chatkit.*` imports (not `from openai_chatkit.*`)
- [ ] Using `OpenAIChatCompletionsModel` wrapper for non-OpenAI models
- [ ] Called `set_default_openai_api("chat_completions")` for OpenRouter/Gemini
- [ ] Store implements ALL abstract methods with correct signatures
- [ ] `load_thread()` auto-creates threads if they don't exist
- [ ] `load_threads()` returns `Page` object, not list
- [ ] Passing `input_items` (not `user_message`) to `Runner.run_streamed()`
- [ ] Replacing `__fake_id__` with unique message IDs in streaming events (prevents overwriting)
- [ ] Using `server.process()` in FastAPI endpoint
- [ ] CORS configured for frontend origin
- [ ] Environment variables set for API keys

---

## Environment Configuration

Required environment variables:

```bash
# Choose one LLM provider
OPENROUTER_API_KEY=sk-or-...
GEMINI_API_KEY=AI...
OPENAI_API_KEY=sk-...

# Model selection
MODEL_NAME=mistralai/devstral-2512:free  # OpenRouter
# MODEL_NAME=gemini-2.0-flash-exp  # Gemini
# MODEL_NAME=gpt-4o-mini  # OpenAI

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Useful Resources

- **ChatKit Python SDK**: https://github.com/openai/chatkit-python
- **ChatKit React**: https://github.com/openai/chatkit-js
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-python
- **OpenRouter**: https://openrouter.ai/

---

## Common Error Messages & Solutions

| Error Message | Likely Cause | Solution |
|--------------|--------------|----------|
| `Unknown prefix: litellm` | Using litellm prefix in model name | Use `OpenAIChatCompletionsModel` wrapper |
| `got an unexpected keyword argument 'after'` | Wrong `load_threads()` signature | Add `after` and `order` parameters |
| `'NoneType' object has no attribute 'id'` | `load_thread()` returns None | Auto-create threads if they don't exist |
| Agent only responds to greetings | Passing `user_message` instead of `input_items` | Pass conversation history via `simple_to_agent_input()` |
| `404 Not Found` from LLM API | Wrong API type or base_url | Use `set_default_openai_api("chat_completions")` |
| `cannot import name 'ChatKitServer'` | Wrong import path | Use `from chatkit.server import ...` |
| **Messages overwriting each other** | `stream_agent_response()` uses `__fake_id__` for all messages | Generate unique ID and replace `__fake_id__` in streaming events |

---

## Timeline of Our Debugging Journey

1. **Initial Setup**: Got ChatKit SDK installed and basic server running
2. **Import Errors**: Fixed incorrect import paths
3. **Model Configuration**: Discovered `OpenAIChatCompletionsModel` wrapper pattern
4. **Store Issues**: Implemented all abstract methods correctly
5. **API Type Error**: Fixed by calling `set_default_openai_api("chat_completions")`
6. **Thread Creation**: Added auto-creation in `load_thread()`
7. **Context Issue**: **Critical breakthrough** - passing `input_items` instead of `user_message`
8. **Success**: Agent now responds to all types of messages with full context
9. **Message Overwriting Bug (2026-01-10)**: Discovered `stream_agent_response()` uses `__fake_id__` placeholder, causing messages to overwrite each other. Fixed by generating unique IDs upfront and replacing `__fake_id__` in streaming events.

---

## Conclusion

The ChatKit integration is deceptively simple but has several critical implementation details that, if missed, will cause mysterious failures. The most critical lessons are:

1. **Always pass conversation history (`input_items`) to the agent, not just the current message**
2. **Always generate unique message IDs and replace `__fake_id__` in streaming events** to prevent message overwriting

Use the templates in this skill as a starting point - they've been battle-tested and incorporate all the lessons learned.
