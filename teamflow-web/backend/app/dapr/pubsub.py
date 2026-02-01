"""
Dapr Pub/Sub Client

This module provides async event publishing capabilities using Dapr's HTTP API.
Events are published to Kafka topics configured in the Dapr pubsub component.
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
DAPR_PUBSUB_NAME = "kafka-pubsub"


class CloudEvent(BaseModel):
    """
    CloudEvents 1.0 envelope for Kafka event publishing.

    Attributes:
        specversion: CloudEvents spec version (always "1.0")
        type: Event type (e.g., "teamflow.task.created")
        source: Event source (e.g., "teamflow-backend")
        id: Unique event ID
        time: Event timestamp (ISO 8601)
        datacontenttype: Content type of data (always "application/json")
        data: Event payload
    """

    specversion: str = "1.0"
    type: str
    source: str
    id: str
    time: str
    datacontenttype: str = "application/json"
    data: dict[str, Any]


class DaprPubSubClient:
    """
    Async Dapr Pub/Sub client for publishing events to Kafka.

    This client wraps Dapr's HTTP API for event publishing with:
    - Async/await support
    - CloudEvents envelope formatting
    - Structured logging
    - Error handling and retry logic
    """

    def __init__(
        self,
        dapr_host: str = DAPR_HTTP_HOST,
        dapr_port: int = DAPR_HTTP_PORT,
        pubsub_name: str = DAPR_PUBSUB_NAME,
    ):
        """
        Initialize the Dapr Pub/Sub client.

        Args:
            dapr_host: Dapr sidecar HTTP host
            dapr_port: Dapr sidecar HTTP port
            pubsub_name: Name of the Dapr pubsub component
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port
        self.pubsub_name = pubsub_name
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

    async def publish(
        self,
        topic: str,
        event_type: str,
        source: str,
        data: dict[str, Any],
        event_id: Optional[str] = None,
    ) -> bool:
        """
        Publish an event to a Kafka topic via Dapr.

        Args:
            topic: Kafka topic name (e.g., "task-events", "reminders")
            event_type: CloudEvents type (e.g., "teamflow.task.created")
            source: Event source (e.g., "teamflow-backend")
            data: Event payload
            event_id: Optional event ID (auto-generated if not provided)

        Returns:
            True if published successfully, False otherwise
        """
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)

        # Create CloudEvents envelope
        import time
        import uuid

        cloud_event = CloudEvent(
            type=event_type,
            source=source,
            id=event_id or str(uuid.uuid4()),
            time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            data=data,
        )

        # Construct Dapr publish URL
        url = f"{self.base_url}/publish/{self.pubsub_name}/{topic}"

        try:
            response = await self._client.post(
                url,
                json=cloud_event.model_dump(mode="json"),
                headers={"Content-Type": "application/cloudevents+json"},
            )

            if response.is_success:
                logger.info(
                    "event_published",
                    topic=topic,
                    event_type=event_type,
                    event_id=cloud_event.id,
                )
                return True
            else:
                logger.error(
                    "event_publish_failed",
                    topic=topic,
                    event_type=event_type,
                    status_code=response.status_code,
                    response_text=response.text,
                )
                return False

        except httpx.HTTPError as e:
            logger.error(
                "event_publish_error",
                topic=topic,
                event_type=event_type,
                error=str(e),
            )
            return False


# Singleton instance for dependency injection
_dapr_client: Optional[DaprPubSubClient] = None


async def get_dapr_client() -> DaprPubSubClient:
    """Get or create the singleton Dapr Pub/Sub client."""
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprPubSubClient()
        await _dapr_client.__aenter__()
    return _dapr_client
