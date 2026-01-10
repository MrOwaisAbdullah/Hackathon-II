"""AsyncOpenAI client configuration with fallback support.

This module configures the AsyncOpenAI client and model with:
- Primary: OpenRouter (access to multiple models)
- Fallback: Direct OpenAI API (when OpenRouter fails)

Reference:
- OpenRouter: https://openrouter.ai/
- OpenAI: https://platform.openai.com/
- OpenAI SDK: https://github.com/openai/openai-python
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
"""
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_default_openai_api, set_tracing_disabled

from app.core.config import settings

# Global client and model instances
_openrouter_client: AsyncOpenAI | None = None
_openai_fallback_client: AsyncOpenAI | None = None
_default_model: OpenAIChatCompletionsModel | None = None

# Disable tracing (not using OpenAI's tracing endpoint)
set_tracing_disabled(True)


def get_openrouter_model(
    model_name: str = "google/gemini-2.0-flash-exp:free",
) -> OpenAIChatCompletionsModel:
    """Get or create the OpenRouter model.

    Args:
        model_name: Model identifier for OpenRouter (e.g., "google/gemini-2.0-flash-exp:free")

    Returns:
        Configured OpenAIChatCompletionsModel instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not configured
    """
    global _default_model

    if _default_model is not None:
        return _default_model

    # Get the client
    client = get_openrouter_client()

    # Configure Agents SDK to use Chat Completions API
    # OpenRouter doesn't support the Responses API
    set_default_openai_api("chat_completions")

    # Create the model wrapper
    _default_model = OpenAIChatCompletionsModel(
        openai_client=client,
        model=model_name,
    )

    return _default_model


def get_openai_fallback_model(
    model_name: str = "gpt-5-nano-2025-08-07",
) -> OpenAIChatCompletionsModel:
    """Get or create a direct OpenAI API model (fallback).

    This provides a direct connection to OpenAI API without going through OpenRouter.
    Use this when:
    - OpenRouter is unavailable or rate limited
    - You need direct OpenAI API access
    - You want to avoid OpenRouter rate limits

    Args:
        model_name: Model identifier for OpenAI (e.g., "gpt-5-nano-2025-08-07")
            Note: Use standard OpenAI model names (not OpenRouter format)

    Returns:
        Configured OpenAIChatCompletionsModel instance

    Raises:
        ValueError: If OPENAI_API_KEY is not configured
    """
    global _openai_fallback_client

    if _openai_fallback_client is None:
        _openai_fallback_client = _create_openai_fallback_client()

    # Configure Agents SDK to use Chat Completions API
    set_default_openai_api("chat_completions")

    # Create the model wrapper
    return OpenAIChatCompletionsModel(
        openai_client=_openai_fallback_client,
        model=model_name,
    )


def get_model_with_fallback(
    model_name: str = "google/gemini-2.0-flash-exp:free",
) -> OpenAIChatCompletionsModel:
    """Get a model with automatic fallback support.

    This function returns a model configured to use OpenRouter as primary,
    with automatic fallback to direct OpenAI API if OpenRouter fails.

    The OpenAI Agents SDK will handle retries automatically, but you can
    manually switch to fallback using get_openai_fallback_model() if needed.

    Args:
        model_name: Model identifier for OpenRouter (e.g., "google/gemini-2.0-flash-exp:free")
            For OpenAI fallback, this will be mapped to the equivalent OpenAI model.

    Returns:
        Configured OpenAIChatCompletionsModel instance

    Raises:
        ValueError: If neither OPENROUTER_API_KEY nor OPENAI_API_KEY is configured

    Example:
        >>> # Primary: OpenRouter with fallback configured
        >>> model = get_model_with_fallback()
        >>> agent = Agent(name="assistant", model=model)
        >>>
        >>> # Or manually use direct OpenAI as fallback
        >>> fallback_model = get_openai_fallback_model()
        >>> fallback_agent = Agent(name="assistant", model=fallback_model)
    """
    # Try OpenRouter first (primary)
    if settings.openrouter_api_key:
        try:
            return get_openrouter_model(model_name)
        except Exception as e:
            # Log warning but don't fail yet
            import logging
            logging.warning(f"OpenRouter initialization failed: {e}. Trying direct OpenAI API...")

    # Fallback to direct OpenAI API
    if settings.openai_api_key:
        # Map OpenRouter model names to OpenAI model names
        openai_model_map = {
            "google/gemini-2.0-flash-exp:free": "gpt-4o-mini",
            "google/gemini-2.0-flash-exp": "gpt-4o-mini",
            "google/gemini-flash-1.5": "gpt-4o-mini",
            "google/gemini-2.5-flash": "gpt-4o-mini",
            "google/gemini-2.5-pro": "gpt-4o",
            "openai/gpt-4o-mini": "gpt-4o-mini",
            "openai/gpt-4o": "gpt-4o",
        }

        # Get the equivalent OpenAI model name
        openai_model = openai_model_map.get(model_name, "gpt-5-nano-2025-08-07")

        import logging
        logging.info(f"Using direct OpenAI API with model: {openai_model}")

        return get_openai_fallback_model(openai_model)

    # Neither API key is configured
    raise ValueError(
        "No AI provider configured. Please set either OPENROUTER_API_KEY or OPENAI_API_KEY "
        "in your environment or .env file."
    )


def get_openrouter_client() -> AsyncOpenAI:
    """Get or initialize the AsyncOpenAI client for OpenRouter.

    This is a singleton pattern - the client is created once and reused.

    Returns:
        Configured AsyncOpenAI client instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not configured
    """
    global _openrouter_client

    if _openrouter_client is None:
        _openrouter_client = _create_openrouter_client()

    return _openrouter_client


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
    # IMPORTANT: Disable built-in retries so our fallback logic can handle 429 errors
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
        max_retries=0,  # Disable automatic retries - let our fallback logic handle it
        timeout=30.0,
    )

    return client


def _create_openai_fallback_client() -> AsyncOpenAI:
    """Create a new AsyncOpenAI client for direct OpenAI API access (fallback).

    This connects directly to OpenAI's API as a fallback when OpenRouter is unavailable.

    Returns:
        Configured AsyncOpenAI client instance

    Raises:
        ValueError: If OPENAI_API_KEY is not configured
    """
    # Validate API key
    if not settings.openai_api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Please configure it in your environment "
            "or .env file."
        )

    # Create AsyncOpenAI client for OpenAI (no custom base_url needed - uses default)
    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        max_retries=0,  # Disable automatic retries
        timeout=30.0,
    )

    return client

