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
8. **Message IDs**: Are you replacing `__fake_id__` with unique IDs? (see Pitfall #9)
9. **Fullscreen Layout**: Does your outer container have `flex flex-col` when using `flex-1` on ChatKit? (see Pitfall #10)
10. **Theme Memoization**: Is your ThemeContext value memoized with `useMemo`? (see Pitfall #11)
11. **Theme Key Prop**: Are you using `key` prop for theme changes? Remove it. (see Pitfall #12)
12. **Domain Verification**: Is your production domain registered at OpenAI dashboard? (see Pitfall #13)

---

### ❌ Pitfall #9: Messages Overwriting Each Other (CRITICAL)

**Problem:**
```python
# WRONG - Using stream_agent_response() without fixing __fake_id__
async for event in stream_agent_response(agent_context, result):
    yield event  # ❌ All messages use same __fake_id__, causing overwrites
```

**Symptoms:**
- First AI response appears correctly
- Second AI response **overwrites** the first instead of appearing below it
- Third AI response overwrites the second
- Chat history restore shows messages correctly (so it's a live streaming issue only)

**Root Cause:**
The `stream_agent_response()` helper uses `__fake_id__` as a temporary placeholder during streaming. When multiple messages are sent, they all use the same `__fake_id__`, causing the frontend ChatKit client to update the same message instead of creating new ones.

**Solution:**
```python
# CORRECT - Generate unique message ID upfront and replace __fake_id__
import uuid

# Generate unique message ID BEFORE streaming
unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"
logger.info(f"Generated unique message ID: {unique_message_id}")

async for event in stream_agent_response(agent_context, result):
    event_type = type(event).__name__

    # CRITICAL: Replace __fake_id__ with our unique ID
    if hasattr(event, 'item'):
        item = event.item
        if hasattr(item, 'id') and item.id == "__fake_id__":
            # Replace __fake_id__ with our unique ID
            new_item = item.model_copy(update={"id": unique_message_id})
            event = event.model_copy(update={"item": new_item})
            logger.info(f"Replaced __fake_id__ with {unique_message_id} in {event_type}")

    # Yield event with fixed unique ID
    yield event
```

**Why This Works:**
- Each AI response gets a **unique, persistent ID** from the start
- The frontend sees a **different ID** for each new message
- Instead of updating the previous message, it creates a **new message**
- Streaming still works because all events for a single response use the same unique ID

**Related Issues:**
- GitHub Issue: https://github.com/openai/openai-agents-python/issues/1485
- GitHub Issue: https://github.com/openai/openai-chatkit-advanced-samples/issues/6

---

### Alternative Approach: Dual `__fake_id__` Replacement (More Robust)

**Pattern**: Replace `__fake_id__` in BOTH the Store's `add_thread_item()` method AND the `respond()` method's streaming loop.

This provides **defense in depth** - if one layer misses the replacement, the other catches it.

**Implementation 1: Store Layer**

```python
class MemoryStore(Store[dict]):
    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: dict,
    ) -> None:
        """Add an item to a thread with __fake_id__ replacement."""
        import logging
        logger = logging.getLogger(__name__)

        # Get or create thread state
        state = self._threads.get(thread_id)
        if not state:
            state = _ThreadState(thread=ThreadMetadata(
                id=thread_id,
                title="New Chat",
                created_at=datetime.utcnow(),
                metadata={},
            ), items=[])
            self._threads[thread_id] = state

        # CRITICAL FIX: Replace __fake_id__ with a real unique ID
        # Each message must have a unique ID or they will overwrite each other
        if item.id == "__fake_id__":
            import uuid
            new_id = f"{item.type}_{uuid.uuid4().hex[:16]}"
            item = item.model_copy(update={"id": new_id})
            logger.info(f"[add_thread_item] Replaced __fake_id__ with {new_id}")

        # Check for overwrites
        existing = self._items_map.get(item.id)
        if existing:
            logger.warning(f"[add_thread_item] ⚠️ OVERWRITING existing item {item.id}!")

        state.items.append(item)
        self._items_map[item.id] = item
```

**Implementation 2: respond() Layer** (same as Pitfall #9 solution)

**Benefits of Dual Approach:**
- Store layer catches items during `add_thread_item()` calls (when ThreadItemAddedEvent is processed)
- respond() layer catches items during streaming (when ThreadItemReplacedEvent is processed)
- Comprehensive logging at both levels helps debugging
- More robust against SDK changes or edge cases

**When to Use:**
- Production applications where message integrity is critical
- Complex setups with multiple agent fallbacks
- When you need detailed logging for debugging

---

## Advanced Patterns

### Fallback Agent Pattern (Rate Limit Resilience)

**Problem**: When using OpenRouter or other third-party LLM providers, you may encounter rate limits (HTTP 429) that interrupt the user experience.

**Solution**: Implement a fallback agent that uses a different provider (e.g., direct OpenAI API) when the primary agent hits rate limits.

**Implementation:**

```python
class TeamFlowChatKitServer(ChatKitServer):
    def __init__(self, data_store: Store):
        super().__init__(data_store)

        # Primary agent (e.g., OpenRouter)
        self.assistant_agent = create_chatbot_agent(
            model="google/gemini-2.0-flash-exp:free",
        )

        # Lazy-initialized fallback agent
        self._fallback_agent: Optional[Agent] = None

    def _get_fallback_agent(self) -> Agent:
        """Get or create the fallback Agent using direct OpenAI API."""
        if self._fallback_agent is None:
            from app.agents.client import get_openai_fallback_model
            from agents import Agent

            # Create direct OpenAI model (not through OpenRouter)
            model_instance = get_openai_fallback_model("gpt-4o-mini")

            # Create fallback agent with same instructions and tools
            self._fallback_agent = Agent(
                name="assistant-fallback",
                instructions=TEAMFLOW_AGENT_INSTRUCTIONS,
                model=model_instance,
                tools=[...],  # Same tools as primary
            )

            import logging
            logging.info("[ChatKit] Created fallback agent using direct OpenAI API")

        return self._fallback_agent

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallItem,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        import logging
        logger = logging.getLogger(__name__)

        # Load history and create context
        items_page = await self.store.load_thread_items(...)
        input_items = await simple_to_agent_input(items_page.data)
        agent_context = AgentContext(thread=thread, store=self.store, request_context=context)

        # Try primary agent first
        agent_to_use = self.assistant_agent
        used_fallback = False

        try:
            result = Runner.run_streamed(agent_to_use, input_items, context=agent_context)
        except Exception as primary_error:
            # Check if this is a 429 rate limit error
            error_str = str(primary_error).lower()
            is_rate_limit = (
                '429' in error_str or
                getattr(primary_error, 'code', None) == 429 or
                'rate limit' in error_str or
                'provider returned error' in error_str
            )

            if is_rate_limit:
                logger.warning(f"Primary agent hit rate limit. Using fallback agent...")

                # Retry with fallback agent
                fallback_agent = self._get_fallback_agent()
                agent_to_use = fallback_agent
                used_fallback = True

                result = Runner.run_streamed(agent_to_use, input_items, context=agent_context)
            else:
                # Not a rate limit error - re-raise
                raise

        # Generate unique message ID and stream response
        import uuid
        unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"

        try:
            async for event in stream_agent_response(agent_context, result):
                # Replace __fake_id__ with unique ID
                if hasattr(event, 'item') and event.item.id == "__fake_id__":
                    new_item = event.item.model_copy(update={"id": unique_message_id})
                    event = event.model_copy(update={"item": new_item})

                yield event

        except Exception as streaming_error:
            # Check if rate limit happened DURING streaming
            error_str = str(streaming_error).lower()
            is_rate_limit = '429' in error_str or getattr(streaming_error, 'code', None) == 429

            # If we hit rate limit during streaming and haven't used fallback yet
            if is_rate_limit and not used_fallback:
                logger.warning(f"Rate limit during streaming. Retrying with fallback...")

                # Retry with fallback agent
                fallback_agent = self._get_fallback_agent()
                result = Runner.run_streamed(fallback_agent, input_items, context=agent_context)

                # Generate NEW unique message ID for fallback response
                unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"

                async for event in stream_agent_response(agent_context, result):
                    # Replace __fake_id__ with unique ID
                    if hasattr(event, 'item') and event.item.id == "__fake_id__":
                        new_item = event.item.model_copy(update={"id": unique_message_id})
                        event = event.model_copy(update={"item": new_item})

                    yield event
            else:
                # Either not a rate limit error, or we already tried fallback
                raise
```

**Key Points:**
1. **Lazy initialization**: Fallback agent is only created when needed (saves resources)
2. **Same tools and instructions**: Ensures consistent behavior across providers
3. **Two-level retry**: Retries on both initial execution AND streaming errors
4. **New message ID on fallback**: Generates fresh unique ID to avoid conflicts

**When to Use:**
- Using OpenRouter or other aggregators with rate limits
- Production applications requiring high availability
- When using free-tier models with strict limits

---

### Action Handlers (Client-Side Interactions)

**Problem**: You need to handle user interactions with AI responses, such as thumbs up/down feedback, button clicks, or form submissions.

**Solution**: Implement the `action()` method in your ChatKitServer to handle client-side actions.

**Frontend Configuration:**

```tsx
// ChatWidget.tsx
const { control, ref, sendUserMessage } = useChatKit({
  api: {
    url: chatkitEndpoint,
    domainKey: 'local-dev',
  },
  // Enable feedback actions (thumbs up/down)
  threadItemActions: {
    feedback: true,  // Show thumbs up/down buttons
    retry: false,    // Hide retry button
  },
})
```

**Backend Implementation:**

```python
class TeamFlowChatKitServer(ChatKitServer):
    async def action(
        self,
        thread: ThreadMetadata,
        action_name: str,
        payload: dict,
        context: Any,
    ) -> AsyncIterator:
        """
        Handle client-side actions (button clicks, form submissions, etc.).

        Args:
            thread: ChatKit thread metadata
            action_name: Name of the action ("feedback", "add_to_todo", etc.)
            payload: Action payload (form values, feedback type, item_id, etc.)
            context: Request context

        Yields:
            ChatKit events from action processing
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # Handle feedback actions (thumbs up/down)
            if action_name == "feedback":
                feedback_type = payload.get("feedback")  # "thumbs_up" or "thumbs_down"
                item_id = payload.get("item_id")

                logger.info(f"Feedback received: {feedback_type} for item {item_id}")

                # Map feedback to action
                action = "accepted" if feedback_type == "thumbs_up" else "rejected"

                # Track recommendation acceptance (analytics)
                await self._track_recommendation_acceptance(
                    recommendation_type="task_creation",
                    recommendation_id=item_id,
                    action=action,
                    reasoning="AI recommended task creation",
                    context={"thread_id": thread.id},
                    user_id=context.get("user_id"),
                )

                # Stream a confirmation response
                async for event in self._stream_agent_response_simple(
                    f"Thanks for your feedback! ({action})",
                    thread,
                    context
                ):
                    yield event

            # Handle custom actions
            elif action_name == "add_to_todo":
                item = payload.get("item")
                if item:
                    async for event in self._stream_agent_response_simple(
                        f"Added '{item}' to todo list",
                        thread,
                        context
                    ):
                        yield event

        except Exception as e:
            yield ErrorEvent(
                error_code=type(e).__name__,
                message=str(e)
            )

    async def _stream_agent_response_simple(
        self,
        message: str,
        thread: ThreadMetadata,
        context: Any,
    ) -> AsyncIterator:
        """Stream a simple text response."""
        from agents import Runner

        result = Runner.run_streamed(
            self.assistant_agent,
            message,
        )

        async for event in result.stream_events():
            # Process events if needed
            pass
```

**Common Action Types:**

| Action Name | Payload Fields | Use Case |
|-------------|----------------|----------|
| `feedback` | `feedback`, `item_id` | Thumbs up/down on AI responses |
| `retry` | `item_id` | Regenerate a failed response |
| `copy` | `text` | Copy text to clipboard |
| `custom` | (varies) | Your custom actions |

**When to Use:**
- Recommendation tracking (thumbs up/down for AI suggestions)
- Analytics (track which responses users find helpful)
- Custom workflows (approve/reject, add to todo, etc.)

---

## Frontend Advanced Patterns

### Voice Input Integration

**Problem**: Users want to send messages via voice input instead of typing.

**Solution**: Integrate Web Speech API with ChatKit's `sendUserMessage` function.

**Implementation:**

```tsx
// VoiceInputButton.tsx
'use client'

import { useState, useEffect } from 'react'
import { Mic, MicOff } from 'lucide-react'

interface VoiceInputButtonProps {
  onTranscriptReady: (transcript: string) => void
  language?: string
}

export function VoiceInputButton({ onTranscriptReady, language = 'en-US' }: VoiceInputButtonProps) {
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState<any>(null)

  useEffect(() => {
    // Initialize speech recognition
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

      if (SpeechRecognition) {
        const recog = new SpeechRecognition()
        recog.continuous = false
        recog.interimResults = false
        recog.lang = language

        recog.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript
          onTranscriptReady(transcript)
          setIsListening(false)
        }

        recog.onerror = () => {
          setIsListening(false)
        }

        recog.onend = () => {
          setIsListening(false)
        }

        setRecognition(recog)
      }
    }
  }, [language, onTranscriptReady])

  const toggleListening = () => {
    if (!recognition) return

    if (isListening) {
      recognition.stop()
    } else {
      recognition.start()
    }
    setIsListening(!isListening)
  }

  return (
    <button
      onClick={toggleListening}
      className={`p-2 rounded-full transition-colors ${
        isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
      }`}
      aria-label={isListening ? 'Stop listening' : 'Start voice input'}
    >
      {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
    </button>
  )
}
```

**ChatWidget Integration:**

```tsx
// ChatWidget.tsx
import { VoiceInputButton } from './VoiceInputButton'
import { useChatKit } from '@openai/chatkit-react'

export function ChatWidget({ apiUrl }: { apiUrl?: string }) {
  const chatkitEndpoint = `${apiUrl}/api/v1/chat/chatkit`

  const { control, ref, sendUserMessage } = useChatKit({
    api: { url: chatkitEndpoint },
  })

  // Handle voice transcript - send to ChatKit when ready
  const handleVoiceTranscriptReady = async (transcript: string) => {
    if (!transcript.trim()) return

    try {
      // Use ChatKit's sendUserMessage API to send the transcript
      await sendUserMessage({ text: transcript.trim() })
    } catch (error) {
      console.error('Failed to send voice message:', error)
    }
  }

  return (
    <div className="relative">
      <ChatKit control={control} ref={ref} />

      {/* Voice Input Button - positioned above input */}
      <div className="absolute bottom-24 right-6 z-10">
        <VoiceInputButton
          onTranscriptReady={handleVoiceTranscriptReady}
          language="en-US"
        />
      </div>
    </div>
  )
}
```

**Key Points:**
- Uses Web Speech API (browser native, no extra dependencies)
- `continuous: false` for single-message inputs
- Sends transcript via `sendUserMessage()` for proper ChatKit integration
- Visual feedback with pulsing animation when listening

---

### Fullscreen Toggle Pattern

**Problem**: Users want to expand the chat widget to fullscreen for better readability.

**Solution**: Implement fullscreen toggle with keyboard shortcuts.

**Implementation:**

```tsx
// ChatWidget.tsx
import { useState, useEffect } from 'react'
import { Maximize2, Minimize2 } from 'lucide-react'

interface ChatWidgetProps {
  isFullscreen?: boolean  // Allow parent control
  onFullscreenToggle?: () => void
  isOpen?: boolean  // Allow parent to control open state
}

export function ChatWidget({
  isFullscreen: isFullscreenProp = false,
  onFullscreenToggle,
  isOpen: isOpenProp,
}: ChatWidgetProps) {
  const [isFullscreen, setIsFullscreen] = useState(isFullscreenProp)
  const [isOpenInternal, setIsOpenInternal] = useState(false)

  // Sync internal state with prop
  useEffect(() => {
    setIsFullscreen(isFullscreenProp)
  }, [isFullscreenProp])

  // Handle fullscreen toggle
  const handleFullscreenToggle = () => {
    const newState = !isFullscreen
    setIsFullscreen(newState)
    if (onFullscreenToggle) {
      onFullscreenToggle()
    }
  }

  // Keyboard shortcut: Ctrl+Shift+F or Escape
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey && event.shiftKey && event.key === 'F') || event.key === 'Escape') {
        event.preventDefault()
        handleFullscreenToggle()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isFullscreen])

  const isOpen = isOpenProp !== undefined ? isOpenProp : isOpenInternal

  return (
    <>
      {/* Floating toggle button */}
      {isOpen && (
        <div className={`
          fixed z-[9998] bg-white shadow-2xl border border-gray-200
          ${isFullscreen ? 'inset-0 rounded-none' : 'rounded-lg'}
        `}
        style={{
          width: isFullscreen ? '100vw' : '400px',
          height: isFullscreen ? '100vh' : '600px',
        }}
        >
          {/* Status bar with fullscreen toggle */}
          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 rounded-t-lg">
            <div className="flex items-center justify-between">
              <span>AI Assistant</span>

              {/* Fullscreen toggle button */}
              <button
                onClick={handleFullscreenToggle}
                className="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-100"
                aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
                title={`Press Ctrl+Shift+F or ${isFullscreen ? 'Escape' : 'click'} to ${isFullscreen ? 'exit' : 'enter'} fullscreen`}
              >
                {isFullscreen ? (
                  <Minimize2 className="h-4 w-4" />
                ) : (
                  <Maximize2 className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          {/* ChatKit component */}
          <div className={isFullscreen ? 'flex-1 overflow-hidden' : 'h-[540px]'}>
            <ChatKit control={control} ref={ref} />
          </div>
        </div>
      )}
    </>
  )
}
```

**Usage from Parent:**

```tsx
// /app/chat/page.tsx (dedicated fullscreen chat page)
'use client'

import { useState } from 'react'
import { ChatWidget } from '@/components/chat/ChatWidget'

export default function ChatPage() {
  const [isFullscreen, setIsFullscreen] = useState(true)

  return (
    <ChatWidget
      isOpen={true}
      isFullscreen={isFullscreen}
      onFullscreenToggle={() => setIsFullscreen(!isFullscreen)}
    />
  )
}
```

**Key Features:**
- Keyboard shortcuts: `Ctrl+Shift+F` to enter fullscreen, `Escape` to exit
- Parent can control fullscreen state via props
- Responsive sizing (fullscreen vs floating widget)
- Persistent state management

---

## Theme Integration

**Problem**: ChatKit needs to support dark/light mode while maintaining your application's brand colors and design system.

**Solution**: Implement a ThemeProvider with CSS variables that integrates with ChatKit's theme prop.

### Implementation

**1. Create ThemeProvider (contexts/ThemeContext.tsx):**

```tsx
'use client'

import { createContext, useContext, useEffect, useState, useMemo } from 'react'

type Theme = 'dark' | 'light' | 'system'

interface ThemeContextType {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      // Clear old storage keys to avoid conflicts
      localStorage.removeItem('vite-ui-theme')

      const savedTheme = localStorage.getItem('theme') as Theme | null

      // Default to 'light' if no saved preference or if 'system'
      if (savedTheme === 'system' || !savedTheme) {
        return 'light'
      }
      return savedTheme
    }
    return 'light'
  })

  // Apply theme to document root
  useEffect(() => {
    if (typeof window === 'undefined') return

    const root = document.documentElement
    root.classList.remove('light', 'dark')

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      root.classList.add(systemTheme)
    } else {
      root.classList.add(theme)
    }

    // Persist theme choice
    localStorage.setItem('theme', theme)
  }, [theme])

  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(() => ({
    theme,
    setTheme: (newTheme: Theme) => {
      localStorage.setItem('theme', newTheme)
      setTheme(newTheme)
    },
    toggleTheme: () => {
      setTheme(prev => prev === 'light' ? 'dark' : 'light')
    },
  }), [theme])

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
```

**2. Define CSS Variables (globals.css):**

```css
@layer base {
  :root {
    /* Light Mode */
    --background: 0 0% 100%;        /* White */
    --foreground: 240 10% 3.9%;     /* Zinc 950 */
    --muted: 240 4.8% 95.9%;        /* Zinc 100 */
    --border: 240 5.9% 90%;         /* Zinc 200 */
    --accent: 83, 78%, 56%;          /* Lime Green */
    --accent-foreground: 240 5.9% 10%;
  }

  .dark {
    /* Dark Mode */
    --background: 240 10% 3.9%;     /* Zinc 950 */
    --foreground: 0 0% 98%;         /* Zinc 50 */
    --muted: 240 3.7% 15.9%;        /* Zinc 800 */
    --border: 240 3.7% 15.9%;       /* Zinc 800 */
    --accent: 83, 78%, 56%;          /* Lime Green (same) */
    --accent-foreground: 240 5.9% 10%;
  }
}
```

**3. ChatWidget Integration:**

```tsx
// ChatWidget.tsx
import { useTheme } from '@/contexts/ThemeContext'
import { Sun, Moon } from 'lucide-react'

export function ChatWidget() {
  const { theme, toggleTheme } = useTheme()

  // Resolve 'system' theme to 'light' or 'dark' for ChatKit
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      setResolvedTheme(systemTheme)
    } else {
      setResolvedTheme(theme as 'light' | 'dark')
    }
  }, [theme])

  const { control, ref } = useChatKit({
    api: { url: chatkitEndpoint, domainKey: 'local-dev' },
    theme: resolvedTheme,  // Pass resolved theme to ChatKit
    // ... other config
  })

  return (
    <div className="bg-background border border-border">
      {/* Status bar with theme toggle */}
      <div className="bg-muted border-b border-border">
        <span>Status: Connected</span>

        <button
          onClick={toggleTheme}
          aria-label={`Switch to ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
        >
          {resolvedTheme === 'light' ? (
            <Moon className="h-4 w-4" />
          ) : (
            <Sun className="h-4 w-4" />
          )}
        </button>
      </div>

      <ChatKit control={control} ref={ref} />
    </div>
  )
}
```

### ❌ Pitfall #11: Theme Toggle Causes Infinite Re-renders

**Problem:**
- Theme toggle causes page to load repeatedly
- Components re-render infinitely
- Browser becomes unresponsive

**Root Cause:**
Creating the context value object on every render without memoization:

```tsx
// WRONG - Value object recreated on every render
const value = {
  theme,
  setTheme: (newTheme) => { ... },
  toggleTheme: () => { ... },
}
```

**Solution:**
Use `useMemo` to memoize the context value:

```tsx
// CORRECT - Value object only changes when theme changes
const value = useMemo(() => ({
  theme,
  setTheme: (newTheme: Theme) => {
    localStorage.setItem('theme', newTheme)
    setTheme(newTheme)
  },
  toggleTheme: () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  },
}), [theme])
```

### ❌ Pitfall #12: Using `key` Prop for Theme Changes

**Problem:**
- Using `key={theme}` on the ChatWidget container to force re-render on theme change
- Causes entire widget to unmount and remount
- Loses chat state and connection
- Creates "loading" state on every theme toggle

```tsx
// WRONG - Forces complete remount on theme change
<div key={resolvedTheme} className="...">
  <ChatKit control={control} ref={ref} />
</div>
```

**Solution:**
ChatKit SDK handles theme changes internally via the `theme` prop. No `key` prop needed:

```tsx
// CORRECT - ChatKit updates without remounting
<div className="...">
  <ChatKit control={control} ref={ref} />
</div>
```

**Why This Works:**
- ChatKit's `theme` prop triggers internal re-style without unmounting
- Preserves chat state and connection
- Smooth transitions between themes
- No "Connecting..." flash on theme toggle

### Key Points

1. **Always memoize context value** with `useMemo` to prevent infinite re-renders
2. **Use CSS variables** (`bg-background`, `text-foreground`) instead of hardcoded colors
3. **Never use `key` prop** for theme changes - let ChatKit handle it internally
4. **Resolve 'system' theme** before passing to ChatKit (it only accepts 'light' | 'dark')
5. **Clear old localStorage keys** to avoid conflicts from previous implementations
6. **Default to 'light'** instead of 'system' for predictable behavior

---

### ❌ Pitfall #13: Domain Verification in Production (CRITICAL)

**Problem:**
- ChatKit loads successfully in local development
- Production deployment shows `IntegrationError: Domain verification failed`
- Error appears in browser console immediately on page load
- Chat widget may briefly appear then disappears

**Symptoms:**
```
IntegrationError: Domain verification failed for https://your-domain.vercel.app
POST https://api.openai.com/v1/chatkit/domain_keys/verify 400 (Bad Request)
Uncaught (in promise) IntegrationError
```

**Root Cause:**
ChatKit's frontend JavaScript is loaded from OpenAI's CDN (`https://cdn.platform.openai.com/deployments/chatkit/chatkit.js`). This CDN code **always** verifies the domain with OpenAI's servers, regardless of whether you use a self-hosted backend. Even though you're using a custom FastAPI backend, the frontend ChatKit client enforces domain verification as a security measure.

**Why It Works Locally:**
- ChatKit automatically allows `localhost`, `127.0.0.1`, and local IP addresses
- No domain registration needed for local development
- Any `domainKey` value works locally

**Why It Fails in Production:**
- Production domains must be registered in OpenAI's dashboard
- The CDN verifies the domain on every page load
- Client-side error handlers cannot suppress this error (thrown by CDN code)

**Solution:**

**Step 1: Register Your Domain**
1. Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
2. Click "Add Domain"
3. Enter your production domain (e.g., `teamflow.vercel.app` or `*.vercel.app`)
4. Copy the generated domain key (starts with `dk_`)

**Step 2: Add Environment Variable**
Add the domain key to your frontend environment variables:

```bash
# .env.local (for local testing with production domain)
NEXT_PUBLIC_CHATKIT_DOMAIN_KEY=dk_xxxxxxxxxxxxx

# Vercel / Netlify / other hosting
# Add as environment variable in deployment settings
```

**Step 3: Use Environment Variable in ChatWidget**

```tsx
// ChatWidget.tsx
const { control, ref, sendUserMessage } = useChatKit({
  api: {
    url: chatkitEndpoint,
    // Use environment variable for production domain key
    domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || 'local-dev',
  },
  theme: resolvedTheme,
  // ... rest of config
})
```

**Step 4: Verify Deployment**
```bash
# Push changes to trigger deployment
git push

# Check browser console for successful initialization
# Should see: "[ChatKit] ChatKit initialized successfully"
# No domain verification errors
```

**Common Mistakes:**

❌ **Using hardcoded 'local-dev' in production**
```tsx
// WRONG - Production won't work
domainKey: 'local-dev'
```

❌ **Trying to suppress error with client-side handlers**
```tsx
// WRONG - Cannot catch error thrown by CDN code
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason?.message?.includes('Domain verification failed')) {
    event.preventDefault() // This doesn't work!
  }
})
```

❌ **Removing domainKey parameter**
```tsx
// WRONG - TypeScript build error, domainKey is required
domainKey: undefined // Build will fail
```

✅ **CORRECT: Register domain + use environment variable**
```tsx
// CORRECT - Domain registered, key from environment
domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || 'local-dev'
```

**Key Points:**
1. **Domain verification is mandatory** for production deployments
2. **Register domain at OpenAI dashboard** before deploying
3. **Use environment variable** for domain key (`NEXT_PUBLIC_CHATKIT_DOMAIN_KEY`)
4. **Client-side error handlers cannot suppress** this error (thrown by CDN)
5. **Local development works without registration** (localhost auto-allowed)
6. **Self-hosted backend doesn't bypass** domain verification (frontend enforces it)

**Environment Variables Checklist:**
- [ ] `NEXT_PUBLIC_CHATKIT_DOMAIN_KEY` added to Vercel/Netlify/CI
- [ ] Domain registered at https://platform.openai.com/settings/organization/security/domain-allowlist
- [ ] Domain key starts with `dk_`
- [ ] Fallback to `'local-dev'` for local development

---

### ❌ Pitfall #10: Fullscreen Chat Shows No Content (CRITICAL)

**Problem:**
- When implementing fullscreen toggle, the chat widget expands but shows no content (no input, no messages, blank screen)
- Status bar and header may be visible, but ChatKit content area is empty

**Symptoms:**
- Fullscreen mode activates (widget expands to fill screen)
- Status bar/header visible
- ChatKit content area is blank or has 0px height
- Messages and input field are not visible

**Root Cause:**
Missing `flex flex-col` on the outer container when using `flex-1` on the ChatKit content area.

**Solution:**
```tsx
// WRONG - Missing flex layout on parent
<div className="fixed z-[9998] ..." style={{ height: isFullscreen ? '100vh' : '600px' }}>
  <div className="px-4 py-2 ...">Status bar</div>

  {/* flex-1 only works when parent has display: flex */}
  <div className={isFullscreen ? 'flex-1 overflow-hidden' : 'h-[540px]'}>
    <ChatKit control={control} ref={ref} />
  </div>
</div>

// CORRECT - Parent has flex flex-col
<div className="fixed z-[9998] flex flex-col ..." style={{ height: isFullscreen ? '100vh' : '600px' }}>
  <div className="px-4 py-2 ...">Status bar</div>

  {/* Now flex-1 works correctly - takes remaining space */}
  <div className={isFullscreen ? 'flex-1 overflow-hidden' : 'h-[540px]'}>
    <ChatKit control={control} ref={ref} />
  </div>
</div>
```

**Key Points:**
1. **Always add `flex flex-col`** to the outer container when using `flex-1` on children
2. The outer container needs `display: flex` and `flex-direction: column` for `flex-1` to work
3. This applies to BOTH fullscreen mode and floating widget mode
4. Common mistake: forgetting `flex-col` which causes children to stack horizontally instead of vertically

**Verification:**
- Toggle fullscreen mode
- Verify status bar appears at top
- Verify ChatKit content area fills remaining space
- Verify messages and input are visible
- Check DevTools Elements panel to confirm container has `display: flex`

**Related:** CSS Flexbox - `flex-1` only works in flex containers

---

## Still Stuck?

Check the logs for:
- `TypeError` → Usually wrong method signature
- `AttributeError` → Usually missing return value or wrong type
- `Unknown prefix` → Usually litellm prefix or wrong model format
- `404 Not Found` → Usually wrong API type or base_url
- **Messages overwriting** → Missing `__fake_id__` replacement (see Pitfall #9)
- **Fullscreen blank screen** → Missing `flex flex-col` on container (see Pitfall #10)
- **Infinite loading/re-renders** → Missing `useMemo` in ThemeContext (see Pitfall #11)
- **Theme toggle causes loading** → Using `key` prop for theme changes (see Pitfall #12)
- **Domain verification error** → Domain not registered at OpenAI dashboard (see Pitfall #13)
- **AI responses not in history** → Not using stream_agent_response() (see Pitfall #14)
- **Messages overwriting** → Missing `__fake_id__` replacement (see Pitfall #15)
- **Duplicate task creation** → Agent re-processing old messages (see Pitfall #16)
- **History loading errors** → Using previous_response_id with wrong model (see Pitfall #17)

---

### ❌ Pitfall #14: AI Responses Not Persisting in Chat History

**Problem:**
- AI responses appear in the chat during streaming
- After page refresh, AI responses are missing from history
- Only user messages are saved to conversation history
- ChatKit "Failed to load conversation" errors

**Symptoms:**
```
# During chat - looks normal:
User: "Create a task"
AI: "Task created successfully!" ✅

# After refresh - AI response gone:
User: "Create a task" ✅
# AI message is missing! ❌
```

**Root Cause:**
Using manual event handling with `ThreadItemAddedEvent` instead of `ThreadItemDoneEvent`. According to ChatKit documentation:

> "ThreadItemAddedEvent does NOT persist the item. ChatKitServer saves on ThreadItemDoneEvent"

When you manually yield events:
- `ThreadItemAddedEvent` - Introduces a new item to the UI (NOT persisted)
- `ThreadItemUpdatedEvent` - Mutates a pending item (NOT persisted)
- `ThreadItemDoneEvent` - Marks item complete AND **persists it**

**WRONG Code (Manual Event Handling):**
```python
# ❌ This does NOT persist messages!
async for event in result.stream_events():
    if event.type == "run_item_stream_event" and event.item.type == "message_output_item":
        message_text = ItemHelpers.text_message_output(event.item)
        assistant_item = AssistantMessageItem(
            id=unique_message_id,
            thread_id=thread.id,
            created_at=datetime.now(timezone.utc),
            content=[AssistantMessageContent(text=message_text)],
        )
        yield ThreadItemAddedEvent(item=assistant_item)  # ❌ Not persisted!
```

**CORRECT Code (Using stream_agent_response):**
```python
# ✅ Use stream_agent_response - handles all event types including persistence
from chatkit.agents import stream_agent_response

result = Runner.run_streamed(agent, input_items, context=agent_context)

async for event in stream_agent_response(agent_context, result):
    # This function yields:
    # - ThreadItemAddedEvent (introduces item)
    # - ThreadItemUpdatedEvent (mutates pending item)
    # - ThreadItemDoneEvent (marks complete AND PERSISTS) ✅
    yield event
```

**Why This Works:**
- `stream_agent_response()` is the official ChatKit helper for agent streaming
- It properly yields `ThreadItemDoneEvent` which persists messages
- It handles tool calls, workflows, and all ChatKit event types
- No manual event construction needed

**Related:** ChatKit Thread Stream Events documentation

---

### ❌ Pitfall #15: AI Responses Overwriting Each Other in Live Chat

**Problem:**
- First AI response appears correctly
- Second AI response **overwrites** the first instead of appearing below it
- Third AI response overwrites the second
- Chat history restore shows messages correctly (so it's a live streaming issue only)

**Symptoms:**
```
Message 1: "Hello!" → Shows: "Hello!"
Message 2: "How are you?" → Shows: "How are you?" (first message gone!)
Message 3: "Good thanks" → Shows: "Good thanks" (second message gone!)
```

**Root Cause:**
The `stream_agent_response()` helper uses `__fake_id__` as a temporary placeholder during streaming. When multiple messages are sent, they all use the same `__fake_id__`, causing the frontend ChatKit client to update the same message instead of creating new ones.

**Solution:**
```python
# Generate unique message ID BEFORE streaming
import uuid

unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"

async for event in stream_agent_response(agent_context, result):
    # CRITICAL: Replace __fake_id__ with our unique ID
    if hasattr(event, 'item'):
        item = event.item
        if hasattr(item, 'id') and item.id == "__fake_id__":
            # Replace __fake_id__ with our unique ID
            new_item = item.model_copy(update={"id": unique_message_id})
            event = event.model_copy(update={"item": new_item})

    yield event
```

**Why This Works:**
- Each AI response gets a **unique, persistent ID** from the start
- The frontend sees a **different ID** for each new message
- Instead of updating the previous message, it creates a **new message**
- Streaming still works because all events for a single response use the same unique ID

**Dual Approach (More Robust):**
Also add `__fake_id__` replacement in the Store's `add_thread_item()` and `save_item()` methods:

```python
# In MemoryStore.add_thread_item()
if item.id == "__fake_id__":
    new_id = f"{item.type}_{uuid.uuid4().hex[:16]}"
    item = item.model_copy(update={"id": new_id})

# In MemoryStore.save_item()
if item.id == "__fake_id__":
    new_id = f"{item.type}_{uuid.uuid4().hex[:16]}"
    item = item.model_copy(update={"id": new_id})
```

**Benefits of Dual Approach:**
- Store layer catches items during `ThreadItemAddedEvent` processing
- respond() layer catches items during streaming
- Comprehensive logging at both levels helps debugging
- More robust against SDK changes

**Related Issues:**
- GitHub Issue: https://github.com/openai/openai-agents-python/issues/1485
- GitHub Issue: https://github.com/openai/openai-chatkit-advanced-samples/issues/6

---

### ❌ Pitfall #16: Agent Re-processing Old Messages (Duplicate Task Creation)

**Problem:**
- User says: "Create a task named 'fix navbar'"
- Agent creates task correctly
- User says: "Move the fix navbar task to in review"
- Agent creates ANOTHER task with same name, then moves it
- User says: "Delete all tasks with name 'fix navbar'"
- Agent creates YET ANOTHER task instead of deleting

**Symptoms:**
```
User: "Create task X" → Agent: Creates task ✅
User: "Move this task" → Agent: Creates task + moves it ❌
User: "Delete this task" → Agent: Creates task + deletes it ❌
```

**Root Cause:**
The agent receives full conversation history including all previous user messages. The LLM may re-execute old user messages as new instructions, creating duplicates.

**INCORRECT Approaches (Don't Use):**

❌ **Filtering to only latest user message** (loses context):
```python
# WRONG - Loses context for "this task" references
user_items = [item for item in items if isinstance(item, UserMessageItem)]
latest_user_item = user_items[-1]
input_items = await simple_to_agent_input([latest_user_item])
```

❌ **Instruction-based filtering only** (unreliable):
```python
# WRONG - LLM may ignore instructions
instructions = "Only respond to the LATEST user message"
```

**CORRECT Solution: Use call_model_input_filter**
```python
from agents import RunConfig
from agents.run import CallModelData, ModelInputData

def filter_to_prevent_reexecution(data: CallModelData) -> ModelInputData:
    """
    Filter conversation history to prevent re-execution of old user messages.
    Keep all items for context (the LLM uses agent instructions to prevent re-execution).
    """
    items = data.model_data.input
    if not items:
        return data.model_data

    # Find the last user message
    last_user_idx = None
    for i in reversed(range(len(items))):
        item = items[i]
        if hasattr(item, "role") and item.role == "user":
            last_user_idx = i
            break

    if last_user_idx is None or last_user_idx == len(items) - 1:
        return data.model_data

    # Keep all items for context
    # The agent instructions tell the LLM to only respond to the latest user message
    logger.info(f"Total items: {len(items)}, latest user message at index: {last_user_idx}")

    return ModelInputData(
        input=items,  # Keep all items for context
        instructions=data.model_data.instructions
    )

# Use the filter
result = Runner.run_streamed(
    agent,
    input_items,  # Full conversation history
    context=agent_context,
    run_config=RunConfig(
        call_model_input_filter=filter_to_prevent_reexecution
    ),
)
```

**Agent Instructions (Critical):**
Your agent instructions MUST explicitly tell the LLM to only respond to the latest message:

```python
TEAMFLOW_AGENT_INSTRUCTIONS = """
**CRITICAL: ONLY respond to the LATEST user message**
- You will receive a conversation history with multiple user messages
- ONLY execute tools based on the LAST/RECENT user message
- Use previous messages ONLY for context (e.g., remembering task names, user preferences)
- NEVER re-execute actions from previous user messages - this creates duplicates!
"""
```

**Why This Works:**
- `call_model_input_filter` filters conversation history BEFORE it reaches the LLM
- Full conversation history is preserved for context (understanding "this task" references)
- Agent instructions tell the LLM to only execute tools for the latest message
- The combination of filter + instructions prevents duplicate execution

---

### ❌ Pitfall #17: Using previous_response_id with Unsupported Models

**Problem:**
- Chat history loading fails with "Failed to load conversation" error
- Loader turns off before AI message appears
- Error logs show issues with AgentContext creation

**Symptoms:**
```
[ChatKit respond] previous_response_id: some_id
[ChatKit respond] Error: 400 Bad Request
Failed to load conversation. We encountered an error. Reload to try again.
```

**Root Cause:**
The `previous_response_id` parameter is ONLY supported for:
- OpenAI Responses API
- OpenAI-hosted models (gpt-4o, gpt-4.1, etc.)

When using alternative models:
- OpenRouter (any model)
- Gemini 2.0 Flash via OpenRouter
- Custom model providers

The `previous_response_id` parameter is **NOT supported** and may cause errors.

**INCORRECT Code:**
```python
# ❌ WRONG - previous_response_id doesn't work with OpenRouter/Gemini
last_response_id = thread.metadata.get("last_response_id")

agent_context = AgentContext(
    thread=thread,
    store=self.store,
    request_context=context,
    previous_response_id=last_response_id,  # ❌ Not supported for OpenRouter!
)

result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
)
```

**CORRECT Code:**
```python
# ✅ CORRECT - Don't use previous_response_id for OpenRouter/Gemini
agent_context = AgentContext(
    thread=thread,
    store=self.store,
    request_response=context,
    # NOTE: No previous_response_id for OpenRouter/Gemini models
    # Rely on __fake_id__ replacement for unique message IDs instead
)

result = Runner.run_streamed(
    agent,
    input_items,
    context=agent_context,
)
```

**Alternative for OpenAI Models:**
If you ARE using OpenAI models (gpt-4o, gpt-4.1, etc.), you CAN use `previous_response_id`:

```python
# Only use with OpenAI Responses API
last_response_id = thread.metadata.get("last_response_id")

agent_context = AgentContext(
    thread=thread,
    store=self.store,
    request_response=context,
    previous_response_id=last_response_id,  # ✅ Only for OpenAI Responses API
)

result = Runner.run_streamed(
    agent,
    input_items,
    previous_response_id=last_response_id,  # ✅ Pass directly to Runner
    auto_previous_response_id=True,  # ✅ Auto-save new response ID
    context=agent_context,
)

# Save the new response ID for next turn
if result.last_response_id:
    thread.metadata["last_response_id"] = result.last_response_id
    await self.store.save_thread(thread, context=context)
```

**How to Detect Which Models Support It:**
- OpenAI Responses API (gpt-4.1-mini, gpt-4o-mini): ✅ Supported
- OpenRouter (any model): ❌ NOT supported
- Gemini (direct or via OpenRouter): ❌ NOT supported
- Custom model providers: ❌ NOT supported (check documentation)

**Workaround for Unsupported Models:**
Use `__fake_id__` replacement (Pitfall #15) to ensure each message gets a unique ID, preventing the overwriting issue that `previous_response_id` was meant to solve.

**Related:** OpenAI Agents SDK - Model Features documentation
