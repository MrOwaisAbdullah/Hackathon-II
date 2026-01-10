"""TeamFlow AI Agents package.

This package provides OpenAI Agents SDK integration with OpenRouter
and OpenAI fallback for the TeamFlow AI Chatbot.
"""

from app.agents.client import get_openrouter_client, get_openai_fallback_model, get_model_with_fallback
from app.agents.chatbot import create_chatbot_agent, run_chatbot_stream

__all__ = [
    "get_openrouter_client",
    "get_openai_fallback_model",
    "get_model_with_fallback",
    "create_chatbot_agent",
    "run_chatbot_stream",
]
