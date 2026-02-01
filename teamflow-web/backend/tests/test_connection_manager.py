"""
T090-T093: Unit tests for ConnectionManager

Test WebSocket connection registration, broadcasting, and cleanup.
Tests should FAIL initially (red phase), then pass after implementation.
"""

import pytest
from asyncio import Queue
from unittest.mock import AsyncMock, MagicMock

from teamflow_web.backend.microservices.realtime_sync_service.connection_manager import (
    ConnectionManager,
    WebSocketConnection,
)


class TestWebSocketConnection:
    """T090: Test WebSocket connection data model"""

    def test_websocket_connection_creation(self):
        """Test WebSocketConnection is created with correct metadata"""
        # Arrange
        user_id = "user-123"
        agency_id = "agency-456"
        websocket = AsyncMock()

        # Act
        connection = WebSocketConnection(
            user_id=user_id,
            agency_id=agency_id,
            websocket=websocket,
        )

        # Assert
        assert connection.user_id == user_id
        assert connection.agency_id == agency_id
        assert connection.websocket == websocket
        assert connection.is_connected is True


class TestConnectionManager:
    """T091-T093: Test connection pool management"""

    @pytest.mark.asyncio
    async def test_websocket_connection_registration(self):
        """T090: Test WebSocket connection registration"""
        # Arrange
        manager = ConnectionManager()
        user_id = "user-123"
        agency_id = "agency-456"
        connection_id = "conn-789"
        websocket = AsyncMock()

        # Act
        await manager.register(connection_id, user_id, agency_id, websocket)

        # Assert
        assert connection_id in manager.connections
        assert user_id in manager.user_connections
        assert len(manager.get_connections_for_user(user_id)) == 1

    @pytest.mark.asyncio
    async def test_websocket_broadcast_to_single_user(self):
        """T091: Test WebSocket broadcast to single user"""
        # Arrange
        manager = ConnectionManager()
        user_id = "user-123"
        agency_id = "agency-456"
        connection_id = "conn-789"
        websocket = AsyncMock()

        await manager.register(connection_id, user_id, agency_id, websocket)

        message = {"type": "task_updated", "task_id": "task-456"}
        queue = Queue()

        # Mock the websocket send method to put message in queue
        async def mock_send(msg):
            await queue.put(msg)

        websocket.send = mock_send

        # Act
        await manager.broadcast_to_user(user_id, message)

        # Assert
        received = await queue.get()
        assert received["type"] == "task_updated"
        assert received["task_id"] == "task-456"

    @pytest.mark.asyncio
    async def test_websocket_broadcast_to_all_users(self):
        """T092: Test WebSocket broadcast to all users in an agency"""
        # Arrange
        manager = ConnectionManager()
        agency_id = "agency-456"

        # Create multiple users with connections
        websockets = []
        for i in range(3):
            user_id = f"user-{i}"
            connection_id = f"conn-{i}"
            websocket = AsyncMock()
            websockets.append(websocket)
            await manager.register(connection_id, user_id, agency_id, websocket)

        message = {"type": "task_created", "task_id": "task-789"}
        queues = [Queue() for _ in range(3)]

        # Mock each websocket send method
        for i, ws in enumerate(websockets):
            async def mock_send(msg, q=queues[i]):
                await q.put(msg)
            ws.send = mock_send

        # Act
        await manager.broadcast_to_agency(agency_id, message)

        # Assert - all users received the message
        for queue in queues:
            received = await queue.get()
            assert received["type"] == "task_created"
            assert received["task_id"] == "task-789"

    @pytest.mark.asyncio
    async def test_websocket_disconnection_cleanup(self):
        """T093: Test WebSocket disconnection cleanup"""
        # Arrange
        manager = ConnectionManager()
        user_id = "user-123"
        agency_id = "agency-456"
        connection_id = "conn-789"
        websocket = AsyncMock()

        await manager.register(connection_id, user_id, agency_id, websocket)

        # Verify connection exists
        assert connection_id in manager.connections
        assert user_id in manager.user_connections

        # Act
        await manager.disconnect(connection_id)

        # Assert - connection removed
        assert connection_id not in manager.connections
        # User still in user_connections but with empty connection list
        user_conns = manager.get_connections_for_user(user_id)
        assert len(user_conns) == 0

    @pytest.mark.asyncio
    async def test_get_active_connections_count(self):
        """Test getting active connections count"""
        # Arrange
        manager = ConnectionManager()
        agency_id = "agency-456"

        # Register multiple connections
        for i in range(5):
            user_id = f"user-{i}"
            connection_id = f"conn-{i}"
            websocket = AsyncMock()
            await manager.register(connection_id, user_id, agency_id, websocket)

        # Act
        count = manager.get_active_count()

        # Assert
        assert count == 5

    @pytest.mark.asyncio
    async def test_get_connections_for_agency(self):
        """Test getting all connections for an agency"""
        # Arrange
        manager = ConnectionManager()
        agency_id_1 = "agency-1"
        agency_id_2 = "agency-2"

        # Register connections for agency 1
        for i in range(3):
            await manager.register(f"conn-{i}", f"user-{i}", agency_id_1, AsyncMock())

        # Register connections for agency 2
        for i in range(2):
            await manager.register(f"conn-{i+3}", f"user-{i+3}", agency_id_2, AsyncMock())

        # Act
        agency_1_connections = manager.get_connections_for_agency(agency_id_1)
        agency_2_connections = manager.get_connections_for_agency(agency_id_2)

        # Assert
        assert len(agency_1_connections) == 3
        assert len(agency_2_connections) == 2
