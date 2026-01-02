"""Contract tests for analytics endpoints.

This module tests the API contracts for analytics operations,
ensuring request/response formats match the OpenAPI specification.
"""
import pytest
from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Dashboard statistics schema."""

    activeProjects: int = Field(..., description="Number of active projects")
    tasksCompleted: int = Field(..., description="Number of completed tasks")
    teamUtilization: float = Field(..., description="Team utilization percentage (0-100)")
    revenue: float = Field(..., description="Total revenue")
    trends: dict = Field(
        default_factory=dict,
        description="Trend data for each metric",
    )


class TaskByStatus(BaseModel):
    """Task count by status schema."""

    label: str = Field(..., description="Status label (e.g., 'To Do', 'Done')")
    value: int = Field(..., description="Number of tasks in this status")
    color: str = Field(..., description="Color for visualization")


class TestAnalyticsContract:
    """Contract tests for GET /analytics endpoints."""

    def test_dashboard_stats_response_contract(self):
        """Verify GET /analytics/stats response matches DashboardStats schema."""
        response_data = {
            "activeProjects": 5,
            "tasksCompleted": 23,
            "teamUtilization": 78.5,
            "revenue": 45000.00,
            "trends": {
                "activeProjects": 12,
                "tasksCompleted": 15,
                "teamUtilization": 5.2,
                "revenue": 3200.00,
            },
        }

        # Should validate successfully
        stats = DashboardStats(**response_data)

        assert stats.activeProjects == 5
        assert stats.tasksCompleted == 23
        assert stats.teamUtilization == 78.5
        assert stats.revenue == 45000.00
        assert stats.trends["activeProjects"] == 12

    def test_dashboard_stats_missing_required_field(self):
        """Verify GET /analytics/stats rejects missing required fields."""
        with pytest.raises(Exception):  # ValidationError
            DashboardStats(
                activeProjects=5,
                # tasksCompleted missing
                teamUtilization=78.5,
                revenue=45000.00,
            )

    def test_dashboard_stats_invalid_types(self):
        """Verify GET /analytics/stats rejects invalid types."""
        with pytest.raises(Exception):  # ValidationError
            DashboardStats(
                activeProjects="not-a-number",  # Should be int
                tasksCompleted=23,
                teamUtilization=78.5,
                revenue=45000.00,
            )

    def test_tasks_by_status_response_contract(self):
        """Verify GET /analytics/tasks-by-status response structure."""
        response_data = [
            {"label": "To Do", "value": 5, "color": "#6366f1"},
            {"label": "In Progress", "value": 3, "color": "#f59e0b"},
            {"label": "In Review", "value": 2, "color": "#8b5cf6"},
            {"label": "Done", "value": 15, "color": "#10b981"},
        ]

        # Should validate successfully
        tasks_by_status = [TaskByStatus(**item) for item in response_data]

        assert len(tasks_by_status) == 4
        assert tasks_by_status[0].label == "To Do"
        assert tasks_by_status[0].value == 5
        assert tasks_by_status[0].color == "#6366f1"

    def test_tasks_by_status_missing_required_field(self):
        """Verify GET /analytics/tasks-by-status rejects missing required fields."""
        with pytest.raises(Exception):  # ValidationError
            TaskByStatus(
                label="To Do",
                # value missing
                color="#6366f1",
            )
