"""Gemini AsyncOpenAI client configuration.

This module configures the AsyncOpenAI client to use Gemini 2.0 Flash model
via OpenAI-compatible endpoint.

Reference:
- Gemini API: https://generativelanguage.googleapis.com/v1beta/
- OpenAI SDK: https://github.com/openai/openai-python
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
"""
from openai import AsyncOpenAI
from agents import set_default_openai_client

from app.core.config import settings

# Global client instance
_gemini_client: AsyncOpenAI | None = None


def initialize_gemini_client() -> AsyncOpenAI:
    """Initialize and configure AsyncOpenAI client for Gemini.

    The Gemini API provides an OpenAI-compatible endpoint at:
    https://generativelanguage.googleapis.com/v1beta/

    This configuration allows us to use the OpenAI Agents SDK with Gemini
    models by setting a custom base_url and using the Gemini API key.

    The client is configured with:
    - Base URL: Gemini's OpenAI-compatible endpoint
    - API Key: Retrieved from GEMINI_API_KEY environment variable
    - Model: gemini-2.0-flash-exp (default, can be overridden)

    Returns:
        Configured AsyncOpenAI client instance

    Example:
        >>> client = initialize_gemini_client()
        >>> response = await client.chat.completions.create(
        ...     model="gemini-2.0-flash-exp",
        ...     messages=[{"role": "user", "content": "Hello!"}]
        ... )
    """
    global _gemini_client

    if _gemini_client is not None:
        return _gemini_client

    # Validate API key
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please configure it in your environment "
            "or .env file."
        )

    # Create AsyncOpenAI client configured for Gemini
    _gemini_client = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/",
        api_key=settings.gemini_api_key,
    )

    # Set as default client for OpenAI Agents SDK
    set_default_openai_client(_gemini_client, use_for_tracing=True)

    return _gemini_client


def get_gemini_client() -> AsyncOpenAI:
    """Get or initialize the Gemini AsyncOpenAI client.

    This is a singleton pattern - the client is created once and reused.

    Returns:
        Configured AsyncOpenAI client instance

    Raises:
        ValueError: If GEMINI_API_KEY is not configured
    """
    if _gemini_client is None:
        return initialize_gemini_client()
    return _gemini_client
