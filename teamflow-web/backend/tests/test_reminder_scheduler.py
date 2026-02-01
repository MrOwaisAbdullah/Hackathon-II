"""
T060-T064: Unit tests for ReminderScheduler

Test reminder time calculation for various offset configurations.
Tests should FAIL initially (red phase), then pass after implementation.
"""

import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from teamflow_web.backend.app.services.reminder_scheduler import ReminderScheduler, ReminderSettings


class TestReminderScheduler:
    """T060-T064: Test reminder time calculation logic"""

    def test_reminder_time_calculation_15m_offset(self):
        """T060: Test reminder time calculation for '15m' offset"""
        # Arrange: Task due tomorrow at 10 AM
        due_date = datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC"))
        reminder_settings = ReminderSettings(
            offsets=["15m"],  # 15 minutes before
            channels=["email"]
        )

        # Act: Calculate reminder times
        reminder_times = ReminderScheduler.calculate_reminder_times(
            due_date=due_date,
            reminder_settings=reminder_settings
        )

        # Assert: Should have 1 reminder 15 minutes before
        assert len(reminder_times) == 1
        expected_time = datetime(2026, 1, 28, 9, 45, tzinfo=ZoneInfo("UTC"))
        assert reminder_times[0] == expected_time

    def test_reminder_time_calculation_1h_offset(self):
        """T061: Test reminder time calculation for '1h' offset"""
        # Arrange: Task due tomorrow at 10 AM
        due_date = datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC"))
        reminder_settings = ReminderSettings(
            offsets=["1h"],  # 1 hour before
            channels=["email"]
        )

        # Act: Calculate reminder times
        reminder_times = ReminderScheduler.calculate_reminder_times(
            due_date=due_date,
            reminder_settings=reminder_settings
        )

        # Assert: Should have 1 reminder 1 hour before
        assert len(reminder_times) == 1
        expected_time = datetime(2026, 1, 28, 9, 0, tzinfo=ZoneInfo("UTC"))
        assert reminder_times[0] == expected_time

    def test_reminder_time_calculation_1d_offset(self):
        """T062: Test reminder time calculation for '1d' offset"""
        # Arrange: Task due tomorrow at 10 AM
        due_date = datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC"))
        reminder_settings = ReminderSettings(
            offsets=["1d"],  # 1 day before
            channels=["email"]
        )

        # Act: Calculate reminder times
        reminder_times = ReminderScheduler.calculate_reminder_times(
            due_date=due_date,
            reminder_settings=reminder_settings
        )

        # Assert: Should have 1 reminder 1 day before
        assert len(reminder_times) == 1
        expected_time = datetime(2026, 1, 27, 10, 0, tzinfo=ZoneInfo("UTC"))
        assert reminder_times[0] == expected_time

    def test_reminder_time_calculation_1w_offset(self):
        """T063: Test reminder time calculation for '1w' offset"""
        # Arrange: Task due in 1 week at 10 AM
        due_date = datetime(2026, 2, 3, 10, 0, tzinfo=ZoneInfo("UTC"))
        reminder_settings = ReminderSettings(
            offsets=["1w"],  # 1 week before
            channels=["email"]
        )

        # Act: Calculate reminder times
        reminder_times = ReminderScheduler.calculate_reminder_times(
            due_date=due_date,
            reminder_settings=reminder_settings
        )

        # Assert: Should have 1 reminder 1 week before
        assert len(reminder_times) == 1
        expected_time = datetime(2026, 1, 27, 10, 0, tzinfo=ZoneInfo("UTC"))
        assert reminder_times[0] == expected_time

    def test_multiple_reminder_offsets_create_multiple_reminders(self):
        """T064: Test multiple reminder offsets create multiple reminder events"""
        # Arrange: Task due tomorrow with multiple reminders
        due_date = datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC"))
        reminder_settings = ReminderSettings(
            offsets=["1d", "1h", "15m"],  # 1 day, 1 hour, 15 minutes before
            channels=["email", "push"]
        )

        # Act: Calculate reminder times
        reminder_times = ReminderScheduler.calculate_reminder_times(
            due_date=due_date,
            reminder_settings=reminder_settings
        )

        # Assert: Should have 3 reminders at correct times
        assert len(reminder_times) == 3

        # Check times are correct and sorted
        expected_times = [
            datetime(2026, 1, 27, 10, 0, tzinfo=ZoneInfo("UTC")),   # 1 day before
            datetime(2026, 1, 28, 9, 0, tzinfo=ZoneInfo("UTC")),     # 1 hour before
            datetime(2026, 1, 28, 9, 45, tzinfo=ZoneInfo("UTC")),    # 15 min before
        ]
        assert reminder_times == sorted(expected_times)

    def test_past_reminder_times_are_filtered(self):
        """Test that past reminder times are filtered out"""
        # Arrange: Task due in the past
        past_due_date = datetime(2025, 1, 1, 10, 0, tzinfo=ZoneInfo("UTC"))
        reminder_settings = ReminderSettings(
            offsets=["1h"],
            channels=["email"]
        )

        # Act
        reminder_times = ReminderScheduler.calculate_reminder_times(
            due_date=past_due_date,
            reminder_settings=reminder_settings
        )

        # Assert: Should return empty since all reminder times are in the past
        assert len(reminder_times) == 0

    def test_get_due_reminders_within_lookback_window(self):
        """Test get_due_reminders returns reminders within lookback window"""
        # Arrange
        now = datetime(2026, 1, 28, 10, 0, tzinfo=ZoneInfo("UTC"))
        reminder_times = [
            now - timedelta(minutes=3),   # Within lookback
            now + timedelta(minutes=2),   # Within future window
            now + timedelta(minutes=10),  # Outside window
        ]

        # Act
        due_reminders = ReminderScheduler.get_due_reminders(
            reminder_times=reminder_times,
            lookback_minutes=5
        )

        # Assert: Should return 2 reminders (3 min ago and 2 min ahead)
        assert len(due_reminders) == 2
        assert due_reminders[0] == now - timedelta(minutes=3)
        assert due_reminders[1] == now + timedelta(minutes=2)

    def test_validate_reminder_settings_valid(self):
        """Test validation passes for valid settings"""
        # Arrange
        reminder_settings = ReminderSettings(
            offsets=["15m", "1h"],
            channels=["email", "push"]
        )

        # Act
        is_valid = ReminderScheduler.validate_reminder_settings(reminder_settings)

        # Assert
        assert is_valid is True

    def test_validate_reminder_settings_invalid_offset(self):
        """Test validation fails for invalid offset format"""
        # Arrange
        reminder_settings = ReminderSettings(
            offsets=["invalid"],  # Invalid format
            channels=["email"]
        )

        # Act
        is_valid = ReminderScheduler.validate_reminder_settings(reminder_settings)

        # Assert
        assert is_valid is False

    def test_validate_reminder_settings_invalid_channel(self):
        """Test validation fails for invalid channel"""
        # Arrange: Create settings manually to bypass Pydantic validation
        from teamflow_web.backend.app.services.reminder_scheduler import ReminderSettings as SchedulerReminderSettings
        reminder_settings = SchedulerReminderSettings(
            offsets=["15m"],
            channels=["sms"]  # Invalid channel
        )

        # Act
        is_valid = ReminderScheduler.validate_reminder_settings(reminder_settings)

        # Assert
        assert is_valid is False
