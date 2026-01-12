"""MCP server for TeamFlow using FastMCP (T017).

This server exposes TeamFlow service layer methods as tools to AI agents.
Uses FastMCP from the official MCP Python SDK (mcp.server.fastmcp).

Transport: Streamable HTTP (recommended for production)
- Server runs mounted at /mcp in FastAPI
- Supports stateful sessions with proper HTTP transport
- Better for production than stdio transport
"""
from mcp.server.fastmcp import FastMCP
from app.mcp.tools import (
    register_knowledge_base_tools,
    register_task_tools,
    register_analytics_tools,
    register_recommendation_tools,
    register_project_tools,
    register_task_update_tools,
    register_time_entry_tools,
)

# Create FastMCP server instance with stateful HTTP support
# CRITICAL: streamable_http_path="/" must be set at initialization
# This ensures the MCP endpoint is at /mcp (not /mcp/mcp) when mounted
# json_response=True enables proper JSON-RPC over HTTP (from official examples)
mcp = FastMCP(
    "TeamFlow",
    streamable_http_path="/",  # Critical: serve at root of mount point
    json_response=True,  # Enable JSON-RPC responses (required for streamable HTTP)
)

# Register all tool categories
register_knowledge_base_tools(mcp)
register_task_tools(mcp)
register_analytics_tools(mcp)
register_recommendation_tools(mcp)
register_project_tools(mcp)
register_task_update_tools(mcp)
register_time_entry_tools(mcp)


def main():
    """Entry point for running the MCP server with HTTP transport."""
    import uvicorn

    # Run with streamable HTTP transport on port 8001
    uvicorn.run(
        mcp.streamable_http_app(),
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )


if __name__ == "__main__":
    main()
