---
id: 0016
title: Chat message overwrite bug analysis
stage: misc
date: 2025-01-09T22:00:00Z
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: (CLI invocation via /sp.analyze)
command: /sp.analyze there is some problem in the chat i send a message to the assistant, it replies then i ageain sent it, but the reponse should be below my sent message but it rewrites the ai previous response, i tried alot of thing but its not fixed, in the chat history when i restore it there all the chat message stacked correctly, but not on actual one
labels: ["bug-analysis","chatkit","message-persistence","critical","streaming"]
links:
  spec: ../../specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - backend/app/chatkit/server.py
 - frontend/src/components/chat/ChatWidget.tsx
 - backend/app/agents/orchestrator.py
 - backend/app/services/chat_service.py
tests:
 - Bug analysis: Assistant responses streamed but never saved to ChatKit MemoryStore
 - Root cause identified: Missing add_thread_item() call for assistant messages
 - Fix approach: Collect streamed text and save as ResponseItem after streaming completes
---

## Prompt

there is some problem in the chat i send a message to the assistant, it replies then i ageain sent it, but the reponse should be below my sent message but it rewrites the ai previous response, i tried alot of thing but its not fixed, in the chat history when i restore it there all the chat message stacked correctly, but not on actual one

## Response snapshot

### Root Cause Identified: **CRITICAL BUG - Assistant Messages Not Persisted**

**The Problem:**
When users send consecutive messages in the chat widget, each new AI response **overwrites** the previous response instead of appearing below it. However, chat history restore shows all messages correctly stacked.

**Root Cause:**
In `backend/app/chatkit/server.py`, the `respond()` method:
1. ✅ **DOES** save user messages to the ChatKit MemoryStore (lines 437-448)
2. ✅ **DOES** stream assistant responses via `ResponseTextItem` (lines 770-773, 806-809)
3. ❌ **DOES NOT** save assistant responses to the ChatKit MemoryStore

The ChatKit React SDK expects the server to persist ALL messages to the thread store. When assistant messages aren't saved:
- Each new streamed response replaces the previous transient assistant message in the UI
- The ChatKit in-memory store only contains user messages
- Chat history restore works because it uses a different data source (ChatService/PostgreSQL) where messages ARE saved by `AgentOrchestrator`

### Evidence:

**User message IS saved** (lines 437-448 in server.py):
```python
user_item = UserMsg(
    id=user_item_id,
    thread_id=thread.id,
    role="user",
    content=input.content,
    created_at=datetime.utcnow(),
    inference_options={},
)
await self.store.add_thread_item(thread.id, user_item, context or {})
```

**Assistant response NEVER saved** (lines 770-773, 806-809):
```python
if event_type == "token":
    content = event_data.get("content", "")
    yield ResponseTextItem(text=content)  # ← Only yielded!
elif event_type == "response":
    content = event_data.get("content", "")
    yield ResponseTextItem(text=content)  # ← Only yielded!
# No call to store.add_thread_item() for assistant messages!
```

### Why Chat History Works But Live Chat Doesn't:

| Feature | Data Source | Assistant Messages Saved? | Behavior |
|---------|-------------|--------------------------|----------|
| **Live Chat (ChatKit)** | MemoryStore (in-memory) | ❌ No | New responses overwrite previous |
| **Chat History Restore** | ChatService (PostgreSQL) | ✅ Yes | All messages display correctly |

The `AgentOrchestrator.process_message()` correctly saves both user AND assistant messages to PostgreSQL via `ChatService`, but the ChatKit server doesn't persist assistant responses to its own MemoryStore.

### Recommended Fix:

Modify `backend/app/chatkit/server.py` in the `respond()` method:

1. **Collect the full response text** during streaming
2. **After streaming completes**, create a `ResponseItem` with role="assistant"
3. **Save it to the MemoryStore** using `await self.store.add_thread_item()`

```python
# After line 521 (streaming loop), collect response:
full_response_parts = []

async for event in stream_agent_response(agent_context, result):
    if isinstance(event, ResponseTextItem):
        full_response_parts.append(event.text)
    yield event

# After streaming completes, save assistant message:
if full_response_parts:
    from chatkit.server import ResponseItem as AssistantMsg
    import uuid

    assistant_item_id = f"assistant_{uuid.uuid4().hex[:16]}"
    assistant_item = AssistantMsg(
        id=assistant_item_id,
        thread_id=thread.id,
        role="assistant",
        content="".join(full_response_parts),
        created_at=datetime.utcnow(),
    )
    await self.store.add_thread_item(thread.id, assistant_item, context or {})
    logger.info(f"[ChatKit] Saved assistant message {assistant_item_id} to thread {thread.id}")
```

### Files to Modify:

1. **`backend/app/chatkit/server.py`** - `respond()` method (lines 393-571)
   - Add response text collection during streaming
   - Add assistant message persistence after streaming

### Impact:

- **Severity**: CRITICAL - Chat feature is functionally broken for multi-turn conversations
- **User Impact**: Users cannot have back-and-forth conversations; each new response erases the previous one
- **Scope**: Single focused fix in one method
- **Risk**: Low - Fix is well-contained and follows existing user message persistence pattern

## Outcome

- ✅ Impact: Root cause identified - assistant messages streamed but never persisted to ChatKit MemoryStore. Explains why chat history works (uses PostgreSQL) but live chat doesn't (uses in-memory store without assistant messages).
- 🧪 Tests: Analysis complete - bug is in `backend/app/chatkit/server.py` respond() method. Missing `add_thread_item()` call for assistant messages after streaming.
- 📁 Files: Analyzed server.py (respond method), ChatWidget.tsx (client), orchestrator.py (agent). Bug is in server streaming logic.
- 🔁 Next prompts: Implement fix by adding assistant message persistence in respond() method. Test with consecutive messages to verify all responses persist correctly.
- 🧠 Reflection: This is a classic "data source inconsistency" bug. ChatKit MemoryStore and ChatService/PostgreSQL are two separate persistence layers. The orchestrator correctly saves to PostgreSQL but ChatKit server doesn't save to its own MemoryStore. The ChatKit React SDK relies on server-side persistence for proper message rendering in multi-turn conversations.

## Evaluation notes (flywheel)

- Failure modes observed: Server implementation incomplete - only implemented half of the persistence contract (user messages saved, assistant messages not saved). The ChatKit protocol requires ALL messages to be persisted by the server for proper client-side rendering.
- Graders run and results (PASS/FAIL): Bug analysis: PASS - Root cause identified with specific file locations and line numbers. Fix approach validated against existing user message persistence pattern.
- Prompt variant (if applicable): User-reported bug with specific behavior description: "response should be below my sent message but it rewrites the ai previous response"
- Next experiment (smallest change to try): Implement the fix by adding assistant message persistence after streaming completes in the respond() method. This is a surgical fix following the existing pattern for user message persistence.
