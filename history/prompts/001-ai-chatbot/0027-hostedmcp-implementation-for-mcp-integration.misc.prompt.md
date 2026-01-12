---
id: 0027
title: hostedmcp-implementation-for-mcp-integration
stage: misc
date: 2026-01-11
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: owais_abdullah
command: (continuation from previous conversation)
labels: [mcp, openai-agents-sdk, integration, hostedmcp]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/app/agents/chatbot.py
 - backend/app/agents/orchestrator.py
 - backend/app/agents/HOSTEDMCP_IMPLEMENTATION.md
tests:
 - python3 -m py_compile app/agents/chatbot.py (PASS)
 - python3 -m py_compile app/agents/orchestrator.py (PASS)
---

## Prompt

(Continuation from previous conversation where we discovered HostedMCPTool as the correct approach for MCP integration with OpenAI Agents SDK. The user had found the HostedMCPTool example in the official OpenAI Agents SDK repository and requested implementation.)

## Response snapshot

Implemented MCP integration using OpenAI Agents SDK's built-in `HostedMCPTool` class, which is the recommended approach for connecting MCP servers to agents. This replaces the manual tool wrapper approach that had issues with Windows/WSL async event loops.

**Key Changes:**

1. **Updated `app/agents/chatbot.py`:**
   - Changed `create_chatbot_agent()` from `async def` to `def` (synchronous)
   - Added `HostedMCPTool` import
   - Added `mcp_server_url` parameter (default: "http://127.0.0.1:8001/mcp")
   - Replaced manual tool list with `HostedMCPTool` configuration:
     ```python
     tools=[
         HostedMCPTool(
             tool_config={
                 "type": "mcp",
                 "server_label": "teamflow",
                 "server_url": mcp_server_url,
                 "require_approval": "never",
             }
         )
     ]
     ```

2. **Updated `app/agents/orchestrator.py`:**
   - Made `get_agent()` synchronous (removed `async def`)
   - Removed `await` from `create_chatbot_agent()` call
   - Updated call site: `agent = self.get_agent()` instead of `agent = await self.get_agent()`

3. **Created documentation:**
   - Added `HOSTEDMCP_IMPLEMENTATION.md` with architecture diagram, benefits of HostedMCPTool over manual wrappers, and deployment notes.

**Benefits of HostedMCPTool:**
- Built-in OpenAI Agents SDK class (recommended approach)
- Auto-discovers all 21 tools from MCP server
- Handles connection management internally
- Simpler, more maintainable code
- No async session management issues

## Outcome

- ✅ Impact: **High** - Proper MCP integration using official SDK patterns, eliminating Windows/WSL async issues
- 🧪 Tests: **Partial** - Syntax verified with py_compile, runtime testing pending (requires proper Linux environment)
- 📁 Files: **3 modified** - chatbot.py (HostedMCPTool integration), orchestrator.py (synchronous updates), HOSTEDMCP_IMPLEMENTATION.md (new documentation)
- 🔁 Next prompts: None - implementation complete, ready for deployment testing
- 🧠 Reflection: HostedMCPTool is the correct, built-in way to integrate MCP servers with OpenAI Agents SDK. The manual wrapper approach was overly complex and prone to environment-specific issues.

## Evaluation notes (flywheel)

- Failure modes observed: Windows/WSL virtual environment IO errors prevented runtime testing (`.venv/Lib` directory removal failed)
- Graders run and results (PASS/FAIL): N/A - syntax validation passed
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Deploy to HuggingFace Spaces (Linux environment) to verify MCP server connection and agent tool usage
