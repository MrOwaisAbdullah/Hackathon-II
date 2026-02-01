"""
Reminder Scheduler Service

This module calculates reminder times based on task due dates and user preferences.
"""

import structlog
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

# Configure structured logging
logger = structlog.get_logger(__name__)


class ReminderSettings(BaseModel):
    """
    Reminder settings for a task.

    Attributes:
        offsets: List of offset values before due date (e.g., ["15m", "1h", "1d", "1w"])
        channels: Notification channels (e.g., ["email", "push"])
        custom_message: Optional custom reminder message
    """

    offsets: List[str]  # ["15m", "1h", "1d", "1w"]
    channels: List[str]  # ["email", "push"]
    custom_message: Optional[str] = None


class ReminderScheduler:
    """
    Scheduler for calculating reminder times based on task due dates.

    This service handles:
    - Multiple reminder offsets per task
    - Time-based offsets (minutes, hours, days, weeks)
    - Custom reminder messages
    """

    # Offset format: <value><unit> where unit is m (minutes), h (hours), d (days), w (weeks)
    OFFSET_UNITS = {
        "m": "minutes",  # minutes
        "h": "hours",  # hours
        "d": "days",  # days
        "w": "weeks",  # weeks
    }

    @classmethod
    def calculate_reminder_times(
        cls,
        due_date: datetime,
        reminder_settings: ReminderSettings,
    ) -> List[datetime]:
        """
        Calculate reminder times for a task based on its due date and reminder settings.

        Args:
            due_date: The task's due date
            reminder_settings: User's reminder preferences for this task

        Returns:
            List of reminder datetimes, sorted ascending (earliest first)

        Example:
            due = datetime(2026, 1, 30, 17, 0)  # 5 PM on Jan 30, 2026
            settings = ReminderSettings(offsets=["1d", "1h", "15m"], channels=["email"])
            reminders = ReminderScheduler.calculate_reminder_times(due, settings)
            # Returns: [
            #   datetime(2026, 1, 29, 17, 0),  # 1 day before
            #   datetime(2026, 1, 30, 16, 0),  # 1 hour before
            #   datetime(2026, 1, 30, 16, 45),  # 15 minutes before
            # ]
        """
        reminder_times = []

        for offset in reminder_settings.offsets:
            try:
                reminder_time = cls._parse_and_apply_offset(due_date, offset)

                # Only add future reminders
                if reminder_time > datetime.now():
                    reminder_times.append(reminder_time)
                    logger.debug(
                        "reminder_scheduled",
                        due_date=due_date.isoformat(),
                        offset=offset,
                        reminder_time=reminder_time.isoformat(),
                    )

            except ValueError as e:
                logger.error(
                    "invalid_offset_format",
                    offset=offset,
                    error=str(e),
                )
                continue

        # Sort by time ascending (earliest reminders first)
        reminder_times.sort()

        return reminder_times

    @classmethod
    def _parse_and_apply_offset(cls, due_date: datetime, offset: str) -> datetime:
        """
        Parse offset string and apply it to the due date.

        Args:
            due_date: The task's due date
            offset: Offset string (e.g., "15m", "1h", "1d", "1w")

        Returns:
            Reminder datetime calculated as (due_date - offset)

        Raises:
            ValueError: If offset format is invalid
        """
        if not offset or len(offset) < 2:
            raise ValueError(f"Invalid offset format: {offset}")

        # Parse value and unit
        unit = offset[-1].lower()
        value_str = offset[:-1]

        try:
            value = int(value_str)
        except ValueError:
            raise ValueError(f"Invalid offset value: {value_str}")

        if unit not in cls.OFFSET_UNITS:
            raise ValueError(f"Invalid offset unit: {unit}. Must be one of: {list(cls.OFFSET_UNITS.keys())}")

        # Apply offset based on unit
        if unit == "m":
            return due_date - timedelta(minutes=value)
        elif unit == "h":
            return due_date - timedelta(hours=value)
        elif unit == "d":
            return due_date - timedelta(days=value)
        elif unit == "w":
            return due_date - timedelta(weeks=value)
        else:
            raise ValueError(f"Unhandled offset unit: {unit}")

    @classmethod
    def get_due_reminders(
        cls,
        reminder_times: List[datetime],
        lookback_minutes: int = 5,
    ) -> List[datetime]:
        """
        Get reminders that are due now (within the lookback period).

        This is useful for the scheduled reminder checker that runs every 5 minutes.

        Args:
            reminder_times: List of scheduled reminder times
            lookback_minutes: How many minutes back to look for due reminders

        Returns:
            List of reminder datetimes that are due

        Example:
            # Reminder checker runs every 5 minutes at :00, :05, :10, etc.
            # Current time: 2026-01-30 16:47
            # Reminders: [16:45, 16:50, 17:00]
            # Result: [16:45] (already passed) and [16:50] (within 5 min window)
            # But not [17:00] (too far in future)
        """
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=lookback_minutes)
        upper_bound = now + timedelta(minutes=lookback_minutes)

        due_reminders = [
            reminder_time
            for reminder_time in reminder_times
            if cutoff_time <= reminder_time <= upper_bound
        ]

        if due_reminders:
            logger.info(
                "reminders_due",
                count=len(due_reminders),
                due_times=[r.isoformat() for r in due_reminders],
            )

        return due_reminders

    @classmethod
    def validate_reminder_settings(cls, reminder_settings: ReminderSettings) -> bool:
        """
        Validate reminder settings configuration.

        Args:
            reminder_settings: The reminder settings to validate

        Returns:
            True if valid, False otherwise
        """
        if not reminder_settings.offsets:
            logger.error("no_offsets_provided")
            return False

        if not reminder_settings.channels:
            logger.error("no_channels_provided")
            return False

        # Validate each offset format
        for offset in reminder_settings.offsets:
            try:
                cls._parse_and_apply_offset(datetime.now(), offset)
            except ValueError as e:
                logger.error("invalid_offset", offset=offset, error=str(e))
                return False

        # Validate channels
        valid_channels = ["email", "push"]
        for channel in reminder_settings.channels:
            if channel not in valid_channels:
                logger.error("invalid_channel", channel=channel)
                return False

        return True
