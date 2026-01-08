"""AsyncOpenAI client configuration for OpenRouter.

This module configures the AsyncOpenAI client and model for use with
various LLM models via OpenRouter's OpenAI-compatible endpoint.

Reference:
- OpenRouter: https://openrouter.ai/
- OpenAI SDK: https://github.com/openai/openai-python
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
"""
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_default_openai_api

from app.core.config import settings

# Global client and model instances
_gemini_client: AsyncOpenAI | None = None
_default_model: OpenAIChatCompletionsModel | None = None


def get_openrouter_model(
    model_name: str = "mistralai/devstral-2512:free",
) -> OpenAIChatCompletionsModel:
    """Get or create the OpenRouter model.

    Args:
        model_name: Model identifier for OpenRouter (e.g., "mistralai/devstral-2512:free")

    Returns:
        Configured OpenAIChatCompletionsModel instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not configured
    """
    global _default_model

    if _default_model is not None:
        return _default_model

    # Get the client
    client = get_gemini_client()

    # Configure Agents SDK to use Chat Completions API
    # OpenRouter doesn't support the Responses API
    set_default_openai_api("chat_completions")

    # Create the model wrapper
    _default_model = OpenAIChatCompletionsModel(
        openai_client=client,
        model=model_name,
    )

    return _default_model


def get_gemini_client() -> AsyncOpenAI:
    """Get or initialize the AsyncOpenAI client for OpenRouter.

    This is a singleton pattern - the client is created once and reused.

    Returns:
        Configured AsyncOpenAI client instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not configured
    """
    global _gemini_client

    if _gemini_client is None:
        _gemini_client = _create_openrouter_client()

    return _gemini_client


def _create_openrouter_client() -> AsyncOpenAI:
    """Create a new AsyncOpenAI client for OpenRouter.

    Returns:
        Configured AsyncOpenAI client instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not configured
    """
    # Validate API key
    if not settings.openrouter_api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set. Please configure it in your environment "
            "or .env file."
        )

    # Create AsyncOpenAI client configured for OpenRouter
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

    return client


def initialize_gemini_client() -> AsyncOpenAI:
    """Initialize and configure AsyncOpenAI client for OpenRouter.

    Uses OpenRouter as an OpenAI-compatible endpoint for LLM models.
    This provides:
    - Access to various models via OpenRouter
    - OpenAI-compatible Chat Completions API
    - Unified billing through OpenRouter
    - Support for models like Mistral, Gemini, etc.

    The client is configured with:
    - Base URL: https://openrouter.ai/api/v1 (OpenRouter)
    - API Key: OPENROUTER_API_KEY from environment
    - API Type: chat_completions (for OpenRouter compatibility)

    Returns:
        Configured AsyncOpenAI client instance

    Example:
        >>> client = initialize_gemini_client()
        >>> response = await client.chat.completions.create(
        ...     model="mistralai/devstral-2512:free",
        ...     messages=[{"role": "user", "content": "Hello!"}]
        ... )
    """
    return get_gemini_client()

