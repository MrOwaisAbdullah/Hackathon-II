# MCP Server 404 Fix - FastAPI Architecture

## Problem

The ChatKit widget was failing with `Session terminated` error when trying to connect to the MCP server. The backend logs showed:

```
INFO: 127.0.0.1:59356 - "POST /mcp HTTP/1.1" 404 Not Found
[not_found_exception_handler] Resource not found
```

## Root Cause

**Incorrect MCP Server Configuration**: The `streamable_http_path` and `json_response` parameters were not being set during `FastMCP()` initialization.

**CRITICAL**: These parameters MUST be passed to the `FastMCP()` constructor - they cannot be set via `mcp.settings` afterwards.

## Solution - Correct FastMCP Initialization

### 1. Configure MCP server during FastMCP initialization

```python
# app/mcp/server.py - Set during FastMCP initialization
from mcp.server.fastmcp import FastMCP

# CRITICAL: streamable_http_path MUST be set during initialization
# json_response=True enables proper JSON-RPC over HTTP
mcp = FastMCP(
    "TeamFlow",
    streamable_http_path="/",  # Serve at root of mount point
    json_response=True,  # Enable JSON-RPC responses
)
```

### 2. Use FastAPI with app.mount()

```python
# app/main.py - FastAPI application
from fastapi import FastAPI
from starlette.routing import Mount
from app.mcp.server import mcp

# Lifespan with session manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(
    lifespan=lifespan,
)

# Mount MCP server directly using FastAPI's mount() method
app.mount("/mcp", mcp.streamable_http_app(), name="mcp")
```

### 3. Run session manager in lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start MCP session manager (required for streamable HTTP)
    async with mcp.session_manager.run():
        yield
```

### Complete Implementation

**app/mcp/server.py:**
```python
from mcp.server.fastmcp import FastMCP

# CRITICAL: streamable_http_path MUST be set during initialization
# json_response=True enables proper JSON-RPC over HTTP
mcp = FastMCP(
    "TeamFlow",
    streamable_http_path="/",  # Serve at root of mount point
    json_response=True,  # Enable JSON-RPC responses
)

# Register tools...
```

**app/main.py:**
```python
"""FastAPI application for TeamFlow backend.

MCP server is mounted at /mcp using FastAPI's mount() method.
Key configuration: streamable_http_path="/" and json_response=True
must be set during FastMCP() initialization (see app/mcp/server.py).
"""
from fastapi import FastAPI
from app.mcp.server import mcp

# Lifespan with session manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(
    lifespan=lifespan,
)

# Include all API routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
# ... other routers ...

# Add health and metrics endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "teamflow-backend"}

# Mount MCP server at /mcp endpoint
app.mount("/mcp", mcp.streamable_http_app(), name="mcp")

# Add middleware
app.add_middleware(...)
```

## Why This Works

1. **`streamable_http_path="/"` during initialization**: This is the CRITICAL setting that must be passed to the `FastMCP()` constructor
2. **`json_response=True`**: Enables proper JSON-RPC over HTTP (from official examples)
3. **FastAPI with `app.mount()`**: FastAPI's mount() method works correctly for MCP servers when the above configuration is set properly
4. **Session manager in lifespan**: The `mcp.session_manager.run()` context manager is required for streamable HTTP transport to work

### Key Insight

The MCP server configuration must be set during `FastMCP()` initialization:

```python
# CORRECT
mcp = FastMCP(
    "TeamFlow",
    streamable_http_path="/",
    json_response=True,
)

# WRONG - setting via settings doesn't work
mcp = FastMCP("TeamFlow")
mcp.settings.streamable_http_path = "/"  # Too late!
```

## Production-Ready Architecture

This fix implements the production-ready single-server architecture:

```
FastAPI on port 8000
  ├─ /api/*          → FastAPI routers
  ├─ /health         → Health check
  ├─ /metrics        → Prometheus metrics
  └─ /mcp            → MCP server (via app.mount)
```

**Benefits:**
- Single container/VM deployment
- Single port exposure (no internal networking)
- Shared lifecycle management
- Simplified monitoring and logging
- Easier horizontal scaling

## What Was Wrong (Previous Attempts)

| Attempt | Method | Problem |
|---------|--------|---------|
| 1 | `app.mount("/mcp", mcp.streamable_http_app())` | 404 - `streamable_http_path` not set during init |
| 2 | Setting `mcp.settings.streamable_http_path = "/"` | Still 404 - must be in constructor |
| 3 | Adding `json_response=True` via settings | Still 404 - must be in constructor |
| 4 | Using Starlette instead of FastAPI | AssertionError - FastAPI routers don't work in Starlette |

## Solution - Correct FastMCP Initialization

**CORRECT:**
```python
# app/mcp/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "TeamFlow",
    streamable_http_path="/",  # In constructor
    json_response=True,        # In constructor
)

# app/main.py
from fastapi import FastAPI
from app.mcp.server import mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(lifespan=lifespan)
app.mount("/mcp", mcp.streamable_http_app())
```

## Verification

### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```

Should return:
```json
{"status": "healthy", "service": "teamflow-backend"}
```

### 2. MCP Server Test
```bash
python test_mcp_integration.py
```

Should show:
```
✅ MCP Server is running at http://127.0.0.1:8000/mcp
✅ Found 21 tools
```

### 3. ChatKit Widget
1. Open the ChatKit widget in the frontend
2. Send a message
3. Should NOT see `Session terminated` error
4. Agent should be able to use MCP tools

## Related Files

- `app/main.py` - FastAPI application with MCP mounted via `app.mount()`
- `app/mcp/server.py` - MCP server with `streamable_http_path="/"` and `json_response=True`
- `app/mcp/tools.py` - 21 MCP tools implementation
- `test_mcp_integration.py` - Integration tests

## Timeline

- **2025-01-12**: Initial implementation with `app.mount()` - 404 errors occurred
- **2025-01-12**: Attempted to set `streamable_http_path` via `mcp.settings` - Still 404
- **2025-01-12**: Switched to Starlette-based architecture - Broke FastAPI routers with AssertionError
- **2025-01-12**: **RESOLVED** - Set `streamable_http_path="/"` and `json_response=True` during `FastMCP()` initialization, reverted to FastAPI with `app.mount()`

## Status: ✅ RESOLVED

The MCP server is now correctly mounted and accessible at `/mcp`. All 21 MCP tools are accessible to the OpenAI Agents SDK via `MCPServerStreamableHttp`.

**Key Takeaways:**
1. `streamable_http_path` MUST be set during `FastMCP()` initialization, not via `mcp.settings`
2. `json_response=True` MUST be set during `FastMCP()` initialization
3. Use FastAPI with `app.mount()` for production deployment
4. Run `mcp.session_manager.run()` in the lifespan context manager
5. FastAPI routers don't work when mounted in a plain Starlette app (they require FastAPI's middleware context)
