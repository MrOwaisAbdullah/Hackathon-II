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
import asyncio
import logging
from typing import Any, Optional

from openai import AsyncOpenAI, APIError, APIStatusError
from agents import OpenAIChatCompletionsModel, set_default_openai_api, set_tracing_disabled
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global client and model instances
_openrouter_client: AsyncOpenAI | None = None
_openai_fallback_client: AsyncOpenAI | None = None
_default_model: OpenAIChatCompletionsModel | None = None

# Disable tracing (not using OpenAI's tracing endpoint)
# set_tracing_disabled(True)


class OpenAIModelWithFallback:
    """Model wrapper that automatically falls back from OpenRouter to OpenAI on 429 errors.

    This class wraps the OpenAI Agents SDK's OpenAIChatCompletionsModel to provide
    automatic fallback behavior when OpenRouter returns rate limit errors (429).

    The wrapper intercepts chat completion API calls and:
    1. First tries the primary model (OpenRouter)
    2. If a 429 rate limit error occurs, automatically retries with fallback (OpenAI)
    3. Logs the fallback for monitoring

    Args:
        primary_model: The primary OpenAIChatCompletionsModel (usually OpenRouter)
        fallback_model: The fallback OpenAIChatCompletionsModel (direct OpenAI API)

    Example:
        >>> primary = get_openrouter_model("google/gemini-2.0-flash-exp:free")
        >>> fallback = get_openai_fallback_model("gpt-5-nano-2025-08-07")
        >>> model = OpenAIModelWithFallback(primary, fallback)
        >>> agent = Agent(name="assistant", model=model)
    """

    def __init__(
        self,
        primary_model: OpenAIChatCompletionsModel,
        fallback_model: OpenAIChatCompletionsModel,
    ) -> None:
        """Initialize the fallback wrapper.

        Args:
            primary_model: Primary model (e.g., OpenRouter)
            fallback_model: Fallback model (e.g., direct OpenAI API)
        """
        self._primary = primary_model
        self._fallback = fallback_model
        self._using_fallback = False

    @property
    def name(self) -> str:
        """Return the model name from the primary model."""
        return getattr(self._primary, "model", "unknown")

    async def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit (429) error.

        OpenRouter returns 429 with various formats:
        - APIStatusError with status_code=429
        - APIError with code=429 in the error message
        """
        if isinstance(error, APIStatusError):
            return error.status_code == 429
        if isinstance(error, APIError):
            # Check error message for 429 code
            error_msg = str(error)
            return "429" in error_msg or "rate.limited" in error_msg.lower()
        return False

    async def complete(
        self,
        messages: list[ChatCompletionMessageParam],
        model: str | None = None,
        **kwargs: Any,
    ) -> ChatCompletion:
        """Complete a chat request with automatic fallback on 429 errors.

        Args:
            messages: Chat completion messages
            model: Optional model override (not used, kept for compatibility)
            **kwargs: Additional completion parameters

        Returns:
            ChatCompletion response

        Raises:
            Exception: If both primary and fallback models fail
        """
        # Try primary model first
        try:
            self._using_fallback = False
            return await self._primary.complete(messages=messages, **kwargs)
        except Exception as e:
            # Check if this is a rate limit error
            if await self._is_rate_limit_error(e):
                logger.warning(
                    f"OpenRouter rate limited (429). Falling back to OpenAI API..."
                )
                self._using_fallback = True

                try:
                    return await self._fallback.complete(messages=messages, **kwargs)
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback to OpenAI API also failed: {fallback_error}"
                    )
                    raise fallback_error
            else:
                # Not a rate limit error, re-raise
                logger.error(f"Primary model failed with non-429 error: {e}")
                raise

    async def stream_complete(
        self,
        messages: list[ChatCompletionMessageParam],
        model: str | None = None,
        **kwargs: Any,
    ):
        """Stream complete a chat request with automatic fallback on 429 errors.

        Args:
            messages: Chat completion messages
            model: Optional model override (not used, kept for compatibility)
            **kwargs: Additional completion parameters

        Yields:
            Chat completion chunks

        Raises:
            Exception: If both primary and fallback models fail
        """
        # Try primary model first
        try:
            self._using_fallback = False
            async for chunk in self._primary.stream_complete(
                messages=messages, **kwargs
            ):
                yield chunk
        except Exception as e:
            # Check if this is a rate limit error
            if await self._is_rate_limit_error(e):
                logger.warning(
                    f"OpenRouter rate limited (429) during streaming. Falling back to OpenAI API..."
                )
                self._using_fallback = True

                try:
                    async for chunk in self._fallback.stream_complete(
                        messages=messages, **kwargs
                    ):
                        yield chunk
                except Exception as fallback_error:
                    logger.error(
                        f"Fallback to OpenAI API also failed during streaming: {fallback_error}"
                    )
                    raise fallback_error
            else:
                # Not a rate limit error, re-raise
                logger.error(f"Primary model failed during streaming: {e}")
                raise

    def __getattr__(self, name: str) -> Any:
        """Forward any other attributes to the primary model.

        This allows the wrapper to act as a transparent proxy for any
        attributes or methods not explicitly overridden.
        """
        return getattr(self._primary, name)


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
) -> OpenAIModelWithFallback | OpenAIChatCompletionsModel:
    """Get a model with automatic fallback support for 429 rate limit errors.

    This function returns a model wrapper that automatically falls back from OpenRouter
    to direct OpenAI API when OpenRouter returns rate limit errors (429).

    The fallback happens transparently during agent execution - no code changes needed.

    Args:
        model_name: Model identifier for OpenRouter (e.g., "google/gemini-2.0-flash-exp:free")
            For OpenAI fallback, this will be mapped to the equivalent OpenAI model.

    Returns:
        OpenAIModelWithFallback wrapper if both keys are configured
        OpenAIChatCompletionsModel if only one provider is configured

    Raises:
        ValueError: If neither OPENROUTER_API_KEY nor OPENAI_API_KEY is configured

    Example:
        >>> # Primary: OpenRouter with automatic 429 fallback
        >>> model = get_model_with_fallback()
        >>> agent = Agent(name="assistant", model=model)
        >>>
        >>> # When OpenRouter hits 429, automatically retries with OpenAI
        >>> result = await Runner.run(agent, "Hello!")
    """
    has_openrouter = bool(settings.openrouter_api_key)
    has_openai = bool(settings.openai_api_key)

    # Both providers available - create fallback wrapper
    if has_openrouter and has_openai:
        logger.info(f"Configuring OpenRouter (primary) with OpenAI fallback")

        # Map OpenRouter model names to OpenAI model names
        openai_model_map = {
            "google/gemini-2.0-flash-exp:free": "gpt-5-nano-2025-08-07",
            "google/gemini-2.0-flash-exp": "gpt-5-nano-2025-08-07",
            "google/gemini-flash-1.5": "gpt-5-nano-2025-08-07",
            "google/gemini-2.5-flash": "gpt-5-nano-2025-08-07",
            "google/gemini-2.5-pro": "gpt-5-nano-2025-08-07",
            "openai/gpt-4o-mini": "gpt-5-nano-2025-08-07",
            "openai/gpt-4o": "gpt-5-nano-2025-08-07",
        }

        # Get the equivalent OpenAI model name
        openai_model = openai_model_map.get(model_name, "gpt-5-nano-2025-08-07")

        # Create both models
        primary_model = get_openrouter_model(model_name)
        fallback_model = get_openai_fallback_model(openai_model)

        # Wrap with fallback support
        return OpenAIModelWithFallback(primary_model, fallback_model)

    # Only OpenRouter available
    if has_openrouter:
        logger.info(f"Configuring OpenRouter without fallback (no OPENAI_API_KEY)")
        return get_openrouter_model(model_name)

    # Only OpenAI available
    if has_openai:
        logger.info(f"Configuring OpenAI directly (no OPENROUTER_API_KEY)")
        return get_openai_fallback_model("gpt-5-nano-2025-08-07")

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
        timeout=300.0,  # 5 minutes - increased for HuggingFace Spaces cold starts
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
        timeout=300.0,  # 5 minutes - increased for HuggingFace Spaces cold starts
    )

    return client

