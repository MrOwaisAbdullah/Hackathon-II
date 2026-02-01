"""
T098-T099: Connection Manager for WebSocket Real-Time Sync

Manages WebSocket connection pooling, broadcasting, and cleanup.
"""

import asyncio
import structlog
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4
from dataclasses import dataclass, field

logger = structlog.get_logger(__name__)


@dataclass
class WebSocketConnection:
    """
    Represents a single WebSocket connection.

    Attributes:
        id: Unique connection identifier
        user_id: ID of the user who owns this connection
        agency_id: ID of the agency the user belongs to
        websocket: The WebSocket instance for sending messages
        connected_at: When this connection was established
        last_ping_at: When the last ping was received
        is_connected: Whether the connection is active
    """
    id: str
    user_id: str
    agency_id: str
    websocket: any  # WebSocket instance from fastapi WebSocket
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping_at: Optional[datetime] = None
    is_connected: bool = True

    async def send(self, message: dict) -> bool:
        """
        Send a message to this WebSocket connection.

        Args:
            message: The message to send (will be JSON serialized)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_connected:
            return False

        try:
            import json
            await self.websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(
                "websocket_send_failed",
                connection_id=self.id,
                user_id=self.user_id,
                error=str(e),
            )
            self.is_connected = False
            return False


class ConnectionManager:
    """
    Manages WebSocket connection pooling for real-time updates.

    Handles:
    - Connection registration and cleanup
    - Broadcasting to specific users or entire agencies
    - Connection health monitoring via ping/pong
    """

    def __init__(self):
        """Initialize the connection manager."""
        # All active connections by connection ID
        self.connections: Dict[str, WebSocketConnection] = {}

        # User ID -> Set of connection IDs (for multi-device support)
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)

        # Agency ID -> Set of user IDs (for agency-wide broadcasts)
        self.agency_users: Dict[str, Set[str]] = defaultdict(set)

        # Ping interval and timeout (seconds)
        self.ping_interval = 30
        self.pong_timeout = 60

        # Background task for ping/pong
        self._ping_task: Optional[asyncio.Task] = None

    async def register(
        self,
        connection_id: str,
        user_id: str,
        agency_id: str,
        websocket: any,
    ) -> WebSocketConnection:
        """
        Register a new WebSocket connection.

        Args:
            connection_id: Unique identifier for this connection
            user_id: ID of the user
            agency_id: ID of the agency
            websocket: The WebSocket instance

        Returns:
            The created WebSocketConnection
        """
        connection = WebSocketConnection(
            id=connection_id,
            user_id=user_id,
            agency_id=agency_id,
            websocket=websocket,
        )

        self.connections[connection_id] = connection
        self.user_connections[user_id].add(connection_id)
        self.agency_users[agency_id].add(user_id)

        logger.info(
            "websocket_registered",
            connection_id=connection_id,
            user_id=user_id,
            agency_id=agency_id,
        )

        return connection

    async def disconnect(self, connection_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            connection_id: The connection ID to remove
        """
        if connection_id not in self.connections:
            return

        connection = self.connections[connection_id]
        user_id = connection.user_id
        agency_id = connection.agency_id

        # Mark as disconnected
        connection.is_connected = False

        # Remove from connections
        del self.connections[connection_id]

        # Remove from user connections
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Check if user has any other connections, if not remove from agency
        user_has_connections = user_id in self.user_connections
        if not user_has_connections and agency_id in self.agency_users:
            self.agency_users[agency_id].discard(user_id)
            if not self.agency_users[agency_id]:
                del self.agency_users[agency_id]

        logger.info(
            "websocket_disconnected",
            connection_id=connection_id,
            user_id=user_id,
            agency_id=agency_id,
        )

    async def broadcast_to_user(self, user_id: str, message: dict) -> int:
        """
        Broadcast a message to all connections for a specific user.

        Args:
            user_id: The user ID to broadcast to
            message: The message to send

        Returns:
            Number of connections the message was sent to
        """
        connection_ids = self.user_connections.get(user_id, set())
        sent_count = 0

        for conn_id in list(connection_ids):  # Use list() to avoid modification during iteration
            if conn_id in self.connections:
                connection = self.connections[conn_id]
                if await connection.send(message):
                    sent_count += 1

        logger.debug(
            "broadcast_to_user",
            user_id=user_id,
            sent_count=sent_count,
            total_connections=len(connection_ids),
        )

        return sent_count

    async def broadcast_to_agency(self, agency_id: str, message: dict) -> int:
        """
        Broadcast a message to all connections in an agency.

        Args:
            agency_id: The agency ID to broadcast to
            message: The message to send

        Returns:
            Number of connections the message was sent to
        """
        user_ids = self.agency_users.get(agency_id, set())
        sent_count = 0

        for user_id in user_ids:
            sent_count += await self.broadcast_to_user(user_id, message)

        logger.debug(
            "broadcast_to_agency",
            agency_id=agency_id,
            sent_count=sent_count,
            total_users=len(user_ids),
        )

        return sent_count

    async def broadcast_to_all(self, message: dict) -> int:
        """
        Broadcast a message to all active connections.

        Args:
            message: The message to send

        Returns:
            Number of connections the message was sent to
        """
        sent_count = 0

        # Get all connection IDs to avoid modification during iteration
        connection_ids = list(self.connections.keys())

        for conn_id in connection_ids:
            if conn_id in self.connections:
                connection = self.connections[conn_id]
                if await connection.send(message):
                    sent_count += 1

        logger.debug(
            "broadcast_to_all",
            sent_count=sent_count,
            total_connections=len(self.connections),
        )

        return sent_count

    def get_connections_for_user(self, user_id: str) -> List[WebSocketConnection]:
        """
        Get all active connections for a user.

        Args:
            user_id: The user ID

        Returns:
            List of WebSocketConnection objects
        """
        connection_ids = self.user_connections.get(user_id, set())
        return [
            self.connections[conn_id]
            for conn_id in connection_ids
            if conn_id in self.connections
        ]

    def get_connections_for_agency(self, agency_id: str) -> List[WebSocketConnection]:
        """
        Get all active connections for an agency.

        Args:
            agency_id: The agency ID

        Returns:
            List of WebSocketConnection objects
        """
        user_ids = self.agency_users.get(agency_id, set())
        connections = []

        for user_id in user_ids:
            connections.extend(self.get_connections_for_user(user_id))

        return connections

    def get_active_count(self) -> int:
        """
        Get the total number of active connections.

        Returns:
            Number of active connections
        """
        return len(self.connections)

    async def start_ping_task(self) -> None:
        """
        Start the background ping/pong task for connection health monitoring.

        Sends ping every 30 seconds and cleans up connections that don't respond within 60 seconds.
        """
        if self._ping_task is not None:
            return

        async def ping_loop():
            while True:
                await asyncio.sleep(self.ping_interval)
                await self._ping_all_connections()

        self._ping_task = asyncio.create_task(ping_loop())
        logger.info("ping_task_started", interval=self.ping_interval)

    async def _ping_all_connections(self) -> None:
        """
        Send ping to all connections and clean up stale ones.
        """
        now = datetime.utcnow()
        stale_connections = []

        for conn_id, connection in list(self.connections.items()):
            # Check if connection hasn't responded to ping
            if (
                connection.last_ping_at
                and (now - connection.last_ping_at).total_seconds() > self.pong_timeout
            ):
                stale_connections.append(conn_id)
                continue

            # Send ping
            try:
                await connection.websocket.send_json({"type": "ping"})
            except Exception as e:
                logger.warning(
                    "ping_failed",
                    connection_id=conn_id,
                    error=str(e),
                )
                stale_connections.append(conn_id)

        # Clean up stale connections
        for conn_id in stale_connections:
            await self.disconnect(conn_id)
            logger.info(
                "stale_connection_cleaned",
                connection_id=conn_id,
            )

    async def handle_pong(self, connection_id: str) -> None:
        """
        Handle a pong response from a client.

        Args:
            connection_id: The connection ID
        """
        if connection_id in self.connections:
            self.connections[connection_id].last_ping_at = datetime.utcnow()

    async def cleanup(self) -> None:
        """
        Cleanup resources when shutting down.
        """
        # Cancel ping task
        if self._ping_task:
            self._ping_task.cancel()
            try:
                await self._ping_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        for conn_id in list(self.connections.keys()):
            await self.disconnect(conn_id)

        logger.info("connection_manager_cleanup_complete")


# Singleton instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create the singleton ConnectionManager."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager
