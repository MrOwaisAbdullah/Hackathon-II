"""
T040: ReminderSettings Pydantic Model

This module defines the ReminderSettings model for task reminder configuration.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ReminderSettings(BaseModel):
    """
    Reminder settings for tasks.

    Defines when and how reminders are sent before a task's due date.

    Attributes:
        offsets: List of time offsets before due date (e.g., ["15m", "1h", "1d", "1w"])
        channels: Notification channels (email, push, or both)
        custom_message: Optional custom reminder message
    """

    offsets: List[str] = Field(
        ...,
        description="List of offsets before due date (e.g., ['15m', '1h', '1d', '1w'])",
    )
    channels: List[Literal["email", "push"]] = Field(
        default_factory=lambda: ["email"],
        description="Notification channels to use",
    )
    custom_message: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom message to include in reminder notification",
    )

    @field_validator("offsets")
    @classmethod
    def validate_offsets(cls, v):
        """Validate offset format: number followed by unit (m/h/d/w)"""
        import re

        offset_pattern = r"^\d+[mhdw]$"
        for offset in v:
            if not re.match(offset_pattern, offset):
                raise ValueError(
                    f"Invalid offset format: {offset}. Must be like '15m', '1h', '1d', '1w'"
                )
        return v

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v):
        """Ensure at least one channel is specified"""
        if not v:
            raise ValueError("At least one notification channel must be specified")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "offsets": ["15m", "1h"],
                    "channels": ["email", "push"],
                    "description": "Remind 15 minutes and 1 hour before due date via email and push",
                },
                {
                    "offsets": ["1d", "1w"],
                    "channels": ["email"],
                    "custom_message": "Don't forget to complete this task!",
                    "description": "Remind 1 day and 1 week before due date via email with custom message",
                },
                {
                    "offsets": ["30m"],
                    "channels": ["push"],
                    "description": "Simple push notification 30 minutes before due",
                },
            ]
        }
    }
