"""
T100-T108: RealtimeSyncService - Real-Time Task Updates Microservice

FastAPI microservice that consumes task events from Kafka via Dapr
and broadcasts them to connected WebSocket clients.

Features:
- Dapr pub/sub subscription to task-updates and task-events topics
- WebSocket endpoint /ws/tasks for client connections
- JWT authentication for WebSocket connections
- Connection pooling via ConnectionManager
- Ping/pong health monitoring
- /health and /ws/health endpoints for Kubernetes
"""

import asyncio
import json
import os
from typing import Optional, Set
from datetime import datetime, timezone
from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog
import jwt

from teamflow_web.backend.microservices.realtime_sync_service.connection_manager import (
    ConnectionManager,
    get_connection_manager,
)


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")
TASK_UPDATES_TOPIC = "task-updates"
TASK_EVENTS_TOPIC = "task-events"

# Dapr configuration
DAPR_PUBSUB_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}"

# Initialize FastAPI
app = FastAPI(
    title="RealtimeSyncService",
    description="Real-time task updates via WebSocket",
    version="1.0.0",
)

# Initialize connection manager
connection_manager = get_connection_manager()


# ============ Models ============

class JWTTokenData(BaseModel):
    """JWT token payload data"""
    user_id: str
    agency_id: str
    exp: Optional[int] = None


class ConnectionAuth(BaseModel):
    """WebSocket connection auth data"""
    token: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    active_connections: int
    uptime_seconds: float


# ============ JWT Validation ============

def decode_jwt_token(token: str) -> JWTTokenData:
    """
    Decode and validate JWT token from WebSocket connection.

    Args:
        token: The JWT token string

    Returns:
        JWTTokenData with user_id and agency_id

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        agency_id = payload.get("agency_id")

        if not user_id or not agency_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return JWTTokenData(
            user_id=user_id,
            agency_id=agency_id,
            exp=payload.get("exp"),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# ============ FastAPI Endpoints ============

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "RealtimeSyncService",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    T101: Dapr subscription endpoint.

    Returns list of topic subscriptions for Dapr sidecar.
    Dapr will route matching events to our event endpoints.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TASK_UPDATES_TOPIC,
            "route": "/events/task-updates",
        },
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TASK_EVENTS_TOPIC,
            "route": "/events/task-events",
        },
    ]


@app.post("/events/task-updates")
async def handle_task_updates_event(request: Request):
    """
    T102: Consume task update events from Kafka via Dapr.

    This endpoint receives CloudEvents from Dapr pub/sub.
    Events are broadcast to all connected WebSocket clients.
    """
    try:
        event_data = await request.json()

        logger.info(
            "received_task_update_event",
            event_type=event_data.get("type"),
            event_id=event_data.get("id"),
        )

        # Extract task data from CloudEvent
        data = event_data.get("data", {})
        agency_id = data.get("agency_id")

        if agency_id:
            # Broadcast to all users in the agency
            message = {
                "type": event_data.get("type"),
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            sent_count = await connection_manager.broadcast_to_agency(agency_id, message)

            logger.info(
                "task_update_broadcast",
                agency_id=agency_id,
                sent_count=sent_count,
            )
        else:
            logger.warning(
                "task_update_event_missing_agency",
                event_data=event_data,
            )

        return JSONResponse(
            content={"status": "SUCCESS"},
            status_code=200,
        )

    except Exception as e:
        logger.error(
            "failed_to_process_task_update_event",
            error=str(e),
        )
        return JSONResponse(
            content={
                "status": "ERROR",
                "error": str(e),
            },
            status_code=500,
        )


@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """
    T103: Consume all task events from Kafka via Dapr.

    This handles task created, completed, deleted events.
    Events are broadcast to connected clients.
    """
    try:
        event_data = await request.json()

        logger.info(
            "received_task_event",
            event_type=event_data.get("type"),
            event_id=event_data.get("id"),
        )

        # Extract task data from CloudEvent
        data = event_data.get("data", {})
        agency_id = data.get("agency_id")

        # Broadcast to appropriate audience
        message = {
            "type": event_data.get("type"),
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if agency_id:
            await connection_manager.broadcast_to_agency(agency_id, message)
        else:
            # Broadcast to all if no agency specified
            await connection_manager.broadcast_to_all(message)

        logger.info(
            "task_event_broadcast",
            event_type=event_data.get("type"),
            agency_id=agency_id,
        )

        return JSONResponse(
            content={"status": "SUCCESS"},
            status_code=200,
        )

    except Exception as e:
        logger.error(
            "failed_to_process_task_event",
            error=str(e),
        )
        return JSONResponse(
            content={
                "status": "ERROR",
                "error": str(e),
            },
            status_code=500,
        )


@app.websocket("/ws/tasks")
async def websocket_tasks_endpoint(websocket: WebSocket):
    """
    T105-T107: WebSocket endpoint for real-time task updates.

    Clients connect here with JWT token authentication.
    Supports:
    - JWT authentication via token query param
    - Connection registration with user/agency context
    - Ping/pong health monitoring
    - Automatic cleanup on disconnect
    """
    # T106: JWT validation
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return

    try:
        token_data = decode_jwt_token(token)
        user_id = token_data.user_id
        agency_id = token_data.agency_id
    except HTTPException as e:
        await websocket.close(code=1008, reason=str(e.detail))
        return

    # Accept the connection
    await websocket.accept()

    # Generate unique connection ID
    from uuid import uuid4
    connection_id = str(uuid4())

    # Register the connection
    await connection_manager.register(
        connection_id=connection_id,
        user_id=user_id,
        agency_id=agency_id,
        websocket=websocket,
    )

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "connection_id": connection_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    logger.info(
        "websocket_connected",
        connection_id=connection_id,
        user_id=user_id,
        agency_id=agency_id,
    )

    try:
        # T107: Handle incoming messages (ping/pong, etc.)
        while True:
            data = await websocket.receive_json()

            # Handle pong messages
            if data.get("type") == "pong":
                await connection_manager.handle_pong(connection_id)

            # Handle subscription updates (future feature)
            elif data.get("type") == "subscribe":
                # Client wants to subscribe to specific channels
                pass

    except WebSocketDisconnect:
        logger.info(
            "websocket_disconnected",
            connection_id=connection_id,
            user_id=user_id,
        )
    except Exception as e:
        logger.error(
            "websocket_error",
            connection_id=connection_id,
            error=str(e),
        )
    finally:
        # Cleanup on disconnect
        await connection_manager.disconnect(connection_id)


@app.get("/health")
async def health_check():
    """
    T108: Health check endpoint for Kubernetes liveness probe.

    Reports service health and active connection count.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "active_connections": connection_manager.get_active_count(),
        }
    )


@app.get("/ws/health")
async def websocket_health_check():
    """
    T109: WebSocket-specific health check endpoint.

    Reports WebSocket service status.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "websocket_enabled": True,
            "active_connections": connection_manager.get_active_count(),
        }
    )


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe.

    Service is ready if it can accept connections.
    """
    return JSONResponse(
        content={
            "ready": True,
        }
    )


# ============ Startup/Shutdown ============

_start_time = datetime.utcnow()


@app.on_event("startup")
async def startup_event():
    """Log service startup and start background tasks"""
    global _start_time
    _start_time = datetime.utcnow()

    # Start ping/pong task
    await connection_manager.start_ping_task()

    logger.info(
        "RealtimeSyncService starting",
        task_updates_topic=TASK_UPDATES_TOPIC,
        task_events_topic=TASK_EVENTS_TOPIC,
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log service shutdown and cleanup resources"""
    await connection_manager.cleanup()

    logger.info("RealtimeSyncService shutting down")
