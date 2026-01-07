"""Example usage of TeamFlow AI Chatbot agent.

This script demonstrates how to use the OpenAI Agents SDK with Gemini 2.0 Flash
model for the TeamFlow AI Chatbot.

Prerequisites:
1. Set GEMINI_API_KEY in your environment or .env file
2. Ensure MCP server is running (or tools are available)
3. Install dependencies: uv sync

Usage:
    python -m app.agents.example
"""
import asyncio
import os

from app.agents import create_chatbot_agent, run_chatbot_stream


async def main():
    """Run example chatbot interactions."""

    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        return

    print("=" * 60)
    print("TeamFlow AI Chatbot - Example Usage")
    print("=" * 60)
    print()

    # Create agent
    print("Initializing TeamFlow AI agent...")
    agent = create_chatbot_agent()
    print("Agent ready!")
    print()

    # Example 1: Simple greeting
    print("-" * 60)
    print("Example 1: Simple greeting")
    print("-" * 60)
    print("User: Hello!")
    print("Agent: ", end="")

    async for chunk in run_chatbot_stream(agent, "Hello!"):
        print(chunk, end="")

    print("\n")

    # Example 2: Task management
    print("-" * 60)
    print("Example 2: Create a task")
    print("-" * 60)
    print("User: Create a task to fix the navbar responsive bug")
    print("Agent: ", end="")

    async for chunk in run_chatbot_stream(
        agent,
        "Create a task to fix the navbar responsive bug. "
        "Set priority to HIGH and assign it to the frontend team."
    ):
        print(chunk, end="")

    print("\n")

    # Example 3: Analytics
    print("-" * 60)
    print("Example 3: Get profitability analysis")
    print("-" * 60)
    print("User: What's the profitability for project XYZ?")
    print("Agent: ", end="")

    async for chunk in run_chatbot_stream(
        agent,
        "Can you get the profitability analysis for project XYZ? "
        "I need to see revenue, costs, and profit margins."
    ):
        print(chunk, end="")

    print("\n")

    # Example 4: AI Recommendations
    print("-" * 60)
    print("Example 4: Suggest task assignee")
    print("-" * 60)
    print("User: Suggest the best person for the new API integration task")
    print("Agent: ", end="")

    async for chunk in run_chatbot_stream(
        agent,
        "I need to assign the new API integration task. "
        "Who would be the best fit based on skills and current workload?"
    ):
        print(chunk, end="")

    print("\n")

    # Example 5: Interactive chat
    print("-" * 60)
    print("Example 5: Interactive mode")
    print("-" * 60)
    print("Type 'quit' to exit\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("Agent: ", end="", flush=True)

            async for chunk in run_chatbot_stream(agent, user_input):
                print(chunk, end="", flush=True)

            print()  # New line after response

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
