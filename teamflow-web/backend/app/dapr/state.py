"""
Dapr State Store Client

This module provides state management capabilities using Dapr's HTTP API.
State is stored in PostgreSQL via the Dapr state store component.
"""

import httpx
import structlog
from typing import Any, Optional
from pydantic import BaseModel

# Configure structured logging
logger = structlog.get_logger(__name__)

# Dapr HTTP endpoint defaults
DAPR_HTTP_HOST = "localhost"
DAPR_HTTP_PORT = 3500
DAPR_STATE_NAME = "postgres-state"


class StateItem(BaseModel):
    """
    Dapr state item for bulk operations.

    Attributes:
        key: State key
        value: State value (will be JSON serialized)
        etag: Optional entity tag for concurrency control
        metadata: Optional metadata dictionary
        options: Optional state operation options
    """

    key: str
    value: Any
    etag: Optional[str] = None
    metadata: Optional[dict[str, str]] = None
    options: Optional[dict[str, Any]] = None


class DaprStateClient:
    """
    Async Dapr State Store client for caching and state management.

    This client wraps Dapr's HTTP API for state operations with:
    - Async/await support
    - JSON serialization
    - Structured logging
    - Error handling
    """

    def __init__(
        self,
        dapr_host: str = DAPR_HTTP_HOST,
        dapr_port: int = DAPR_HTTP_PORT,
        state_name: str = DAPR_STATE_NAME,
    ):
        """
        Initialize the Dapr State client.

        Args:
            dapr_host: Dapr sidecar HTTP host
            dapr_port: Dapr sidecar HTTP port
            state_name: Name of the Dapr state store component
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port
        self.state_name = state_name
        self.base_url = f"http://{dapr_host}:{dapr_port}/v1.0"
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a state value by key.

        Args:
            key: State key

        Returns:
            State value or None if not found
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)

        url = f"{self.base_url}/state/{self.state_name}/{key}"

        try:
            response = await self._client.get(url)

            if response.status_code == 200:
                # Dapr returns JSON with "data" field containing the actual value
                result = response.json()
                return result.get("data")
            elif response.status_code == 204:
                # No content = key not found
                logger.debug("state_not_found", key=key)
                return None
            else:
                logger.error(
                    "state_get_failed",
                    key=key,
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return None

        except httpx.HTTPError as e:
            logger.error("state_get_error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        etag: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Set a state value by key.

        Args:
            key: State key
            value: State value (will be JSON serialized)
            etag: Optional entity tag for concurrency control
            ttl_seconds: Optional time-to-live in seconds

        Returns:
            True if set successfully, False otherwise
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)

        url = f"{self.base_url}/state/{self.state_name}"

        # Build state item
        state_item = [{"key": key, "value": value}]

        # Add optional parameters
        if etag:
            state_item[0]["etag"] = etag
        if ttl_seconds:
            state_item[0]["options"] = {"ttlInSeconds": ttl_seconds}

        try:
            response = await self._client.post(url, json=state_item)

            if response.is_success:
                logger.debug("state_set", key=key)
                return True
            else:
                logger.error(
                    "state_set_failed",
                    key=key,
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return False

        except httpx.HTTPError as e:
            logger.error("state_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str, etag: Optional[str] = None) -> bool:
        """
        Delete a state value by key.

        Args:
            key: State key
            etag: Optional entity tag for concurrency control

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)

        url = f"{self.base_url}/state/{self.state_name}/{key}"

        headers = {}
        if etag:
            headers["If-Match"] = etag

        try:
            response = await self._client.delete(url, headers=headers)

            if response.is_success or response.status_code == 204:
                logger.debug("state_deleted", key=key)
                return True
            else:
                logger.error(
                    "state_delete_failed",
                    key=key,
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return False

        except httpx.HTTPError as e:
            logger.error("state_delete_error", key=key, error=str(e))
            return False

    async def set_bulk(self, items: list[StateItem]) -> bool:
        """
        Set multiple state values in a single request.

        Args:
            items: List of StateItem objects

        Returns:
            True if all set successfully, False otherwise
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)

        url = f"{self.base_url}/state/{self.state_name}"

        # Convert StateItem models to dicts
        state_items = [item.model_dump(mode="json", exclude_none=True) for item in items]

        try:
            response = await self._client.post(url, json=state_items)

            if response.is_success:
                logger.debug("state_set_bulk", count=len(items))
                return True
            else:
                logger.error(
                    "state_set_bulk_failed",
                    count=len(items),
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return False

        except httpx.HTTPError as e:
            logger.error("state_set_bulk_error", count=len(items), error=str(e))
            return False


# Singleton instance for dependency injection
_state_client: Optional[DaprStateClient] = None


async def get_state_client() -> DaprStateClient:
    """Get or create the singleton Dapr State client."""
    global _state_client
    if _state_client is None:
        _state_client = DaprStateClient()
        await _state_client.__aenter__()
    return _state_client
