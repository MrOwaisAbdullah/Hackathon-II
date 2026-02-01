"""
T065-T066: Integration tests for NotificationService

Test reminder event handling and email sending with retry logic.
Tests should FAIL initially (red phase), then pass after implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from teamflow_web.backend.app.models.event import CloudEvent
from teamflow_web.backend.app.models.reminder_event import ReminderEvent, ReminderEventStatus


class TestNotificationService:
    """T065-T066: Test notification service event handling"""

    @pytest.mark.asyncio
    async def test_reminder_event_triggers_email_send(self):
        """T065: Test reminder event triggers email send"""
        # Arrange: Create a reminder event
        reminder_event = ReminderEvent(
            id="reminder-123",
            task_id="task-456",
            task_title="Complete project proposal",
            task_description="Submit the Q1 project proposal",
            due_date=datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC")),
            remind_at=datetime(2026, 1, 28, 9, 0, tzinfo=ZoneInfo("UTC")),  # 1 hour before
            user_email="user@example.com",
            user_name="John Doe",
            status=ReminderEventStatus.PENDING,
            created_at=datetime.now(ZoneInfo("UTC")),
        )

        # Mock email client
        mock_email_client = AsyncMock()
        mock_email_client.send_email.return_value = {"status": "accepted", "message_id": "msg-789"}

        # Import here to avoid import errors before implementation
        from teamflow_web.backend.microservices.notification_service.main import (
            NotificationService,
            app,
        )

        # Act: Process the reminder event
        notification_service = NotificationService(email_client=mock_email_client)
        result = await notification_service.process_reminder(reminder_event)

        # Assert: Email was sent with correct parameters
        mock_email_client.send_email.assert_called_once()
        call_args = mock_email_client.send_email.call_args

        # Check email parameters
        assert call_args[1]["to_email"] == "user@example.com"
        assert "Reminder: Complete project proposal" in call_args[1]["subject"]
        assert "Due: January 28, 2026 at 10:00 AM UTC" in call_args[1]["html_content"]
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_failed_email_send_triggers_retry_with_backoff(self):
        """T066: Test failed email send triggers retry with backoff"""
        # Arrange: Reminder event
        reminder_event = ReminderEvent(
            id="reminder-123",
            task_id="task-456",
            task_title="Complete project proposal",
            task_description="Submit the Q1 project proposal",
            due_date=datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC")),
            remind_at=datetime(2026, 1, 28, 9, 0, tzinfo=ZoneInfo("UTC")),
            user_email="user@example.com",
            user_name="John Doe",
            status=ReminderEventStatus.PENDING,
            created_at=datetime.now(ZoneInfo("UTC")),
        )

        # Mock email client that fails initially then succeeds
        mock_email_client = AsyncMock()
        mock_email_client.send_email.side_effect = [
            Exception("SendGrid API error"),  # First attempt fails
            Exception("SendGrid API timeout"),  # Second attempt fails
            {"status": "accepted", "message_id": "msg-789"},  # Third attempt succeeds
        ]

        # Import here
        from teamflow_web.backend.microservices.notification_service.main import NotificationService

        # Act: Process with retry
        notification_service = NotificationService(
            email_client=mock_email_client,
            max_retries=3,
            initial_backoff_ms=100,
        )
        result = await notification_service.process_reminder_with_retry(reminder_event)

        # Assert: Called 3 times with exponential backoff
        assert mock_email_client.send_email.call_count == 3
        assert result["status"] == "sent"
        assert result["attempts"] == 3

    @pytest.mark.asyncio
    async def test_max_retries_exhausted_marks_as_failed(self):
        """Test that exhausted retries mark event as failed"""
        # Arrange
        reminder_event = ReminderEvent(
            id="reminder-123",
            task_id="task-456",
            task_title="Complete project proposal",
            task_description="Submit the Q1 project proposal",
            due_date=datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC")),
            remind_at=datetime(2026, 1, 28, 9, 0, tzinfo=ZoneInfo("UTC")),
            user_email="user@example.com",
            user_name="John Doe",
            status=ReminderEventStatus.PENDING,
            created_at=datetime.now(ZoneInfo("UTC")),
        )

        # Mock email client that always fails
        mock_email_client = AsyncMock()
        mock_email_client.send_email.side_effect = Exception("Persistent error")

        # Import
        from teamflow_web.backend.microservices.notification_service.main import NotificationService

        # Act
        notification_service = NotificationService(
            email_client=mock_email_client,
            max_retries=3,
            initial_backoff_ms=100,
        )
        result = await notification_service.process_reminder_with_retry(reminder_event)

        # Assert: Failed after max retries
        assert mock_email_client.send_email.call_count == 3  # Initial + 2 retries
        assert result["status"] == "failed"
        assert result["error"] is not None

    @pytest.mark.asyncio
    async def test_multiple_reminders_processed_independently(self):
        """Test that multiple reminder events are processed independently"""
        # Arrange: Multiple reminder events
        reminder_events = [
            ReminderEvent(
                id=f"reminder-{i}",
                task_id=f"task-{i}",
                task_title=f"Task {i}",
                task_description=f"Description {i}",
                due_date=datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC")),
                remind_at=datetime(2026, 1, 28, 9, 0, tzinfo=ZoneInfo("UTC")),
                user_email=f"user{i}@example.com",
                user_name=f"User {i}",
                status=ReminderEventStatus.PENDING,
                created_at=datetime.now(ZoneInfo("UTC")),
            )
            for i in range(1, 4)
        ]

        # Mock email client
        mock_email_client = AsyncMock()
        mock_email_client.send_email.return_value = {
            "status": "accepted",
            "message_id": "msg-789",
        }

        # Import
        from teamflow_web.backend.microservices.notification_service.main import NotificationService

        # Act: Process all reminders
        notification_service = NotificationService(email_client=mock_email_client)
        results = await notification_service.process_batch(reminder_events)

        # Assert: All processed independently
        assert len(results) == 3
        assert mock_email_client.send_email.call_count == 3
        assert all(r["status"] == "sent" for r in results)


class TestNotificationServiceEndpoints:
    """Test NotificationService FastAPI endpoints"""

    @pytest.mark.asyncio
    async def test_dapr_subscribe_endpoint(self):
        """Test /dapr/subscribe endpoint returns correct subscriptions"""
        # Import
        from teamflow_web.backend.microservices.notification_service.main import app

        # Act: Call subscribe endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/dapr/subscribe")

        # Assert: Returns reminder subscription
        assert response.status_code == 200
        subscriptions = response.json()
        assert len(subscriptions) >= 1
        assert any(s["pubsubname"] == "kafka-pubsub" and s["topic"] == "reminders" for s in subscriptions)

    @pytest.mark.asyncio
    async def test_events_reminders_endpoint_consumes_events(self):
        """Test /events/reminders route consumes reminder events"""
        # Arrange: CloudEvent for reminder
        cloud_event = {
            "specversion": "1.0",
            "type": "teamflow.task.reminder.created",
            "source": "/tasks/task-456",
            "id": "event-123",
            "time": "2026-01-28T09:00:00Z",
            "datacontenttype": "application/json",
            "data": {
                "reminder_id": "reminder-123",
                "task_id": "task-456",
                "task_title": "Complete project proposal",
                "due_date": "2026-01-28T10:00:00Z",
                "remind_at": "2026-01-28T09:00:00Z",
                "user_email": "user@example.com",
                "user_name": "John Doe",
            },
        }

        # Mock email client
        mock_email_client = AsyncMock()
        mock_email_client.send_email.return_value = {
            "status": "accepted",
            "message_id": "msg-789",
        }

        # Import
        from teamflow_web.backend.microservices.notification_service.main import app
        from fastapi.testclient import TestClient

        # Patch email client
        with patch(
            "teamflow_web.backend.microservices.notification_service.main.SendGridEmailClient",
            return_value=mock_email_client,
        ):
            client = TestClient(app)
            response = client.post("/events/reminders", json=cloud_event)

        # Assert: Event processed successfully
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"
        mock_email_client.send_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_endpoint_checks_sendgrid_connectivity(self):
        """Test /health endpoint checks SendGrid API connectivity"""
        # Import
        from teamflow_web.backend.microservices.notification_service.main import app
        from fastapi.testclient import TestClient

        # Mock healthy email client
        mock_email_client = AsyncMock()
        mock_email_client.check_health.return_value = {"healthy": True}

        with patch(
            "teamflow_web.backend.microservices.notification_service.main.SendGridEmailClient",
            return_value=mock_email_client,
        ):
            client = TestClient(app)
            response = client.get("/health")

        # Assert: Health check passes
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_ready_endpoint_for_kubernetes(self):
        """Test /ready endpoint for Kubernetes readiness probe"""
        # Import
        from teamflow_web.backend.microservices.notification_service.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/ready")

        # Assert: Ready
        assert response.status_code == 200
        assert response.json()["ready"] is True
