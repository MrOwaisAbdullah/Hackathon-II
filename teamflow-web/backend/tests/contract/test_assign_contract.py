"""Contract tests for task assignment endpoints.

This module tests the API contracts for task assignment operations,
ensuring request/response formats match the OpenAPI specification.
"""
import pytest
from pydantic import ValidationError
from uuid import UUID

from app.models.task import TaskAssign, TaskRead


class TestAssignTaskContract:
    """Contract tests for POST /tasks/{id}/assign endpoint."""

    def test_assign_task_request_contract(self):
        """Verify POST /tasks/{id}/assign request matches TaskAssign schema."""
        # Valid request with assignee_id
        assign_data = {
            "assignee_id": UUID("123e4567-e89b-12d3-a456-426614174100"),
        }

        # Should validate successfully
        assignment = TaskAssign(**assign_data)
        assert str(assignment.assignee_id) == "123e4567-e89b-12d3-a456-426614174100"

    def test_assign_task_missing_assignee_id(self):
        """Verify POST /tasks/{id}/assign rejects missing assignee_id."""
        with pytest.raises(ValidationError):
            TaskAssign()

    def test_assign_task_invalid_assignee_id_type(self):
        """Verify POST /tasks/{id}/assign rejects non-UUID assignee_id."""
        with pytest.raises(ValidationError):
            TaskAssign(assignee_id="not-a-uuid")

    def test_assign_task_response_contract(self):
        """Verify POST /tasks/{id}/assign response structure."""
        response_data = {
            "id": UUID("123e4567-e89b-12d3-a456-426614174100"),
            "title": "Assigned Task",
            "description": "Task description",
            "status": "todo",
            "priority": "high",
            "project_id": None,
            "assignee_id": UUID("123e4567-e89b-12d3-a456-426614174200"),
            "due_date": None,
            "created_at": "2025-01-29T12:00:00",
            "updated_at": "2025-01-29T12:00:00",
        }

        # Should validate successfully
        task = TaskRead(**response_data)

        assert task.title == "Assigned Task"
        assert task.assignee_id == UUID("123e4567-e89b-12d3-a456-426614174200")

    def test_assign_task_unassign_response_contract(self):
        """Verify POST /tasks/{id}/assign with null assignee_id for unassigning."""
        # After unassignment, the assignee_id should be None
        response_data = {
            "id": UUID("123e4567-e89b-12d3-a456-426614174100"),
            "title": "Unassigned Task",
            "description": "Task description",
            "status": "todo",
            "priority": None,
            "project_id": None,
            "assignee_id": None,  # Unassigned
            "due_date": None,
            "created_at": "2025-01-29T12:00:00",
            "updated_at": "2025-01-29T12:00:00",
        }

        # Should validate successfully
        task = TaskRead(**response_data)

        assert task.title == "Unassigned Task"
        assert task.assignee_id is None
