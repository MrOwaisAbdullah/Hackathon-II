"""MCP server for TeamFlow using FastMCP (T017).

This server exposes TeamFlow service layer methods as tools to AI agents.
Uses FastMCP from the official MCP Python SDK (mcp.server.fastmcp).
"""
from mcp.server.fastmcp import FastMCP
from app.mcp.tools import (
    register_knowledge_base_tools,
    register_task_tools,
    register_analytics_tools,
    register_recommendation_tools,
)

# Create FastMCP server instance
mcp = FastMCP("TeamFlow")

# Register all tool categories
register_knowledge_base_tools(mcp)
register_task_tools(mcp)
register_analytics_tools(mcp)
register_recommendation_tools(mcp)


def main():
    """Entry point for running the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
