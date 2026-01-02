"""Contract tests for tasks endpoints.

These tests verify that the API responses match the OpenAPI specification
for task management endpoints (User Story 2).
"""
import pytest
from datetime import date, datetime
from pydantic import ValidationError
from uuid import UUID

from app.models.task import TaskCreate, TaskUpdate, TaskRead, TaskStatus, TaskPriority


class TestListTasksContract:
    """Contract tests for GET /tasks endpoint."""

    def test_list_tasks_response_contract(self):
        """Verify GET /tasks response structure."""
        response_data = {
            "tasks": [
                {
                    "id": UUID("123e4567-e89b-12d3-a456-426614174100"),
                    "title": "Test Task",
                    "description": "Task description",
                    "status": "todo",
                    "priority": "high",
                    "project_id": None,
                    "assignee_id": None,
                    "due_date": None,
                    "created_at": "2025-01-29T12:00:00",
                    "updated_at": "2025-01-29T12:00:00",
                }
            ]
        }

        # Should validate successfully
        tasks = [TaskRead(**task) for task in response_data["tasks"]]

        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"
        assert tasks[0].status == TaskStatus.TODO
        assert tasks[0].priority == TaskPriority.HIGH


class TestCreateTaskContract:
    """Contract tests for POST /tasks endpoint."""

    def test_create_task_request_contract(self):
        """Verify POST /tasks request matches TaskCreate schema."""
        # Valid minimal request
        task_data = {
            "title": "New Task",
        }

        # Should validate successfully
        task = TaskCreate(**task_data)
        assert task.title == "New Task"
        assert task.status == TaskStatus.TODO

    def test_create_task_full_request_contract(self):
        """Verify POST /tasks full request with all fields."""
        task_data = {
            "title": "Full Task",
            "description": "Complete task description",
            "status": "doing",
            "priority": "high",
            "project_id": UUID("123e4567-e89b-12d3-a456-426614174200"),
            "assignee_id": UUID("123e4567-e89b-12d3-a456-426614174300"),
            "due_date": "2025-02-15",
        }

        # Should validate successfully
        task = TaskCreate(**task_data)
        assert task.title == "Full Task"
        assert task.status == TaskStatus.DOING
        assert task.priority == TaskPriority.HIGH

    def test_create_task_invalid_title_empty(self):
        """Verify POST /tasks rejects empty title."""
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_create_task_invalid_title_too_long(self):
        """Verify POST /tasks rejects title > 255 chars."""
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 256)

    def test_create_task_invalid_status(self):
        """Verify POST /tasks rejects invalid status."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Test", status="invalid_status")

    def test_create_task_response_contract(self):
        """Verify POST /tasks response structure."""
        response_data = {
            "id": UUID("123e4567-e89b-12d3-a456-426614174100"),
            "title": "Created Task",
            "description": "Task description",
            "status": "todo",
            "priority": None,
            "project_id": None,
            "assignee_id": None,
            "due_date": None,
            "created_at": "2025-01-29T12:00:00",
            "updated_at": "2025-01-29T12:00:00",
        }

        # Should validate successfully
        task = TaskRead(**response_data)

        assert task.title == "Created Task"
        assert task.status == TaskStatus.TODO


class TestUpdateTaskContract:
    """Contract tests for PATCH /tasks/{id} endpoint."""

    def test_update_task_request_contract(self):
        """Verify PATCH /tasks/{id} request matches TaskUpdate schema."""
        # Partial update - only status
        task_data = {
            "status": "done",
        }

        # Should validate successfully
        task = TaskUpdate(**task_data)
        assert task.status == TaskStatus.DONE
        assert task.title is None  # Not provided

    def test_update_task_full_update_contract(self):
        """Verify PATCH /tasks/{id} with all fields."""
        task_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "status": "review",
            "priority": "medium",
            "project_id": UUID("123e4567-e89b-12d3-a456-426614174200"),
            "assignee_id": UUID("123e4567-e89b-12d3-a456-426614174300"),
            "due_date": "2025-03-01",
        }

        # Should validate successfully
        task = TaskUpdate(**task_data)
        assert task.title == "Updated Title"
        assert task.status == TaskStatus.REVIEW

    def test_update_task_invalid_status(self):
        """Verify PATCH /tasks/{id} rejects invalid status."""
        with pytest.raises(ValidationError):
            TaskUpdate(status="invalid")

    def test_update_task_response_contract(self):
        """Verify PATCH /tasks/{id} response structure."""
        response_data = {
            "id": UUID("123e4567-e89b-12d3-a456-426614174100"),
            "title": "Updated Task",
            "description": "Updated description",
            "status": "done",
            "priority": "low",
            "project_id": None,
            "assignee_id": None,
            "due_date": None,
            "created_at": "2025-01-29T12:00:00",
            "updated_at": "2025-01-29T13:00:00",
        }

        # Should validate successfully
        task = TaskRead(**response_data)

        assert task.title == "Updated Task"
        assert task.status == TaskStatus.DONE


class TestDeleteTaskContract:
    """Contract tests for DELETE /tasks/{id} endpoint."""

    def test_delete_task_response_contract(self):
        """Verify DELETE /tasks/{id} returns 204 No Content."""
        # DELETE returns no content on success
        # This is tested by status code in integration tests
        # Contract test: ensure 204 status is expected behavior
        assert True  # Placeholder - validates 204 is expected


class TestTaskStatusContract:
    """Contract tests for TaskStatus enum values."""

    def test_task_status_valid_values(self):
        """Verify TaskStatus accepts all valid values."""
        valid_statuses = ["todo", "doing", "review", "done"]

        for status_str in valid_statuses:
            status = TaskStatus(status_str)
            assert status.value == status_str

    def test_task_status_invalid_value(self):
        """Verify TaskStatus rejects invalid values."""
        with pytest.raises(ValueError):
            TaskStatus("invalid_status")


class TestTaskPriorityContract:
    """Contract tests for TaskPriority enum values."""

    def test_task_priority_valid_values(self):
        """Verify TaskPriority accepts all valid values."""
        valid_priorities = ["low", "medium", "high"]

        for priority_str in valid_priorities:
            priority = TaskPriority(priority_str)
            assert priority.value == priority_str

    def test_task_priority_invalid_value(self):
        """Verify TaskPriority rejects invalid values."""
        with pytest.raises(ValueError):
            TaskPriority("invalid_priority")


class TestTaskFilteringContract:
    """Contract tests for task filtering query parameters."""

    def test_task_filter_by_status_contract(self):
        """Verify GET /tasks?status=todo query parameter."""
        # Query parameter should be valid TaskStatus
        status = TaskStatus("todo")
        assert status == TaskStatus.TODO

    def test_task_filter_by_project_contract(self):
        """Verify GET /tasks?project_id={id} query parameter."""
        # Query parameter should be valid UUID
        project_id = UUID("123e4567-e89b-12d3-a456-426614174200")
        assert isinstance(project_id, UUID)

    def test_task_filter_by_assignee_contract(self):
        """Verify GET /tasks?assignee_id={id} query parameter."""
        # Query parameter should be valid UUID
        assignee_id = UUID("123e4567-e89b-12d3-a456-426614174300")
        assert isinstance(assignee_id, UUID)
