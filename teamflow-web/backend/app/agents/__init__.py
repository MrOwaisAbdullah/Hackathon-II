"""TeamFlow AI Agents package.

This package provides OpenAI Agents SDK integration with Gemini 2.0 Flash
model for the TeamFlow AI Chatbot.
"""

from app.agents.client import get_gemini_client, initialize_gemini_client
from app.agents.chatbot import create_chatbot_agent, run_chatbot_stream

__all__ = [
    "get_gemini_client",
    "initialize_gemini_client",
    "create_chatbot_agent",
    "run_chatbot_stream",
]
