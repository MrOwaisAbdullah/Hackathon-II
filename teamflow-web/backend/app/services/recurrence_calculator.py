"""
Recurrence Calculator Service

This module calculates next instance dates for recurring tasks using RFC 5545
recurrence rules (iCal format) via the dateutil library.
"""

import structlog
from datetime import datetime, date
from typing import Optional, List
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

# Configure structured logging
logger = structlog.get_logger(__name__)


class RecurrenceRule(BaseModel):
    """
    Recurrence rule for recurring tasks.

    Attributes:
        frequency: Recurrence frequency (daily, weekly, monthly, yearly)
        interval: How often the recurrence repeats (e.g., 1 = every, 2 = every other)
        days_of_week: Specific days of the week for weekly recurrence
        day_of_month: Specific day of month for monthly recurrence
        end_date: Optional end date for recurrence
        max_occurrences: Optional maximum number of occurrences
        time_of_day: Optional time component for "every Friday at 2 PM" scenario
    """

    frequency: str  # "daily", "weekly", "monthly", "yearly"
    interval: int = 1
    days_of_week: Optional[List[str]] = None  # ["Monday", "Tuesday", ...]
    day_of_month: Optional[int] = None  # 1-31
    end_date: Optional[date] = None
    max_occurrences: Optional[int] = None
    time_of_day: Optional[str] = None  # HH:MM format


class RecurrenceCalculator:
    """
    Calculator for recurring task next instance dates.

    This service handles:
    - Daily, weekly, monthly, yearly recurrence
    - Custom intervals
    - End date and max occurrence constraints
    - Weekend/holiday business day adjustments
    """

    # Day of week constants matching RFC 5545
    WEEKDAY_MAP = {
        "Monday": rrule.MO,
        "Tuesday": rrule.TU,
        "Wednesday": rrule.WE,
        "Thursday": rrule.TH,
        "Friday": rrule.FR,
        "Saturday": rrule.SA,
        "Sunday": rrule.SU,
    }

    @classmethod
    def calculate_next_instance(
        cls,
        current_due_date: datetime,
        recurrence_rule: RecurrenceRule,
        skip_weekends: bool = True,
        holidays: Optional[List[date]] = None,
    ) -> Optional[datetime]:
        """
        Calculate the next instance date for a recurring task.

        Args:
            current_due_date: The due date of the current completed task
            recurrence_rule: The recurrence rule configuration
            skip_weekends: If True, skip Saturday/Sunday to next business day
            holidays: Optional list of holiday dates to skip

        Returns:
            The next instance due date, or None if recurrence has ended

        Example:
            rule = RecurrenceRule(frequency="weekly", interval=1, days_of_week=["Monday"])
            next_date = RecurrenceCalculator.calculate_next_instance(
                current_due_date=datetime(2026, 1, 27),
                recurrence_rule=rule
            )
            # Returns: datetime(2026, 2, 2) - next Monday
        """
        try:
            # Build rrule parameters
            rrule_params = cls._build_rrule_params(recurrence_rule, current_due_date)

            # Apply max occurrences constraint
            if recurrence_rule.max_occurrences:
                rrule_params["count"] = recurrence_rule.max_occurrences + 1  # +1 for the first instance

            # Create recurrence rule
            rule = rrule.rrule(**rrule_params)

            # Get next occurrence after current due date
            next_date = None
            for occurrence in rule:
                # Skip the current occurrence
                if occurrence.replace(tzinfo=None) <= current_due_date:
                    continue

                next_date = occurrence.replace(tzinfo=None)

                # Apply end date constraint
                if recurrence_rule.end_date and next_date.date() > recurrence_rule.end_date:
                    logger.info(
                        "recurrence_ended_end_date",
                        end_date=recurrence_rule.end_date.isoformat(),
                    )
                    return None

                # Apply weekend/holiday adjustment
                if skip_weekends or holidays:
                    next_date = cls._adjust_for_business_day(
                        next_date.date(),
                        recurrence_rule.time_of_day,
                        skip_weekends=skip_weekends,
                        holidays=holidays or [],
                    )

                break

            if next_date:
                logger.info(
                    "next_instance_calculated",
                    current_date=current_due_date.isoformat(),
                    next_date=next_date.isoformat(),
                    frequency=recurrence_rule.frequency,
                    interval=recurrence_rule.interval,
                )
                return next_date
            else:
                logger.info("recurrence_ended_no_more_occurrences")
                return None

        except Exception as e:
            logger.error(
                "recurrence_calculation_failed",
                current_date=current_due_date.isoformat(),
                frequency=recurrence_rule.frequency,
                error=str(e),
            )
            return None

    @classmethod
    def _build_rrule_params(
        cls, recurrence_rule: RecurrenceRule, start_date: datetime
    ) -> dict:
        """Build rrule parameters from recurrence rule."""
        params = {
            "dtstart": start_date,
        }

        # Map frequency to rrule constant
        freq_map = {
            "daily": rrule.DAILY,
            "weekly": rrule.WEEKLY,
            "monthly": rrule.MONTHLY,
            "yearly": rrule.YEARLY,
        }
        params["freq"] = freq_map[recurrence_rule.frequency]
        params["interval"] = recurrence_rule.interval

        # Add byweekday for weekly recurrence with specific days
        if recurrence_rule.frequency == "weekly" and recurrence_rule.days_of_week:
            weekdays = [
                cls.WEEKDAY_MAP[day]
                for day in recurrence_rule.days_of_week
                if day in cls.WEEKDAY_MAP
            ]
            if weekdays:
                params["byweekday"] = weekdays

        # Add bymonthday for monthly recurrence with specific day
        if recurrence_rule.frequency == "monthly" and recurrence_rule.day_of_month:
            params["bymonthday"] = recurrence_rule.day_of_month

        return params

    @classmethod
    def _adjust_for_business_day(
        cls,
        target_date: date,
        time_of_day: Optional[str],
        skip_weekends: bool,
        holidays: List[date],
    ) -> datetime:
        """
        Adjust date to next business day if it falls on weekend or holiday.

        Args:
            target_date: The calculated next instance date
            time_of_day: Optional time component (HH:MM format)
            skip_weekends: If True, skip Saturday/Sunday
            holidays: List of holiday dates to skip

        Returns:
            Adjusted datetime with business day and optional time
        """
        adjusted_date = target_date

        # Skip weekends
        if skip_weekends:
            while adjusted_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                adjusted_date += relativedelta(days=1)
                logger.debug("skipped_weekend", adjusted_date=adjusted_date.isoformat())

        # Skip holidays
        while adjusted_date in holidays:
            adjusted_date += relativedelta(days=1)
            logger.debug("skipped_holiday", adjusted_date=adjusted_date.isoformat())

        # Add time component if specified
        if time_of_day:
            hour, minute = map(int, time_of_day.split(":"))
            return datetime.combine(adjusted_date, datetime.min.time()).replace(
                hour=hour, minute=minute
            )

        # Return datetime at midnight if no time specified
        return datetime.combine(adjusted_date, datetime.min.time())

    @classmethod
    def validate_recurrence_rule(cls, recurrence_rule: RecurrenceRule) -> bool:
        """
        Validate a recurrence rule configuration.

        Args:
            recurrence_rule: The recurrence rule to validate

        Returns:
            True if valid, False otherwise
        """
        valid_frequencies = ["daily", "weekly", "monthly", "yearly"]
        if recurrence_rule.frequency not in valid_frequencies:
            logger.error("invalid_frequency", frequency=recurrence_rule.frequency)
            return False

        if recurrence_rule.interval < 1:
            logger.error("invalid_interval", interval=recurrence_rule.interval)
            return False

        if recurrence_rule.day_of_month and not (1 <= recurrence_rule.day_of_month <= 31):
            logger.error("invalid_day_of_month", day=recurrence_rule.day_of_month)
            return False

        return True
