# MCP Integration Testing Guide

## Quick Start

### Option 1: Windows (Recommended for Development)

1. **Open two terminals:**

   **Terminal 1 - Start MCP Server:**
   ```cmd
   cd backend
   .venv\Scripts\python.exe -m app.mcp.server
   ```

   **Terminal 2 - Run Test:**
   ```cmd
   cd backend
   .venv\Scripts\python.exe test_mcp_integration.py
   ```

### Option 2: Automated Test (Windows)

Double-click the batch file:
```cmd
test_mcp_integration.bat
```

This will:
1. Start the MCP server in a new window
2. Wait 10 seconds for it to start
3. Run the integration test
4. Display results

### Option 3: Production (HuggingFace Spaces / Linux)

```bash
# Terminal 1: Start MCP server
cd backend
python -m app.mcp.server

# Terminal 2: Run test
cd backend
python test_mcp_integration.py
```

## What the Test Does

The integration test (`test_mcp_integration.py`) performs three tests:

### Test 1: MCP Server Direct Connection
- Connects to the MCP server via HTTP
- Lists all available tools
- Verifies tools are correctly registered

**Expected Result:** ✅ MCP Server is running with 21 tools

### Test 2: Agent Creation with MCPServerStreamableHttp
- Creates an agent using `create_chatbot_agent()`
- Verifies `MCPServerStreamableHttp` is configured
- Checks MCP server URL and settings

**Expected Result:** ✅ Agent created with MCPServerStreamableHttp

### Test 3: Agent Simple Query
- Sends a simple greeting to the agent
- Verifies the agent can respond

**Expected Result:** ✅ Agent responds to greeting

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

📋 Available Tools:
   1. search_knowledge_base: Search the TeamFlow knowledge base...
   2. add_task: Create a new task in TeamFlow...
   3. list_tasks: List tasks in TeamFlow...
   ... (and 18 more)

============================================================
Test 2: Agent Creation with MCPServerStreamableHttp
============================================================
⏳ Creating agent...
✅ Agent created: teamflow-ai
✅ MCP servers configured: 1
✅ MCP server name: TeamFlow MCP Server
✅ MCP server URL: http://127.0.0.1:8001/mcp
✅ Cache tools list: True

============================================================
Test 3: Agent Simple Query (No Tools)
============================================================
⏳ Creating agent...
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

### MCP Server Not Starting

**Error:** `httpx.ConnectError: All connection attempts failed`

**Solution:** Make sure the MCP server is running before starting the test:
```cmd
# Terminal 1
cd backend
.venv\Scripts\python.exe -m app.mcp.server
```

### Tools Not Loading (0 Tools)

**Error:** `Agent: teamflow-ai, Tools: 0`

**Solution:** This was the old issue with `HostedMCPTool`. Make sure you're using `MCPServerStreamableHttp`:
- Check `app/agents/chatbot.py` uses `MCPServerStreamableHttp`
- Agent should have `mcp_servers=[server]` not `tools=[...]`

### WSL Cannot Connect to Windows Server

**Error:** Connection refused from WSL to localhost:8001

**Solution:** The Windows server listens on `127.0.0.1` which WSL cannot access.
- Use Windows terminals for testing (recommended)
- Or run the test on HuggingFace Spaces (Linux environment)

## Running pytest Tests

For unit tests of individual MCP tools:

```bash
cd backend
pytest tests/unit/test_mcp_tools.py -v
```

For integration tests:

```bash
cd backend
pytest tests/integration/test_mcp_streamablehttp.py -v
```

**Note:** Integration tests require the MCP server to be running first.

## Architecture Verification

To verify the correct MCP integration class is being used:

1. Check `app/agents/chatbot.py`:
   ```python
   # Should be using MCPServerStreamableHttp
   from agents.mcp import MCPServerStreamableHttp

   # Agent creation should use mcp_servers parameter
   agent = Agent(
       name="teamflow-ai",
       ...
       mcp_servers=[mcp_server],  # NOT tools=[...]
   )
   ```

2. Check that `HostedMCPTool` is NOT being used:
   - `HostedMCPTool` is for hosted/remote MCP servers (HTTPS)
   - `MCPServerStreamableHttp` is for local/HTTP MCP servers
   - Our server is at `http://127.0.0.1:8001/mcp` (local HTTP)

## Deployment Checklist

Before deploying to HuggingFace Spaces:

- [ ] MCP server uses HTTP transport (port 8001)
- [ ] Agent uses `MCPServerStreamableHttp` (NOT `HostedMCPTool`)
- [ ] Test passes in local Windows environment
- [ ] All 21 tools are listed by MCP server
- [ ] Agent can respond to simple queries
- [ ] `mcp_servers` parameter is used (not `tools`)
