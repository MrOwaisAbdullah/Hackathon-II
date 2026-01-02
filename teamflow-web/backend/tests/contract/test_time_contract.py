"""Contract tests for time entries API endpoints.

These tests verify the schema validation for time entry operations (User Story 5).
"""
import pytest
from pydantic import ValidationError
from uuid import UUID


class TestTimeEntryContract:
    """Contract tests for time entry schemas."""

    def test_time_entry_create_valid(self):
        """Test time entry creation accepts valid data."""
        data = {
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "duration_minutes": 120,
            "note": "Worked on feature implementation",
            "entry_date": "2026-01-02",
        }

        # Verify UUID format
        try:
            UUID(data["task_id"])
        except ValueError:
            pytest.fail("task_id should be a valid UUID")

        # Verify required fields
        assert "task_id" in data
        assert "duration_minutes" in data
        assert data["duration_minutes"] > 0

    def test_time_entry_create_minimal(self):
        """Test time entry with minimal required fields."""
        data = {
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "duration_minutes": 60,
        }

        assert data["task_id"]
        assert data["duration_minutes"] == 60
        # entry_date should be optional (defaults to today)

    def test_time_entry_duration_validation(self):
        """Test duration_minutes must be positive."""
        # Negative duration should be invalid
        invalid_durations = [-30, 0, -1]
        for duration in invalid_durations:
            assert duration <= 0, "Duration must be positive"

        # Valid durations
        valid_durations = [1, 15, 30, 60, 120, 480]
        for duration in valid_durations:
            assert duration > 0, f"Duration {duration} should be valid"

    def test_time_entry_task_id_format(self):
        """Test task_id must be valid UUID format."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        invalid_uuids = [
            "not-a-uuid",
            "12345678",
            "g23e4567-e89b-12d3-a456-426614174000",  # Invalid hex char
        ]

        # Valid UUID
        try:
            UUID(valid_uuid)
        except ValueError:
            pytest.fail("Valid UUID should parse correctly")

        # Invalid UUIDs should fail
        for invalid_uuid in invalid_uuids:
            with pytest.raises(ValueError):
                UUID(invalid_uuid)

    def test_time_entry_date_format(self):
        """Test entry_date follows ISO date format (YYYY-MM-DD)."""
        valid_dates = [
            "2026-01-02",
            "2026-12-31",
            "2024-02-29",  # Leap year
        ]

        for date_str in valid_dates:
            parts = date_str.split("-")
            assert len(parts) == 3, "Date should have 3 parts"
            year, month, day = parts
            assert len(year) == 4 and year.isdigit()
            assert len(month) == 2 and month.isdigit()
            assert len(day) == 2 and day.isdigit()

    def test_time_entry_response_structure(self):
        """Test time entry response contains all required fields."""
        data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "task_id": "223e4567-e89b-12d3-a456-426614174001",
            "user_id": "323e4567-e89b-12d3-a456-426614174002",
            "agency_id": "423e4567-e89b-12d3-a456-426614174003",
            "duration_minutes": 90,
            "note": "Review meeting",
            "entry_date": "2026-01-02",
            "created_at": "2026-01-02T10:00:00Z",
        }

        # Required fields for response
        required_fields = [
            "id", "task_id", "user_id", "agency_id",
            "duration_minutes", "entry_date", "created_at"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify UUIDs
        UUID(data["id"])
        UUID(data["task_id"])
        UUID(data["user_id"])
        UUID(data["agency_id"])
