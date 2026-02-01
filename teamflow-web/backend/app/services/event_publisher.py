"""
Event Publisher Service

This module provides event publishing capabilities using the Dapr Pub/Sub client.
It wraps the Dapr client and provides convenient methods for publishing TeamFlow events.
"""

import structlog
from typing import Any, Optional
from datetime import datetime

from teamflow_web.backend.app.dapr.pubsub import DaprPubSubClient

# Configure structured logging
logger = structlog.get_logger(__name__)


class EventPublisher:
    """
    High-level event publisher for TeamFlow domain events.

    This service provides typed methods for publishing all TeamFlow events
    to Kafka via Dapr. Events are published in CloudEvents 1.0 format.

    Supported Topics:
    - task-events: Task lifecycle events (created, updated, completed, deleted, assigned)
    - reminders: Reminder events for notification service
    - time-logged: Time entry logging events
    - task-updates: All task updates for real-time sync service
    """

    # Event type constants
    EVENT_TASK_CREATED = "teamflow.task.created"
    EVENT_TASK_UPDATED = "teamflow.task.updated"
    EVENT_TASK_COMPLETED = "teamflow.task.completed"
    EVENT_TASK_DELETED = "teamflow.task.deleted"
    EVENT_TASK_ASSIGNED = "teamflow.task.assigned"

    EVENT_REMINDER_DUE = "teamflow.reminder.due"
    EVENT_REMINDER_SENT = "teamflow.reminder.sent"
    EVENT_REMINDER_FAILED = "teamflow.reminder.failed"

    EVENT_TIME_LOGGED = "teamflow.time.logged"

    # Topic constants
    TOPIC_TASK_EVENTS = "task-events"
    TOPIC_REMINDERS = "reminders"
    TOPIC_TIME_LOGGED = "time-logged"
    TOPIC_TASK_UPDATES = "task-updates"

    def __init__(self, dapr_client: Optional[DaprPubSubClient] = None):
        """
        Initialize the event publisher.

        Args:
            dapr_client: Optional Dapr Pub/Sub client (creates new one if not provided)
        """
        self.dapr_client = dapr_client

    async def _get_client(self) -> DaprPubSubClient:
        """Get or create the Dapr client."""
        if self.dapr_client is None:
            from teamflow_web.backend.app.dapr import get_dapr_client
            self.dapr_client = await get_dapr_client()
        return self.dapr_client

    async def publish_task_event(
        self,
        event_type: str,
        task_id: str,
        project_id: str,
        user_id: str,
        data: dict[str, Any],
    ) -> bool:
        """
        Publish a task lifecycle event to the task-events topic.

        Args:
            event_type: Type of task event (e.g., EVENT_TASK_CREATED)
            task_id: ID of the task
            project_id: ID of the project
            user_id: ID of the user who triggered the event
            data: Additional event data (title, status, etc.)

        Returns:
            True if published successfully, False otherwise
        """
        client = await self._get_client()

        # Build event payload
        payload = {
            "task_id": task_id,
            "project_id": project_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **data,
        }

        # Publish event
        success = await client.publish(
            topic=self.TOPIC_TASK_EVENTS,
            event_type=event_type,
            source="teamflow-backend",
            data=payload,
        )

        if success:
            logger.info(
                "task_event_published",
                event_type=event_type,
                task_id=task_id,
                project_id=project_id,
                user_id=user_id,
            )

        return success

    async def publish_task_created(
        self,
        task_id: str,
        project_id: str,
        user_id: str,
        title: str,
        status: str,
        recurrence_rule: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Publish a task created event."""
        data = {"title": title, "status": status}
        if recurrence_rule:
            data["recurrence_rule"] = recurrence_rule

        return await self.publish_task_event(
            event_type=self.EVENT_TASK_CREATED,
            task_id=task_id,
            project_id=project_id,
            user_id=user_id,
            data=data,
        )

    async def publish_task_completed(
        self,
        task_id: str,
        project_id: str,
        user_id: str,
        recurrence_rule: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Publish a task completed event."""
        return await self.publish_task_event(
            event_type=self.EVENT_TASK_COMPLETED,
            task_id=task_id,
            project_id=project_id,
            user_id=user_id,
            data={"recurrence_rule": recurrence_rule} if recurrence_rule else {},
        )

    async def publish_task_updated(
        self,
        task_id: str,
        project_id: str,
        user_id: str,
        changes: dict[str, Any],
    ) -> bool:
        """
        Publish a task updated event to both task-events and task-updates topics.

        The task-updates topic is consumed by the real-time sync service.
        """
        client = await self._get_client()

        # Build event payload
        payload = {
            "task_id": task_id,
            "project_id": project_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "changes": changes,
        }

        # Publish to task-events topic
        success1 = await client.publish(
            topic=self.TOPIC_TASK_EVENTS,
            event_type=self.EVENT_TASK_UPDATED,
            source="teamflow-backend",
            data=payload,
        )

        # Also publish to task-updates for real-time sync
        success2 = await client.publish(
            topic=self.TOPIC_TASK_UPDATES,
            event_type=self.EVENT_TASK_UPDATED,
            source="teamflow-backend",
            data=payload,
        )

        if success1 and success2:
            logger.info(
                "task_update_published",
                task_id=task_id,
                project_id=project_id,
                user_id=user_id,
            )

        return success1 and success2

    async def publish_reminder_event(
        self,
        reminder_id: str,
        task_id: str,
        user_id: str,
        due_date: str,
        channels: list[str],
        custom_message: Optional[str] = None,
    ) -> bool:
        """
        Publish a reminder event to the reminders topic.

        This event is consumed by the notification service to send notifications.
        """
        client = await self._get_client()

        payload = {
            "reminder_id": reminder_id,
            "task_id": task_id,
            "user_id": user_id,
            "due_date": due_date,
            "channels": channels,
            "custom_message": custom_message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        success = await client.publish(
            topic=self.TOPIC_REMINDERS,
            event_type=self.EVENT_REMINDER_DUE,
            source="teamflow-backend",
            data=payload,
        )

        if success:
            logger.info(
                "reminder_event_published",
                reminder_id=reminder_id,
                task_id=task_id,
                user_id=user_id,
                channels=channels,
            )

        return success

    async def publish_time_logged(
        self,
        time_entry_id: str,
        task_id: str,
        user_id: str,
        duration_minutes: int,
        notes: Optional[str] = None,
    ) -> bool:
        """Publish a time logged event to the time-logged topic."""
        client = await self._get_client()

        payload = {
            "time_entry_id": time_entry_id,
            "task_id": task_id,
            "user_id": user_id,
            "duration_minutes": duration_minutes,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        success = await client.publish(
            topic=self.TOPIC_TIME_LOGGED,
            event_type=self.EVENT_TIME_LOGGED,
            source="teamflow-backend",
            data=payload,
        )

        if success:
            logger.info(
                "time_logged_event_published",
                time_entry_id=time_entry_id,
                task_id=task_id,
                user_id=user_id,
                duration_minutes=duration_minutes,
            )

        return success


# Singleton instance for dependency injection
_event_publisher: Optional[EventPublisher] = None


async def get_event_publisher() -> EventPublisher:
    """Get or create the singleton EventPublisher."""
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
