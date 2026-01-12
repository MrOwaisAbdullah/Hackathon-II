# Quick Start: MCP Integration Testing

## Prerequisites

The MCP integration requires **two servers** to be running:

1. **MCP Server** (port 8001) - Exposes tools to the agent
2. **FastAPI Backend** (port 8000) - Main API server

## Starting the Servers

### Option 1: Single Command (Recommended - MCP Auto-Starts)

```cmd
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

**The MCP server now starts automatically in the background when FastAPI starts!**

You'll see logs like:
```
[lifespan] Starting up application...
[lifespan] Starting MCP server as background task...
[lifespan] Starting MCP server on http://127.0.0.1:8001/mcp
[lifespan] MCP server started (background)
```

### Option 2: Use the startup script

```cmd
cd backend
start-backend.bat
```

### Option 3: Start manually (if needed for debugging)

**Terminal 1 - MCP Server:**
```cmd
cd backend
.venv\Scripts\python.exe -m app.mcp.server
```

**Terminal 2 - FastAPI Backend:**
```cmd
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

## Running the Tests

Once both servers are running:

```cmd
cd backend
.venv\Scripts\python.exe test_mcp_integration.py
```

## Expected Output

```
============================================================
MCPServerStreamableHttp Integration Test
============================================================

============================================================
Test 1: MCP Server Direct Connection
============================================================
✅ MCP Server is running
✅ Found 21 tools

============================================================
Test 2: Agent Creation with MCPServerStreamableHttp (Context Manager)
============================================================
⏳ Creating agent context...
✅ Agent created: teamflow-ai
✅ MCP servers configured: 1
✅ MCP server name: TeamFlow MCP Server
✅ MCP server URL: http://127.0.0.1:8001/mcp
✅ Cache tools list: True

============================================================
Test 3: Agent Simple Query (Context Manager)
============================================================
⏳ Creating agent context...
⏳ Running simple query...
✅ Agent responded:
   Hello! I'm TeamFlow AI, your intelligent assistant...

============================================================
Test Summary
============================================================
Total tests: 3
✅ Passed: 3
❌ Failed: 0

🎉 All tests passed!
```

## Troubleshooting

### "MCP server returned status 406" or "Connection refused"

**Cause:** MCP server is not running on port 8001.

**Solution:** Start the MCP server:
```cmd
.venv\Scripts\python.exe -m app.mcp.server
```

### "Server not initialized. Make sure you call `connect()` first."

**Cause:** Using old `create_chatbot_agent()` function instead of `create_chatbot_agent_context()`.

**Solution:** Update your code to use the context manager:
```python
# OLD (wrong):
agent = await create_chatbot_agent()

# NEW (correct):
async with create_chatbot_agent_context() as agent:
    # Use agent here
    result = await Runner.run(agent, "Hello!")
```

### "ModuleNotFoundError: No module named 'agents'"

**Cause:** Dependencies not installed.

**Solution:** Install dependencies:
```cmd
uv sync
```

## Architecture Changes

### Before (Incorrect)
```python
# Old approach - MCP server not connected
agent = await create_chatbot_agent()
result = await Runner.run(agent, "Hello!")
# Error: Server not initialized
```

### After (Correct)
```python
# New approach - MCP server connected via context manager
async with create_chatbot_agent_context() as agent:
    result = await Runner.run(agent, "Hello!")
    # Works! MCP server is connected
```

### Why the Context Manager?

`MCPServerStreamableHttp` from the OpenAI Agents SDK requires:
1. Connection to the MCP server before use
2. Disconnection when done

The context manager (`async with`) handles this automatically:
- Connects when entering the context
- Disconnects when exiting the context
- Ensures proper cleanup even if errors occur

## Files Modified

- `app/agents/chatbot.py` - Added `create_chatbot_agent_context()` function
- `app/agents/orchestrator.py` - Updated to use context manager
- `app/agents/__init__.py` - Exported new context manager function
- `test_mcp_integration.py` - Updated to use context manager

## Next Steps

1. Start both servers using `start-backend.bat`
2. Run `test_mcp_integration.py` to verify the integration
3. Test the agent with actual tool usage (create tasks, list projects, etc.)
