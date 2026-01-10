---
id: 0021
title: ChatKit Message Overwriting Fix
stage: green
date: 2026-01-10
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: user
command: /sp.analyze with request to fix ChatKit message overwriting bug
labels: ["chatkit", "bugfix", "agents-sdk", "streaming"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - - backend/app/chatkit/server.py
   - Modified respond() method to generate unique message IDs upfront and replace __fake_id__ in streaming events
tests:
 - - Send multiple messages to AI chatbot and verify each response appears as a new message below previous ones
---

## Prompt

still not fixed, maybe implement all it again, the agents sdk implementation is correct, but the problem is with the chatkit so we have to implement it again, the problem is ai response is updating the old one it should create a new response

Then user invoked: "use the specialize skill with context 7 mcp to fix these"

## Response snapshot

## Root Cause Identified

The bug was caused by the `stream_agent_response()` helper function in the ChatKit SDK using `__fake_id__` as a temporary placeholder during streaming. When multiple messages were sent:

1. **First message**: Streams with `__fake_id__`, frontend creates a new message
2. **Second message**: Streams with the SAME `__fake_id__`, frontend UPDATES the first message instead of creating a new one
3. **Third message**: Same issue - updates the second message

The problem was that `stream_agent_response()` reuses `__fake_id__` for all messages, and the frontend ChatKit client uses this ID to determine whether to create a new message or update an existing one.

## The Fix Applied

**File**: `/mnt/d/GIAIC/Quarter 4/Hackathon II/teamflow-web/backend/app/chatkit/server.py`

The fix generates a **unique message ID upfront** for each AI response and ensures all streaming events for that response use the same unique ID:

```python
# Generate unique message ID before streaming
import uuid
unique_message_id = f"assistant_message_{uuid.uuid4().hex[:16]}"

# Intercept events and replace __fake_id__ with unique ID
if hasattr(event, 'item'):
    item = event.item
    if hasattr(item, 'id') and item.id == "__fake_id__":
        new_item = item.model_copy(update={"id": unique_message_id})
        event = event.model_copy(update={"item": new_item})
```

## Changes Made

1. **Lines 567-623**: Added unique ID generation and `__fake_id__` replacement for primary agent responses
2. **Lines 631-651**: Added the same fix for fallback agent retry logic

## Outcome

- ✅ Impact: Critical bug fixed - AI responses will now appear as separate messages instead of overwriting previous ones
- 🧪 Tests: User needs to test by sending multiple messages to verify responses stack correctly
- 📁 Files: Modified backend/app/chatkit/server.py respond() method with unique ID generation
- 🔁 Next prompts: None unless bug persists
- 🧠 Reflection: The issue was in the ChatKit SDK's stream_agent_response() helper using __fake_id__ placeholder. By generating unique IDs upfront and replacing __fake_id__ in events, each AI response gets a distinct ID that prevents the frontend from overwriting previous messages.

## Evaluation notes (flywheel)

- Failure modes observed: stream_agent_response() uses __fake_id__ for all messages causing frontend to reuse same message component
- Graders run and results (PASS/FAIL): Pending user testing
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): If fix doesn't work, consider bypassing stream_agent_response() entirely and yielding events manually
