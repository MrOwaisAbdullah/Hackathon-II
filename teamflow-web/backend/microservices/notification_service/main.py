"""
T070-T079: NotificationService - Due Date Reminder Microservice

FastAPI microservice that consumes reminder events from Kafka via Dapr
and sends email notifications via SendGrid.

Features:
- Dapr pub/sub subscription to reminders topic
- Email sending via SendGrid with retry logic
- Health and readiness endpoints for Kubernetes
- Structured logging with structlog
"""

import asyncio
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog

from teamflow_web.backend.app.models.reminder_event import (
    ReminderEvent,
    ReminderEventStatus,
    ReminderEventCreate,
)
from teamflow_web.backend.app.models.event import CloudEvent
from teamflow_web.backend.microservices.notification_service.email_client import (
    SendGridEmailClient,
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
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
INITIAL_BACKOFF_MS = int(os.getenv("INITIAL_BACKOFF_MS", "1000"))
BACKOFF_MULTIPLIER = float(os.getenv("BACKOFF_MULTIPLIER", "2.0"))

# Dapr configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")
REMINDERS_TOPIC = "reminders"

# Initialize FastAPI
app = FastAPI(
    title="NotificationService",
    description="Due date reminder notification microservice",
    version="1.0.0",
)

# Initialize email client
email_client = SendGridEmailClient(api_key=SENDGRID_API_KEY)


class NotificationService:
    """
    Service for processing reminder events and sending notifications.

    Handles:
    - Consuming reminder events from Kafka via Dapr
    - Sending emails via SendGrid
    - Retry logic with exponential backoff
    - Error tracking and reporting
    """

    def __init__(
        self,
        email_client: SendGridEmailClient,
        max_retries: int = MAX_RETRIES,
        initial_backoff_ms: int = INITIAL_BACKOFF_MS,
        backoff_multiplier: float = BACKOFF_MULTIPLIER,
    ):
        self.email_client = email_client
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.backoff_multiplier = backoff_multiplier

    async def process_reminder(self, reminder_event: ReminderEvent) -> Dict[str, Any]:
        """
        Process a single reminder event by sending email.

        Args:
            reminder_event: The reminder event to process

        Returns:
            Dict with processing status
        """
        logger.info(
            "Processing reminder event",
            reminder_id=str(reminder_event.id),
            task_id=str(reminder_event.task_id),
            user_email=reminder_event.user_email,
        )

        try:
            result = await self.email_client.send_reminder_email(reminder_event)
            logger.info(
                "Reminder email sent successfully",
                reminder_id=str(reminder_event.id),
                message_id=result.get("message_id"),
            )
            return {
                "status": "sent",
                "message_id": result.get("message_id"),
                "reminder_id": str(reminder_event.id),
            }
        except Exception as e:
            logger.error(
                "Failed to send reminder email",
                reminder_id=str(reminder_event.id),
                error=str(e),
            )
            return {
                "status": "failed",
                "error": str(e),
                "reminder_id": str(reminder_event.id),
            }

    async def process_reminder_with_retry(
        self,
        reminder_event: ReminderEvent,
    ) -> Dict[str, Any]:
        """
        Process a reminder with retry logic and exponential backoff.

        Args:
            reminder_event: The reminder event to process

        Returns:
            Dict with final status and attempt count
        """
        last_error = None
        backoff_ms = self.initial_backoff_ms

        for attempt in range(self.max_retries):
            try:
                result = await self.process_reminder(reminder_event)
                if result["status"] == "sent":
                    return {
                        **result,
                        "attempts": attempt + 1,
                    }
                last_error = result.get("error", "Unknown error")
            except Exception as e:
                last_error = str(e)

            # Exponential backoff before retry
            if attempt < self.max_retries - 1:
                logger.info(
                    "Retrying reminder email",
                    reminder_id=str(reminder_event.id),
                    attempt=attempt + 1,
                    backoff_ms=backoff_ms,
                )
                await asyncio.sleep(backoff_ms / 1000)
                backoff_ms *= self.backoff_multiplier

        # All retries exhausted
        logger.error(
            "Failed to send reminder after max retries",
            reminder_id=str(reminder_event.id),
            max_retries=self.max_retries,
            last_error=last_error,
        )
        return {
            "status": "failed",
            "error": last_error,
            "attempts": self.max_retries,
            "reminder_id": str(reminder_event.id),
        }

    async def process_batch(
        self,
        reminder_events: List[ReminderEvent],
    ) -> List[Dict[str, Any]]:
        """
        Process multiple reminder events concurrently.

        Args:
            reminder_events: List of reminder events to process

        Returns:
            List of processing results
        """
        logger.info(
            "Processing reminder batch",
            count=len(reminder_events),
        )

        tasks = [
            self.process_reminder_with_retry(reminder)
            for reminder in reminder_events
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "status": "failed",
                    "error": str(result),
                    "reminder_id": str(reminder_events[i].id),
                })
            else:
                processed_results.append(result)

        success_count = sum(1 for r in processed_results if r["status"] == "sent")
        logger.info(
            "Batch processing complete",
            total=len(reminder_events),
            success=success_count,
            failed=len(reminder_events) - success_count,
        )

        return processed_results


# Initialize service
notification_service = NotificationService(email_client=email_client)


# ============ FastAPI Endpoints ============

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "NotificationService",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    T071: Dapr subscription endpoint.

    Returns list of topic subscriptions for Dapr sidecar.
    Dapr will route matching events to our /events/reminders endpoint.
    """
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": REMINDERS_TOPIC,
            "route": "/events/reminders",
        }
    ]


@app.post("/events/reminders")
async def handle_reminder_event(request: Request):
    """
    T072: Consume reminder events from Kafka via Dapr.

    This endpoint receives CloudEvents from Dapr pub/sub.
    Event type: teamflow.task.reminder.created
    """
    try:
        # Parse CloudEvent from request body
        event_data = await request.json()

        logger.info(
            "Received reminder event",
            event_type=event_data.get("type"),
            event_id=event_data.get("id"),
        )

        # Extract reminder data from CloudEvent
        data = event_data.get("data", {})
        reminder_create = ReminderEventCreate(**data)

        # Create ReminderEvent
        reminder_event = ReminderEvent(
            id=reminder_create.task_id,  # Use task_id as reminder_id for now
            task_id=reminder_create.task_id,
            agency_id=reminder_create.agency_id,
            user_id=reminder_create.user_id,
            remind_at=reminder_create.remind_at,
            due_date=reminder_create.due_date,
            task_title=reminder_create.task_title,
            task_description=reminder_create.task_description,
            user_email=reminder_create.user_email,
            user_name=reminder_create.user_name,
            status=ReminderEventStatus.PENDING,
            created_at=datetime.now(timezone.utc),
        )

        # Process reminder with retry (T073, T074)
        result = await notification_service.process_reminder_with_retry(reminder_event)

        return JSONResponse(
            content={
                "status": "SUCCESS",
                "result": result,
            },
            status_code=200,
        )

    except Exception as e:
        logger.error(
            "Failed to process reminder event",
            error=str(e),
            event_data=event_data,
        )
        return JSONResponse(
            content={
                "status": "ERROR",
                "error": str(e),
            },
            status_code=500,
        )


@app.get("/health")
async def health_check():
    """
    T075: Health check endpoint for Kubernetes liveness probe.

    Checks SendGrid API connectivity.
    """
    health = await email_client.check_health()
    status_code = 200 if health["healthy"] else 503
    return JSONResponse(content=health, status_code=status_code)


@app.get("/ready")
async def readiness_check():
    """
    T076: Readiness check endpoint for Kubernetes readiness probe.

    Returns ready if service can accept traffic.
    """
    # Check if email client is initialized
    if email_client.client is None:
        return JSONResponse(
            content={
                "ready": False,
                "reason": "Email client not initialized",
            },
            status_code=503,
        )

    # Check SendGrid connectivity
    health = await email_client.check_health()
    if not health["healthy"]:
        return JSONResponse(
            content={
                "ready": False,
                "reason": health.get("error", "Unknown"),
            },
            status_code=503,
        )

    return JSONResponse(
        content={
            "ready": True,
        },
        status_code=200,
    )


# ============ Startup/Shutdown ============

@app.on_event("startup")
async def startup_event():
    """Log service startup"""
    logger.info(
        "NotificationService starting",
        dapr_port=DAPR_HTTP_PORT,
        pubsub_name=PUBSUB_NAME,
        reminders_topic=REMINDERS_TOPIC,
        max_retries=MAX_RETRIES,
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log service shutdown"""
    logger.info("NotificationService shutting down")
