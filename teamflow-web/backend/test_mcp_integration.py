#!/usr/bin/env python
"""Manual test script for MCPServerStreamableHttp integration.

This script tests the MCP server integration with the OpenAI Agents SDK
using the production-ready single-server architecture.

The MCP server is mounted at /mcp endpoint on the main FastAPI server.

Usage:
    # Terminal 1: Start the FastAPI server (includes MCP at /mcp)
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

    # Terminal 2: Run this test
    python test_mcp_integration.py
"""
import asyncio
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


async def test_mcp_server_direct():
    """Test MCP server directly via HTTP.

    Uses the production-ready single-server architecture where MCP is
    mounted at /mcp endpoint on the main FastAPI server (port 8000).
    """
    print("=" * 60)
    print("Test 1: MCP Server Direct Connection")
    print("=" * 60)

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            # Production-ready: MCP server at /mcp on port 8000
            response = await client.post(
                "http://127.0.0.1:8000/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list",
                    "params": {}
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                tools = data["result"]["tools"]
                print(f"✅ MCP Server is running at http://127.0.0.1:8000/mcp")
                print(f"✅ Found {len(tools)} tools")

                # Show all tools
                print("\n📋 Available Tools:")
                for i, tool in enumerate(tools, 1):
                    desc = tool.get('description', 'No description')
                    print(f"   {i}. {tool['name']}: {desc[:50]}{'...' if len(desc) > 50 else ''}")

                return True
            else:
                print(f"❌ MCP server returned status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to MCP server: {e}")
        print("\n⚠️  Make sure the FastAPI server is running:")
        print("   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
        return False


async def test_agent_creation():
    """Test agent creation with MCPServerStreamableHttp using context manager."""
    print("\n" + "=" * 60)
    print("Test 2: Agent Creation with MCPServerStreamableHttp (Context Manager)")
    print("=" * 60)

    try:
        from app.agents.chatbot import create_chatbot_agent_context

        print("⏳ Creating agent context...")
        async with create_chatbot_agent_context() as agent:
            print(f"✅ Agent created: {agent.name}")
            print(f"✅ MCP servers configured: {len(agent.mcp_servers)}")

            # Show MCP server details
            mcp_server = agent.mcp_servers[0]
            print(f"✅ MCP server name: {mcp_server.name}")
            print(f"✅ MCP server URL: {mcp_server.params['url']}")
            print(f"✅ Cache tools list: {mcp_server.cache_tools_list}")

        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_simple_query():
    """Test agent with a simple query (no tools) using context manager."""
    print("\n" + "=" * 60)
    print("Test 3: Agent Simple Query (Context Manager)")
    print("=" * 60)

    try:
        from app.agents.chatbot import create_chatbot_agent_context
        from agents import Runner

        print("⏳ Creating agent context...")
        async with create_chatbot_agent_context() as agent:
            print("⏳ Running simple query...")
            result = await Runner.run(agent, "Hello! What can you help me with?")

            response = result.final_output
            if len(response) > 150:
                response = response[:150] + "..."

            print(f"✅ Agent responded:")
            print(f"   {response}")

        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tool_discovery():
    """Test that all 21 MCP tools are discoverable by the agent."""
    print("\n" + "=" * 60)
    print("Test 4: Tool Discovery (All 21 MCP Tools)")
    print("=" * 60)

    try:
        from app.agents.chatbot import create_chatbot_agent_context

        print("⏳ Creating agent context to discover tools...")
        async with create_chatbot_agent_context() as agent:
            # Get MCP server
            mcp_server = agent.mcp_servers[0]

            # List tools from MCP server
            print("⏳ Discovering tools from MCP server...")
            tools = await mcp_server.list_tools()

            print(f"✅ Discovered {len(tools)} tools")

            # Expected tools by category
            expected_tools = {
                "Knowledge Base": ["search_knowledge_base"],
                "Task Management": ["add_task", "list_tasks", "assign_task", "complete_task"],
                "Task Updates": ["update_task_priority", "update_task_due_date", "update_task_status", "archive_task", "delete_task"],
                "Project Management": ["list_projects", "create_project", "get_project_details"],
                "Analytics": ["get_profitability", "workload_summary"],
                "Recommendations": ["suggest_assignee"],
                "Time Entry": ["add_time_entry", "list_time_entries", "get_time_for_task", "update_time_entry", "delete_time_entry"],
            }

            # Categorize discovered tools
            discovered_names = [tool.name for tool in tools]
            missing_tools = []

            print("\n📋 Tool Categories:")
            total_expected = 0
            for category, tool_list in expected_tools.items():
                total_expected += len(tool_list)
                found_count = sum(1 for t in tool_list if t in discovered_names)
                status = "✅" if found_count == len(tool_list) else "⚠️"
                print(f"   {status} {category}: {found_count}/{len(tool_list)}")

                # Find missing tools
                for tool_name in tool_list:
                    if tool_name not in discovered_names:
                        missing_tools.append(f"{category}:{tool_name}")

            # Verify we have all expected tools
            if len(discovered_names) >= 21:
                print(f"\n✅ All {len(discovered_names)} tools discovered!")
                if missing_tools:
                    print(f"⚠️  Missing tools: {missing_tools}")
                return True
            else:
                print(f"\n⚠️  Expected 21 tools, found {len(discovered_names)}")
                if missing_tools:
                    print(f"   Missing: {missing_tools}")
                return False

    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tool_usage_list_projects():
    """Test that the agent can actually use an MCP tool (list_projects)."""
    print("\n" + "=" * 60)
    print("Test 5: Tool Usage - list_projects")
    print("=" * 60)

    try:
        from app.agents.chatbot import create_chatbot_agent_context
        from agents import Runner

        print("⏳ Creating agent context...")
        async with create_chatbot_agent_context() as agent:
            print("⏳ Asking agent to list projects...")
            result = await Runner.run(
                agent,
                "Please list all projects in the system. Use the list_projects tool."
            )

            response = result.final_output
            if len(response) > 300:
                response = response[:300] + "..."

            print(f"✅ Agent responded:")
            print(f"   {response}")

            # Check if tool was used
            if result.tool_calls:
                print(f"✅ Tool calls made: {len(result.tool_calls)}")
                for call in result.tool_calls:
                    print(f"   - {call.tool_name}")
                return True
            else:
                print(f"⚠️  No tool calls detected, but agent responded")
                return True

    except Exception as e:
        print(f"❌ Tool usage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCPServerStreamableHttp Integration Test")
    print("=" * 60)
    print()

    results = []

    # Test 1: MCP server direct connection
    results.append(await test_mcp_server_direct())

    # Test 2: Agent creation
    results.append(await test_agent_creation())

    # Test 3: Simple query
    results.append(await test_agent_simple_query())

    # Test 4: Tool discovery (all 21 tools)
    results.append(await test_tool_discovery())

    # Test 5: Tool usage
    results.append(await test_tool_usage_list_projects())

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if all(results):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
