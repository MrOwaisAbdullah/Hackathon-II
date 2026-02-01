"""
Dapr Integration Layer

This module provides Dapr (Distributed Application Runtime) integration for TeamFlow.
Dapr enables event-driven architecture with pub/sub, state management, and service invocation.

Components:
- pubsub.py: Dapr Pub/Sub client for Kafka event publishing
- state.py: Dapr State Store client for caching
- secrets.py: Dapr Secret Store client for secret retrieval
"""

from teamflow_web.backend.app.dapr.pubsub import DaprPubSubClient, get_dapr_client
from teamflow_web.backend.app.dapr.state import DaprStateClient, get_state_client
from teamflow_web.backend.app.dapr.secrets import DaprSecretClient, get_secret_client

__all__ = [
    "DaprPubSubClient",
    "DaprStateClient",
    "DaprSecretClient",
    "get_dapr_client",
    "get_state_client",
    "get_secret_client",
]
