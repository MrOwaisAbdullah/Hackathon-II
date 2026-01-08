# OpenAI Agents SDK Streaming Fix

## Problem

The error `"object RunResultStreaming can't be used in 'await' expression"` occurred because `Runner.run_streamed()` was being incorrectly awaited.

## Root Cause

**`Runner.run_streamed()` is a SYNCHRONOUS method** that returns a `RunResultStreaming` object immediately. It does NOT return a coroutine, so it cannot be awaited.

The actual streaming happens when you iterate over `result.stream_events()`, which IS an async generator.

## Incorrect Pattern (What you had)

```python
# ❌ WRONG - This causes the error
result = await Runner.run_streamed(
    self.assistant_agent,
    user_message,
    context=agent_context
)

# ❌ WRONG - Can't iterate over RunResultStreaming directly
async for chunk in result:
    ...
```

## Correct Pattern (What it should be)

```python
# ✅ CORRECT - Call run_streamed() synchronously
result = Runner.run_streamed(
    self.assistant_agent,
    user_message,
    context=agent_context
)

# ✅ CORRECT - Iterate over stream_events() which is async
async for event in result.stream_events():
    # Process events
    if event.type == "raw_response_event":
        # Handle response events
        ...
```

## Key Points

1. **`Runner.run_streamed()` is synchronous** - It returns a `RunResultStreaming` object immediately, not a coroutine
2. **`result.stream_events()` is async** - This is where the actual streaming happens
3. **The pattern is always**:
   ```python
   result = Runner.run_streamed(...)  # No await
   async for event in result.stream_events():  # Async iteration
       # Process events
   ```

## OpenAI Agents SDK Methods

From the official documentation:

| Method | Type | Returns |
|--------|------|---------|
| `Runner.run()` | Async coroutine | `RunResult` (use `await`) |
| `Runner.run_sync()` | Synchronous | `RunResult` (no `await`) |
| `Runner.run_streamed()` | Synchronous | `RunResultStreaming` (no `await`) |

## Fixed Locations

### Location 1: `respond()` method (line 371)
**Before:**
```python
result = await Runner.run_streamed(
    self.assistant_agent,
    user_message,
    context=agent_context
)
```

**After:**
```python
result = Runner.run_streamed(
    self.assistant_agent,
    user_message,
    context=agent_context
)
```

### Location 2: `_stream_agent_response_simple()` method (line 532)
**Before:**
```python
result = Runner.run_streamed(
    self.assistant_agent,
    message,
)
async for chunk in result:  # ❌ Wrong iteration
    ...
```

**After:**
```python
result = Runner.run_streamed(
    self.assistant_agent,
    message,
)
async for event in result.stream_events():  # ✅ Correct iteration
    ...
```

## Usage with ChatKit SDK

The `stream_agent_response()` function from ChatKit SDK expects a `RunResultStreaming` object and correctly calls `result.stream_events()` internally:

```python
from chatkit.agents import stream_agent_response, AgentContext

# In your respond() method:
result = Runner.run_streamed(
    self.assistant_agent,
    user_message,
    context=agent_context
)

# ChatKit SDK handles the streaming correctly
async for event in stream_agent_response(agent_context, result):
    yield event
```

## Event Types to Handle

When streaming events, you'll encounter these event types:

- `raw_response_event` - Raw LLM response events (text deltas, annotations, etc.)
- `run_item_stream_event` - Agent run items (tool calls, handoffs, etc.)
- Custom events from `AgentContext` (widgets, workflows, etc.)

Example:
```python
async for event in result.stream_events():
    if event.type == "raw_response_event":
        if event.data.type == "response.output_text.delta":
            # Stream text delta
            print(event.data.delta, end="", flush=True)
```

## Testing

After applying this fix:

1. Test streaming responses work correctly
2. Verify text appears incrementally (not all at once)
3. Check that errors are properly handled
4. Ensure ChatKit events are yielded correctly

## References

- [OpenAI Agents SDK - Running Agents](https://openai.github.io/openai-agents-python/running_agents/)
- [OpenAI Agents SDK - Streaming](https://openai.github.io/openai-agents-python/streaming/)
- [ChatKit Python SDK - Agents Module](https://github.com/openai/chatkit-python)
