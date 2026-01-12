---
id: 0028
title: mcp-streamablehttp-correction
stage: misc
date: 2026-01-11
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: owais_abdullah
command: (continuation from previous conversation)
labels: [mcp, openai-agents-sdk, integration, correction, streamablehttp]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/app/agents/chatbot.py
 - backend/app/agents/orchestrator.py
 - backend/app/chatkit/server.py
 - backend/app/agents/MCP_STREAMABLEHTTP_IMPLEMENTATION.md
tests:
 - python3 -m py_compile app/agents/chatbot.py (PASS)
 - python3 -m py_compile app/agents/orchestrator.py (PASS)
 - python3 -m py_compile app/chatkit/server.py (PASS)
---

## Prompt

(After implementing HostedMCPTool, we discovered that the agent showed "Tools: 0" - no tools were being loaded from the MCP server. Investigation revealed that HostedMCPTool is designed for hosted/remote MCP servers accessed through OpenAI's infrastructure, NOT for local HTTP MCP servers.)

## Response snapshot

**Critical Discovery:** `HostedMCPTool` is designed for **hosted/remote MCP servers** (HTTPS URLs like `https://gitmcp.io/openai/codex`), **NOT** for local MCP servers running on `http://127.0.0.1:8001/mcp`.

For **local HTTP MCP servers**, we must use **`MCPServerStreamableHttp`** instead.

**Key Differences:**

| Feature | HostedMCPTool (WRONG for local) | MCPServerStreamableHttp (CORRECT) |
|---------|-------------------------------|-----------------------------------|
| Use Case | Hosted/remote MCP servers | Local/remote HTTP servers |
| Transport | HTTPS via OpenAI infrastructure | Direct HTTP connection |
| Parameter | `tools=[HostedMCPTool(...)]` | `mcp_servers=[server]` |
| Example URL | `https://gitmcp.io/openai/codex` | `http://127.0.0.1:8001/mcp` |

**Changes Made:**

1. **`app/agents/chatbot.py`:**
   - Changed import from `HostedMCPTool` to `MCPServerStreamableHttp`
   - Made `create_chatbot_agent()` async again
   - Updated agent creation:
     ```python
     mcp_server = MCPServerStreamableHttp(
         name="TeamFlow MCP Server",
         params={"url": mcp_server_url},
         cache_tools_list=True,
     )
     agent = Agent(
         name="teamflow-ai",
         instructions=instructions or TEAMFLOW_AGENT_INSTRUCTIONS,
         model=model_instance,
         mcp_servers=[mcp_server],  # Note: mcp_servers, not tools
     )
     ```

2. **`app/agents/orchestrator.py`:**
   - Made `get_agent()` async again
   - Updated call site to use `await self.get_agent()`

3. **`app/chatkit/server.py`:**
   - Implemented lazy initialization pattern
   - Added `async def _get_assistant_agent()` method
   - Agent created on first use instead of in `__init__()`

4. **Documentation:**
   - Created `MCP_STREAMABLEHTTP_IMPLEMENTATION.md` with correct implementation details
   - Deleted obsolete `HOSTEDMCP_IMPLEMENTATION.md`

## Outcome

- ✅ Impact: **Critical** - Fixed incorrect MCP integration class that was preventing tools from loading
- 🧪 Tests: **Partial** - Syntax verified with py_compile, runtime testing pending
- 📁 Files: **4 modified** - chatbot.py (MCPServerStreamableHttp), orchestrator.py (async), chatkit/server.py (lazy init), MCP_STREAMABLEHTTP_IMPLEMENTATION.md (new docs)
- 🔁 Next prompts: None - implementation corrected
- 🧠 Reflection: Important distinction: `HostedMCPTool` is for OpenAI-hosted MCP servers (external services), while `MCPServerStreamableHttp` is for your own local/remote HTTP MCP servers. The tools weren't loading because `HostedMCPTool` routes through OpenAI's infrastructure which doesn't work with localhost MCP servers.

## Evaluation notes (flywheel)

- Failure modes observed: Windows/WSL virtual environment IO errors prevented runtime testing; initial implementation with `HostedMCPTool` resulted in 0 tools being loaded
- Graders run and results (PASS/FAIL): N/A - syntax validation passed
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Deploy to HuggingFace Spaces (Linux environment) to verify MCP server connection and confirm all 21 tools are loaded correctly
