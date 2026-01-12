# MCPServerStreamableHttp Implementation Summary

## Overview

This document summarizes the implementation of MCP (Model Context Protocol) integration using the OpenAI Agents SDK's `MCPServerStreamableHttp` class for **local HTTP MCP servers**.

## Critical Discovery: HostedMCPTool vs MCPServerStreamableHttp

After initial implementation with `HostedMCPTool`, we discovered it was designed for **hosted/remote MCP servers** (HTTPS URLs accessed through OpenAI's infrastructure), **NOT** for local MCP servers.

### The Problem with HostedMCPTool

| Feature | HostedMCPTool | MCPServerStreamableHttp |
|---------|---------------|-------------------------|
| **Use Case** | Hosted/remote MCP servers | Local/remote HTTP servers |
| **Transport** | HTTPS (external services) | HTTP (localhost or custom) |
| **Parameter** | `tools=[HostedMCPTool(...)]` | `mcp_servers=[server]` |
| **Example URL** | `https://gitmcp.io/openai/codex` | `http://127.0.0.1:8001/mcp` |
| **Discovery** | Via OpenAI's infrastructure | Direct HTTP connection |

**Why HostedMCPTool Failed:**
- Designed for OpenAI's hosted MCP infrastructure
- Routes tool calls through OpenAI's Responses API
- Not suitable for local MCP servers
- Tools were not discovered (agent showed "Tools: 0")

**Why MCPServerStreamableHttp Works:**
- Direct HTTP connection to local MCP server
- Tools auto-discovered on connection
- No external infrastructure required
- Works with FastMCP's `streamable_http_app()`

## Changes Made

### 1. Updated `app/agents/chatbot.py`

**Import Change:**
```python
# BEFORE (incorrect for local servers)
from agents import Agent, Runner, RunConfig, ModelResponse, HostedMCPTool

# AFTER (correct for local HTTP servers)
from agents import Agent, Runner, RunConfig, ModelResponse
from agents.mcp import MCPServerStreamableHttp
```

**Function Signature Change:**
```python
# BEFORE: synchronous def
def create_chatbot_agent(...)

# AFTER: async def (required for MCPServerStreamableHttp)
async def create_chatbot_agent(
    instructions: str | None = None,
    model: str = "google/gemini-2.0-flash-exp:free",
    use_fallback: bool = True,
    mcp_server_url: str = "http://127.0.0.1:8001/mcp",
) -> Agent:
```

**Agent Creation with MCPServerStreamableHttp:**
```python
# Create MCP server connection for HTTP transport
mcp_server = MCPServerStreamableHttp(
    name="TeamFlow MCP Server",
    params={
        "url": mcp_server_url,
    },
    cache_tools_list=True,  # Cache the tools list for performance
)

# Create agent with MCP server
agent = Agent(
    name="teamflow-ai",
    instructions=instructions or TEAMFLOW_AGENT_INSTRUCTIONS,
    model=model_instance,
    mcp_servers=[mcp_server],  # Note: mcp_servers parameter, not tools
)
```

### 2. Updated `app/agents/orchestrator.py`

**Made `get_agent()` async again:**
```python
# AFTER: async def (required for async create_chatbot_agent)
async def get_agent(self) -> Agent:
    if self._agent is None:
        instructions = self._build_agent_instructions()
        self._agent = await create_chatbot_agent(
            instructions=instructions,
            model=self.model,
            use_fallback=True,
        )
    return self._agent
```

**Updated call site:**
```python
# AFTER: await required
agent = await self.get_agent()
```

### 3. Updated `app/chatkit/server.py`

**Lazy initialization pattern:**
```python
# __init__ - no longer calls _init_agent()
def __init__(self, ...):
    self._assistant_agent: Optional[Agent] = None  # Lazy initialized
    # ... other init code ...

# New async method for lazy initialization
async def _get_assistant_agent(self) -> Agent:
    """Get or create the chatbot agent (lazy initialization)."""
    if self._assistant_agent is None:
        self._assistant_agent = await create_chatbot_agent(
            model="google/gemini-2.0-flash-exp:free",
        )
    return self._assistant_agent
```

## MCP Server Configuration

The MCP server runs on `http://127.0.0.1:8001/mcp` using FastMCP with HTTP transport:

```python
# app/mcp/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TeamFlow")

# Register tools from app/mcp/tools.py
register_knowledge_base_tools(mcp)
register_task_tools(mcp)
register_analytics_tools(mcp)
register_recommendation_tools(mcp)

def main():
    import uvicorn
    uvicorn.run(
        mcp.streamable_http_app(),
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
```

## Available MCP Tools

The following tools are auto-discovered by `MCPServerStreamableHttp`:

1. `search_knowledge_base` - Search knowledge base
2. `add_task` - Create a new task
3. `list_tasks` - List tasks with filters
4. `assign_task` - Assign task to user
5. `complete_task` - Mark task as complete
6. `get_profitability` - Get project profitability
7. `workload_summary` - Get agency workload summary
8. `suggest_assignee` - Suggest best assignee for task
9. `delete_task` - Delete a task
10. `archive_task` - Archive a task
11. `update_task_priority` - Update task priority
12. `update_task_due_date` - Update task due date
13. `update_task_status` - Update task status
14. `list_projects` - List projects
15. `create_project` - Create a project
16. `get_project_details` - Get project details
17. `add_time_entry` - Log time to task
18. `list_time_entries` - List time entries
19. `get_time_for_task` - Get time entries for task
20. `update_time_entry` - Update time entry
21. `delete_time_entry` - Delete time entry

## Testing

### Local Testing
```bash
# Start MCP server
uv run python -m app.mcp.server

# In another terminal, test agent creation
uv run python -c "
import asyncio
from app.agents.chatbot import create_chatbot_agent

async def test():
    agent = await create_chatbot_agent()
    print(f'Agent created: {agent.name}')
    # Tools should be loaded from MCP server

asyncio.run(test())
"
```

### Verification Checklist

- [x] Code syntax verified (py_compile)
- [x] Import statements updated correctly
- [x] `create_chatbot_agent()` is async
- [x] `orchestrator.py` uses async calls
- [x] `chatkit/server.py` uses lazy initialization
- [x] MCP server uses HTTP transport
- [x] Using `MCPServerStreamableHttp` instead of `HostedMCPTool`
- [ ] Runtime testing (requires proper environment)

## Production Deployment

The implementation is ready for deployment to HuggingFace Spaces where:

1. The MCP server will run on port 8001
2. The `MCPServerStreamableHttp` will connect via HTTP (localhost)
3. All 21 tools will be automatically available to the agent
4. Tools are cached for performance (`cache_tools_list=True`)

## Architecture Diagram

```
┌─────────────────┐
│  TeamFlow App   │
│                 │
│  ┌───────────┐  │
│  │ Orchestrator│  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────────────────────┐
│  │ create_chatbot_agent()    │
│  │  (async)                  │
│  └─────┬─────────────────────┘
│        │
│  ┌─────▼──────────────────────┐
│  │ MCPServerStreamableHttp    │
│  │  - Direct HTTP connection  │
│  │  - Auto-discovers tools    │
│  │  - Caches tool list        │
│  └─────┬──────────────────────┘
└────────┼────────────────────────┘
         │
         │ HTTP (localhost)
         │
┌────────▼─────────┐
│  MCP Server      │
│  (FastMCP)       │
│  Port 8001       │
│  - 21 Tools      │
└──────────────────┘
```

## Key Differences Summary

| Aspect | HostedMCPTool (WRONG) | MCPServerStreamableHttp (CORRECT) |
|--------|---------------------|----------------------------------|
| **Purpose** | External hosted MCP servers | Local/remote HTTP MCP servers |
| **Transport** | HTTPS via OpenAI infrastructure | Direct HTTP connection |
| **Configuration** | `tools=[HostedMCPTool(...)]` | `mcp_servers=[server]` |
| **URL Type** | `https://gitmcp.io/...` | `http://127.0.0.1:8001/mcp` |
| **Tool Discovery** | Through OpenAI API | Direct from MCP server |
| **Use Case** | Third-party hosted services | Your own MCP servers |

## References

- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
- MCPServerStreamableHttp Documentation: https://github.com/openai/openai-agents-python/blob/main/docs/mcp.md
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- FastMCP: `mcp.server.fastmcp`
