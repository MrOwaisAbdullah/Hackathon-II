"""
T039: RecurrenceRule Pydantic Model

This module defines the RecurrenceRule model for recurring task configuration.
Supports RFC 5545 recurrence rules with extensions for time-of-day.
"""

from typing import List, Optional, Literal
from datetime import date
from pydantic import BaseModel, Field, field_validator


class RecurrenceRule(BaseModel):
    """
    Recurrence rule for recurring tasks.

    Supports:
    - Daily, weekly, monthly, yearly recurrence
    - Custom intervals (e.g., every 2 weeks)
    - Specific days of week for weekly recurrence
    - Day of month for monthly recurrence
    - End date constraint
    - Maximum occurrences constraint
    - Time of day (for "every Friday at 2 PM" scenario)

    Attributes:
        frequency: Recurrence frequency (daily, weekly, monthly, yearly)
        interval: How often the recurrence repeats (default: 1 = every)
        days_of_week: Specific days for weekly recurrence (Monday-Sunday)
        day_of_month: Specific day for monthly recurrence (1-31)
        end_date: Optional end date for recurrence
        max_occurrences: Optional maximum number of occurrences
        time_of_day: Optional time component in HH:MM format
    """

    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    interval: int = Field(default=1, ge=1, description="How often to repeat (1 = every, 2 = every other)")
    days_of_week: Optional[List[Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]] = None
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    end_date: Optional[date] = None
    max_occurrences: Optional[int] = Field(default=None, ge=1)
    time_of_day: Optional[str] = Field(default=None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, v, info):
        """Validate that days_of_week is only set for weekly frequency"""
        if v is not None and info.data.get("frequency") != "weekly":
            raise ValueError("days_of_week can only be set for weekly frequency")
        return v

    @field_validator("day_of_month")
    @classmethod
    def validate_day_of_month(cls, v, info):
        """Validate that day_of_month is only set for monthly frequency"""
        if v is not None and info.data.get("frequency") != "monthly":
            raise ValueError("day_of_month can only be set for monthly frequency")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "frequency": "daily",
                    "interval": 1,
                    "description": "Every day",
                },
                {
                    "frequency": "weekly",
                    "interval": 1,
                    "days_of_week": ["Monday", "Wednesday", "Friday"],
                    "description": "Every Monday, Wednesday, and Friday",
                },
                {
                    "frequency": "weekly",
                    "interval": 2,
                    "days_of_week": ["Friday"],
                    "time_of_day": "14:00",
                    "description": "Every other Friday at 2 PM",
                },
                {
                    "frequency": "monthly",
                    "interval": 1,
                    "day_of_month": 15,
                    "description": "On the 15th of every month",
                },
                {
                    "frequency": "daily",
                    "interval": 1,
                    "max_occurrences": 10,
                    "description": "Daily for 10 occurrences",
                },
                {
                    "frequency": "weekly",
                    "interval": 1,
                    "days_of_week": ["Monday"],
                    "end_date": "2026-12-31",
                    "description": "Every Monday until end of 2026",
                },
            ]
        }
    }
