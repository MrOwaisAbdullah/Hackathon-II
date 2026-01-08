# Skills Update Summary - ChatKit Integration Journey

This document summarizes the key lessons learned from implementing ChatKit integration with OpenAI Agents SDK, RAG pipeline, and MCP tools.

## Date: 2025-01-08

## Skills Updated

### 1. openai-chatkit-integration
**Path:** `.claude/skills/openai-chatkit-integration/`

**Key Updates:**
- Added comprehensive pitfalls section with 8 critical issues
- Created IMPLEMENTATION_GUIDE.md with step-by-step setup
- Created LEARNINGS.md with debugging journey summary
- Updated server.py template with correct implementation
- Updated chatkit-protocol.md with accurate protocol details

**Most Critical Learning:**
- Pass `input_items` (conversation history) NOT `user_message` to `Runner.run_streamed()`
- This was the #1 issue causing agent to only respond to greetings

### 2. openai-agents-sdk-gemini
**Path:** `.claude/skills/openai-agents-sdk-gemini/`

**Key Updates:**
- Added "Critical Pitfalls & Solutions" section
- Corrected misunderstanding about litellm prefix (SDK does support it)
- Emphasized using `OpenAIChatCompletionsModel` wrapper
- Added quick setup pattern for OpenRouter
- Added error message reference table

**Most Critical Learning:**
- Always wrap AsyncOpenAI client with `OpenAIChatCompletionsModel` for non-OpenAI providers
- Call `set_default_openai_api("chat_completions")` for OpenRouter/Gemini
- Call `set_tracing_disabled(True)` when not using OpenAI

### 3. rag-pipeline-builder
**Path:** `.claude/skills/rag-pipeline-builder/`

**Key Updates:**
- Enhanced production lessons learned section
- Added Agent SDK integration guidance
- Added OpenRouter configuration example
- Clarified embedding model selection (free models don't support embeddings)

**Most Critical Learning:**
- Free chat models like `mistralai/devstral-2512:free` do NOT support embeddings
- Always use dedicated embedding models like `openai/text-embedding-3-small`

### 4. mcp-builder
**Path:** `.claude/skills/mcp-builder/`

**Key Updates:**
- Added FastMCP integration examples
- Added tool design best practices
- Added testing patterns with Agent SDK
- Added actionable error message patterns
- Fixed duplicate "# Process" header

**Most Critical Learning:**
- Clear tool descriptions help agents understand when to use each tool
- Use Pydantic for input validation
- Provide actionable error messages that guide agents toward solutions

## The Complete Correct Pattern

### For OpenRouter + OpenAI Agents SDK:

```python
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    set_default_openai_api,
    set_tracing_disabled,
)
from openai import AsyncOpenAI

# Step 1: Disable tracing (not using OpenAI)
set_tracing_disabled(True)

# Step 2: Set API type for OpenRouter compatibility
set_default_openai_api("chat_completions")

# Step 3: Create custom OpenAI client
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

# Step 4: Wrap with OpenAIChatCompletionsModel
model = OpenAIChatCompletionsModel(
    openai_client=client,
    model="mistralai/devstral-2512:free",
)

# Step 5: Create agent with MCP tools
agent = Agent(
    name="assistant",
    instructions="You are a helpful assistant.",
    model=model,
    tools=MCP_TOOLS,  # Tools from FastMCP server
)
```

### For RAG with OpenRouter:

```python
# For embeddings - use dedicated embedding model
response = await client.embeddings.create(
    model="openai/text-embedding-3-small",  # ✅ Embedding model
    input=texts,
)

# NOT the chat model:
# model="mistralai/devstral-2512:free"  # ❌ Doesn't support embeddings
```

### For ChatKit Integration:

```python
# Load conversation history
items_page = await store.load_thread_items(thread.id, ...)

# Convert to agent input format
input_items = await simple_to_agent_input(items_page.data)

# CRITICAL: Pass conversation history, not just message
result = Runner.run_streamed(
    agent,
    input_items,  # ✅ Full context
    context=agent_context
)
```

## Error Messages Reference

| Error Message | Cause | Solution |
|--------------|-------|----------|
| `Unknown prefix: mistralai` | Direct model string without wrapper | Use `OpenAIChatCompletionsModel` wrapper |
| `404 Not Found` from LLM API | Wrong API type | Call `set_default_openai_api("chat_completions")` |
| `Model does not support embeddings` | Using chat model for embeddings | Use `openai/text-embedding-3-small` |
| Agent only responds to greetings | Passing message string instead of input_items | Pass conversation history via `simple_to_agent_input()` |
| Tracing authentication error | Not disabling tracing | Call `set_tracing_disabled(True)` |

## Summary of All Issues Encountered

1. **ChatKit SDK Integration** (8 pitfalls documented)
2. **OpenAI Agents SDK with OpenRouter** (5 pitfalls documented)
3. **RAG Pipeline with OpenRouter** (4 pitfalls documented)
4. **MCP Tool Integration** (4 pitfalls documented)

**Total: 21 documented pitfalls with solutions**

## Files Created/Updated

### New Files Created:
- `openai-chatkit-integration/LEARNINGS.md`
- `openai-chatkit-integration/assets/IMPLEMENTATION_GUIDE.md`

### Files Updated:
- `openai-chatkit-integration/SKILL.md`
- `openai-chatkit-integration/assets/backend/server.py`
- `openai-chatkit-integration/assets/backend/pyproject.toml`
- `openai-chatkit-integration/references/chatkit-protocol.md`
- `openai-agents-sdk-gemini/skills.md`
- `rag-pipeline-builder/SKILL.md`
- `mcp-builder/SKILL.md`

## Result

All skills now contain production-ready, battle-tested patterns based on real-world debugging experience. Future implementations can reference these skills to avoid the same pitfalls.
