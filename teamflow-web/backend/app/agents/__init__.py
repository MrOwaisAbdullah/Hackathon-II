"""TeamFlow AI Agents package.

This package provides OpenAI Agents SDK integration with OpenRouter
and OpenAI fallback for the TeamFlow AI Chatbot.
"""

from app.agents.client import (
    get_openrouter_client,
    get_openai_fallback_model,
    get_model_with_fallback,
    OpenAIModelWithFallback,  # Runtime fallback wrapper for 429 errors
)
from app.agents.chatbot import (
    create_chatbot_agent_context,  # NEW: Use this for proper MCP server lifecycle
    create_chatbot_agent,  # LEGACY: Deprecated - does NOT connect MCP server
    run_chatbot_stream,
)

__all__ = [
    "get_openrouter_client",
    "get_openai_fallback_model",
    "get_model_with_fallback",
    "OpenAIModelWithFallback",  # Runtime fallback wrapper
    "create_chatbot_agent_context",  # NEW: Preferred function
    "create_chatbot_agent",  # LEGACY: Deprecated
    "run_chatbot_stream",
]
