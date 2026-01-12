# MCP Context Manager Fix - Complete

## Summary

Fixed the "Agent not initialized" error by updating `chatkit/server.py` to use the new `create_chatbot_agent_context()` async context manager pattern.

## The Problem

The old code tried to access `self.assistant_agent` as a property, but the agent was not initialized because we changed the architecture to use lazy initialization with an async context manager.

## The Solution

Updated the `process()` method in `chatkit/server.py` to use `async with create_chatbot_agent_context() as agent:` which properly:
1. Connects to the MCP server when entering the context
2. Creates the agent
3. Streams all responses within the context
4. Disconnects from the MCP server when exiting

## Files Modified

1. **`app/agents/chatbot.py`**
   - Added `create_chatbot_agent_context()` - async context manager
   - Deprecated `create_chatbot_agent()` (marked as legacy)

2. **`app/agents/orchestrator.py`**
   - Updated to use `create_chatbot_agent_context()` in `process_message()`

3. **`app/chatkit/server.py`**
   - Updated `process()` method to use context manager pattern
   - Removed lazy initialization property
   - All streaming now happens within the MCP server context

4. **`app/agents/__init__.py`**
   - Exported both `create_chatbot_agent_context()` (new) and `create_chatbot_agent()` (legacy)

## How to Test

### Quick Start (Auto-Starting MCP Server)

**Single Command - Start FastAPI (MCP server starts automatically):**
```cmd
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

The MCP server now starts automatically in the background when FastAPI starts!

### Manual Start (If Needed)

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

### Step 3: Run Integration Test
```cmd
cd backend
.venv\Scripts\python.exe test_mcp_integration.py
```

## Expected Results

### Test 1: MCP Server Direct Connection
- May show 406 (expected - raw HTTP request vs SDK protocol)
- This is OK - the SDK uses a different protocol

### Test 2: Agent Creation
```
✅ Agent created: teamflow-ai
✅ MCP servers configured: 1
✅ MCP server name: TeamFlow MCP Server
✅ MCP server URL: http://127.0.0.1:8001/mcp
✅ Cache tools list: True
```

### Test 3: Simple Query
- May show 429 rate limit (OpenRouter free tier)
- This is OK - add your own API key to `.env` if needed

## Key Architecture Change

### Before (Wrong)
```python
# Agent created but MCP server NOT connected
agent = await create_chatbot_agent()
result = await Runner.run(agent, "Hello!")
# Error: Server not initialized
```

### After (Correct)
```python
# MCP server connected within context manager
async with create_chatbot_agent_context() as agent:
    result = await Runner.run(agent, "Hello!")
    # Works! Tools are loaded
```

## Why Context Manager?

`MCPServerStreamableHttp` requires explicit connection/disconnection:
- **Connect**: When entering the context (`async with`)
- **Disconnect**: When exiting the context (after `with` block)
- **Tool Discovery**: Happens after connection

Without the context manager, the agent is created but the MCP server is never connected, resulting in:
- 0 tools available
- "Server not initialized" errors

## Quick Start Script

For convenience, use `start-backend.bat` to start both servers:

```cmd
start-backend.bat
```

This will:
1. Start MCP Server on port 8001 (in new window)
2. Start FastAPI Backend on port 8000 (in current window)

## Troubleshooting

### "Agent not initialized" Error
**Cause:** Code trying to access `assistant_agent` property directly

**Solution:** Use `async with create_chatbot_agent_context() as agent:` pattern

### Port 8001 Already in Use
**Cause:** Previous MCP server still running

**Solution:** Run `kill-mcp-port.bat` or:
```cmd
netstat -aon | find ":8001"
taskkill /F /PID <PID>
```

### 429 Rate Limit
**Cause:** OpenRouter free tier rate limit

**Solution:** Wait a few minutes or add your own API key to `.env`:
```env
OPENROUTER_API_KEY=your_key_here
```

## Next Steps

1. ✅ Restart both servers
2. ✅ Run `test_mcp_integration.py` to verify
3. ✅ Test the chatbot in the browser
4. ✅ Verify MCP tools are working (create tasks, list projects, etc.)
