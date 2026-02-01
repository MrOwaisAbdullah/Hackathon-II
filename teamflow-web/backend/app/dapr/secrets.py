"""
Dapr Secret Store Client

This module provides secret retrieval capabilities using Dapr's HTTP API.
Secrets are fetched from Kubernetes secrets via the Dapr secret store component.
"""

import httpx
import structlog
from typing import Any, Optional

# Configure structured logging
logger = structlog.get_logger(__name__)

# Dapr HTTP endpoint defaults
DAPR_HTTP_HOST = "localhost"
DAPR_HTTP_PORT = 3500
DAPR_SECRET_STORE = "kubernetes-secret-store"


class DaprSecretClient:
    """
    Async Dapr Secret Store client for retrieving secrets from Kubernetes.

    This client wraps Dapr's HTTP API for secret retrieval with:
    - Async/await support
    - Structured logging
    - Error handling
    """

    def __init__(
        self,
        dapr_host: str = DAPR_HTTP_HOST,
        dapr_port: int = DAPR_HTTP_PORT,
        secret_store: str = DAPR_SECRET_STORE,
    ):
        """
        Initialize the Dapr Secret Store client.

        Args:
            dapr_host: Dapr sidecar HTTP host
            dapr_port: Dapr sidecar HTTP port
            secret_store: Name of the Dapr secret store component
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port
        self.secret_store = secret_store
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

    async def get_secret(self, secret_name: str, secret_key: str) -> Optional[str]:
        """
        Get a secret value from Kubernetes secret store.

        Args:
            secret_name: Kubernetes secret name (e.g., "sendgrid-credentials")
            secret_key: Key within the secret (e.g., "api-key")

        Returns:
            Secret value or None if not found

        Example:
            # Get SendGrid API key
            api_key = await secret_client.get_secret("sendgrid-credentials", "api-key")
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)

        url = f"{self.base_url}/secrets/{self.secret_store}/{secret_name}"

        try:
            response = await self._client.get(url)

            if response.is_success:
                # Dapr returns the secret as a JSON object with key-value pairs
                secret_data = response.json()

                # Return the specific key if requested
                if secret_key:
                    return secret_data.get(secret_key)

                # Return the entire secret dict if no key specified
                return secret_data

            elif response.status_code == 404:
                logger.warning(
                    "secret_not_found",
                    secret_name=secret_name,
                    secret_key=secret_key,
                )
                return None
            else:
                logger.error(
                    "secret_get_failed",
                    secret_name=secret_name,
                    secret_key=secret_key,
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return None

        except httpx.HTTPError as e:
            logger.error(
                "secret_get_error",
                secret_name=secret_name,
                secret_key=secret_key,
                error=str(e),
            )
            return None

    async def get_all_secrets(self, secret_name: str) -> Optional[dict[str, str]]:
        """
        Get all key-value pairs from a Kubernetes secret.

        Args:
            secret_name: Kubernetes secret name

        Returns:
            Dictionary of all secret key-value pairs or None if not found

        Example:
            # Get all OAuth token data
            tokens = await secret_client.get_all_secrets("oauth-tokens")
            access_token = tokens.get("access-token")
        """
        return await self.get_secret(secret_name, secret_key="")


# Singleton instance for dependency injection
_secret_client: Optional[DaprSecretClient] = None


async def get_secret_client() -> DaprSecretClient:
    """Get or create the singleton Dapr Secret client."""
    global _secret_client
    if _secret_client is None:
        _secret_client = DaprSecretClient()
        await _secret_client.__aenter__()
    return _secret_client
