"""
T041: TaskEvent Pydantic Model

This module defines the TaskEvent model following CloudEvents 1.0 specification.
Used for event-driven communication via Kafka.
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CloudEventEnvelope(BaseModel):
    """
    CloudEvents 1.0 envelope for all TeamFlow events.

    https://github.com/cloudevents/spec/blob/v1.0.0/cloudevents/spec.md

    Attributes:
        specversion: CloudEvents spec version (always "1.0")
        type: Event type (e.g., "teamflow.task.created")
        source: Event source (e.g., "teamflow-backend")
        id: Unique event ID
        time: Event timestamp (ISO 8601)
        datacontenttype: Content type of data (always "application/json")
        data: Event payload
    """

    specversion: str = Field(default="1.0", description="CloudEvents spec version")
    type: str = Field(..., description="Event type")
    source: str = Field(..., description="Event source")
    id: str = Field(..., description="Unique event ID")
    time: str = Field(..., description="Event timestamp (ISO 8601)")
    datacontenttype: str = Field(default="application/json", description="Content type")
    data: dict[str, Any] = Field(default_factory=dict, description="Event payload")


class TaskEvent(BaseModel):
    """
    Task-related event for Kafka messaging.

    This model represents task lifecycle events that are published to the
    task-events topic for consumption by microservices.

    Attributes:
        task_id: ID of the task
        project_id: ID of the project
        user_id: ID of the user who triggered the event
        title: Task title
        status: Task status (created, in_progress, completed, cancelled)
        recurrence_rule: Optional recurrence rule for recurring tasks
        reminder_settings: Optional reminder settings
        timestamp: When the event occurred
        event_type: Type of event (for backwards compatibility)
    """

    task_id: str
    project_id: str
    user_id: str
    title: str
    status: str
    recurrence_rule: Optional[dict[str, Any]] = None
    reminder_settings: Optional[dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    changes: Optional[dict[str, Any]] = Field(
        default=None,
        description="For update events: what fields changed",
    )

    def to_cloud_event(
        self,
        event_type: str,
        source: str = "teamflow-backend",
        event_id: Optional[str] = None,
    ) -> CloudEventEnvelope:
        """Convert to CloudEvents envelope"""
        import uuid

        return CloudEventEnvelope(
            type=event_type,
            source=source,
            id=event_id or str(uuid.uuid4()),
            time=self.timestamp,
            data=self.model_dump(),
        )


# Event type constants (matching EventPublisher service)
class TaskEventType:
    """Constants for task event types"""
    TASK_CREATED = "teamflow.task.created"
    TASK_UPDATED = "teamflow.task.updated"
    TASK_COMPLETED = "teamflow.task.completed"
    TASK_DELETED = "teamflow.task.deleted"
    TASK_ASSIGNED = "teamflow.task.assigned"


class ReminderEventType:
    """Constants for reminder event types"""
    REMINDER_DUE = "teamflow.reminder.due"
    REMINDER_SENT = "teamflow.reminder.sent"
    REMINDER_FAILED = "teamflow.reminder.failed"


class TimeLogEventType:
    """Constants for time logging event types"""
    TIME_LOGGED = "teamflow.time.logged"
