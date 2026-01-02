"""Integration tests for analytics API endpoints.

These tests verify the analytics and statistics calculations
for the dashboard (User Story 4).
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session

from app.models.task import Task
from app.models.project import Project


@pytest.mark.asyncio
class TestDashboardStatsIntegration:
    """Integration tests for dashboard statistics endpoint."""

    async def test_get_dashboard_stats_empty(self, client: AsyncClient, session: Session):
        """Test getting dashboard stats when no data exists."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Stats Agency",
                "email": "stats@test.com",
            },
            "user_data": {
                "name": "Stats User",
                "email": "user@stats.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "user@stats.com",
            "password": "password123",
        }))
        token = login_response.json()["access_token"]

        # Get stats
        response = await client.get(
            "/api/v1/analytics/stats",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have zero values
        assert data["activeProjects"] == 0
        assert data["tasksCompleted"] == 0
        assert "teamUtilization" in data
        assert "revenue" in data
        assert "trends" in data

    async def test_get_dashboard_stats_with_data(self, client: AsyncClient, session: Session):
        """Test getting dashboard stats with actual data."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Stats Data Agency",
                "email": "statsdata@test.com",
            },
            "user_data": {
                "name": "Stats Data User",
                "email": "user@statsdata.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "user@statsdata.com",
            "password": "password123",
        }))
        token = login_response.json()["access_token"]

        # Create some projects
        for i in range(3):
            await client.post(
                "/api/v1/projects",
                json={"name": f"Project {i}", "description": f"Project {i} description"},
                headers={"Authorization": f"Bearer {token}"}
            )

        # Create tasks with different statuses
        tasks_data = [
            {"title": "Task 1", "status": "TODO"},
            {"title": "Task 2", "status": "DOING"},
            {"title": "Task 3", "status": "DONE"},
            {"title": "Task 4", "status": "DONE"},
        ]
        for task_data in tasks_data:
            await client.post(
                "/api/v1/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Get stats
        response = await client.get(
            "/api/v1/analytics/stats",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should reflect created data
        assert data["activeProjects"] == 3
        assert data["tasksCompleted"] == 2  # DONE tasks
        assert "trends" in data

    async def test_get_tasks_by_status(self, client: AsyncClient, session: Session):
        """Test getting task counts grouped by status."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Tasks By Status Agency",
                "email": "taskstatus@test.com",
            },
            "user_data": {
                "name": "Task Status User",
                "email": "user@taskstatus.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "user@taskstatus.com",
            "password": "password123",
        }))
        token = login_response.json()["access_token"]

        # Create tasks with different statuses
        tasks_data = [
            {"title": "Task 1", "status": "TODO"},
            {"title": "Task 2", "status": "TODO"},
            {"title": "Task 3", "status": "DOING"},
            {"title": "Task 4", "status": "DONE"},
        ]
        for task_data in tasks_data:
            await client.post(
                "/api/v1/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token}"}
            )

        # Get tasks by status
        response = await client.get(
            "/api/v1/analytics/tasks-by-status",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should be an array with status counts
        assert isinstance(data, list)
        assert len(data) == 4  # TODO, DOING, REVIEW, DONE

        # Check TODO count
        todo_item = next((item for item in data if item["label"] == "TODO"), None)
        assert todo_item is not None
        assert todo_item["value"] == 2

        # Check DONE count
        done_item = next((item for item in data if item["label"] == "DONE"), None)
        assert done_item is not None
        assert done_item["value"] == 1

    async def test_get_dashboard_stats_unauthorized(self, client: AsyncClient):
        """Test getting stats without authentication returns 401."""
        response = await client.get("/api/v1/analytics/stats")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_tasks_by_status_unauthorized(self, client: AsyncClient):
        """Test getting tasks by status without authentication returns 401."""
        response = await client.get("/api/v1/analytics/tasks-by-status")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_dashboard_stats_multi_tenant_isolation(self, client: AsyncClient, session: Session):
        """Test that dashboard stats are isolated per agency."""
        # Create first agency
        signup_data1 = {
            "agency_data": {
                "name": "Agency A",
                "email": "agencysa@test.com",
            },
            "user_data": {
                "name": "User A",
                "email": "usera@agencysa.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data1)

        login_response1 = await client.post("/api/v1/auth/login", json={
            "email": "usera@agencysa.com",
            "password": "password123",
        }))
        token_a = login_response1.json()["access_token"]

        # Create tasks in Agency A
        await client.post(
            "/api/v1/tasks",
            json={"title": "Agency A Task 1", "status": "DONE"},
            headers={"Authorization": f"Bearer {token_a}"}
        )
        await client.post(
            "/api/v1/tasks",
            json={"title": "Agency A Task 2", "status": "TODO"},
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Create second agency
        signup_data2 = {
            "agency_data": {
                "name": "Agency B",
                "email": "agencysb@test.com",
            },
            "user_data": {
                "name": "User B",
                "email": "userb@agencysb.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data2)

        login_response2 = await client.post("/api/v1/auth/login", json={
            "email": "userb@agencysb.com",
            "password": "password123",
        }))
        token_b = login_response2.json()["access_token"]

        # Create tasks in Agency B
        await client.post(
            "/api/v1/tasks",
            json={"title": "Agency B Task 1", "status": "DONE"},
            headers={"Authorization": f"Bearer {token_b}"}
        )

        # Get stats for Agency A
        response_a = await client.get(
            "/api/v1/analytics/stats",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        stats_a = response_a.json()

        # Get stats for Agency B
        response_b = await client.get(
            "/api/v1/analytics/stats",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        stats_b = response_b.json()

        # Stats should be different (isolated)
        assert stats_a["tasksCompleted"] == 1  # Agency A has 1 DONE task
        assert stats_b["tasksCompleted"] == 1  # Agency B has 1 DONE task
        # Both should see their own data only


@pytest.mark.asyncio
class TestProjectProfitabilityIntegration:
    """Integration tests for project profitability endpoint (US5 T121)."""

    async def test_get_project_profitability_empty(self, client: AsyncClient, session: Session):
        """Test getting profitability when no data exists."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Profit Agency",
                "email": "profit@test.com",
            },
            "user_data": {
                "name": "Profit User",
                "email": "user@profit.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "user@profit.com",
            "password": "password123",
        }))
        token = login_response.json()["access_token"]

        # Get profitability
        response = await client.get(
            "/api/v1/analytics/profitability",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should be an empty array or array with zero-value projects
        assert isinstance(data, list)

    async def test_get_project_profitability_with_time_entries(self, client: AsyncClient, session: Session):
        """Test getting profitability with actual time entries."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Profit Data Agency",
                "email": "profitdata@test.com",
            },
            "user_data": {
                "name": "Profit Data User",
                "email": "user@profitdata.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "user@profitdata.com",
            "password": "password123",
        }))
        token = login_response.json()["access_token"]

        # Create project with hourly rate
        project_response = await client.post(
            "/api/v1/projects",
            json={"name": "Billable Project", "description": "Project with hourly rate"},
            headers={"Authorization": f"Bearer {token}"}
        )
        project_id = project_response.json()["id"]

        # Create tasks
        task1_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task 1", "project_id": project_id, "status": "DONE"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task1_id = task1_response.json()["id"]

        task2_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task 2", "project_id": project_id, "status": "DONE"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Log time entries
        await client.post(
            "/api/v1/time-entries",
            json={
                "task_id": task1_id,
                "duration_minutes": 120,  # 2 hours
                "note": "Initial implementation"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        await client.post(
            "/api/v1/time-entries",
            json={
                "task_id": task1_id,
                "duration_minutes": 60,  # 1 hour
                "note": "Code review"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        # Get profitability
        response = await client.get(
            "/api/v1/analytics/profitability",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should have profitability data
        assert isinstance(data, list)
        assert len(data) > 0

        # Check project profitability structure
        project_profit = data[0]
        assert "project_id" in project_profit
        assert "project_name" in project_profit
        assert "total_tasks" in project_profit
        assert "completed_tasks" in project_profit
        assert "completion_percentage" in project_profit
        assert "total_hours" in project_profit
        assert "total_cost" in project_profit
        assert "total_revenue" in project_profit
        assert "profit" in project_profit
        assert "profit_margin" in project_profit

        # Verify values
        assert project_profit["total_tasks"] == 2
        assert project_profit["completed_tasks"] == 2
        assert project_profit["completion_percentage"] == 100.0
        assert project_profit["total_hours"] == 3.0  # 180 minutes / 60

    async def test_get_project_profitability_unauthorized(self, client: AsyncClient):
        """Test getting profitability without authentication returns 401."""
        response = await client.get("/api/v1/analytics/profitability")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_project_profitability_multi_tenant_isolation(self, client: AsyncClient, session: Session):
        """Test that profitability data is isolated per agency."""
        # Create first agency with project
        signup_data1 = {
            "agency_data": {
                "name": "Profit Agency A",
                "email": "profita@test.com",
            },
            "user_data": {
                "name": "Profit User A",
                "email": "usera@profita.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data1)

        login_response1 = await client.post("/api/v1/auth/login", json={
            "email": "usera@profita.com",
            "password": "password123",
        }))
        token_a = login_response1.json()["access_token"]

        # Create project and task in Agency A
        project_response_a = await client.post(
            "/api/v1/projects",
            json={"name": "Agency A Project"},
            headers={"Authorization": f"Bearer {token_a}"}
        )
        project_a_id = project_response_a.json()["id"]

        await client.post(
            "/api/v1/tasks",
            json={"title": "Agency A Task", "project_id": project_a_id, "status": "DONE"},
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Create second agency
        signup_data2 = {
            "agency_data": {
                "name": "Profit Agency B",
                "email": "profitb@test.com",
            },
            "user_data": {
                "name": "Profit User B",
                "email": "userb@profitb.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data2)

        login_response2 = await client.post("/api/v1/auth/login", json={
            "email": "userb@profitb.com",
            "password": "password123",
        }))
        token_b = login_response2.json()["access_token"]

        # Create project in Agency B
        await client.post(
            "/api/v1/projects",
            json={"name": "Agency B Project"},
            headers={"Authorization": f"Bearer {token_b}"}
        )

        # Get profitability for Agency A
        response_a = await client.get(
            "/api/v1/analytics/profitability",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        profit_a = response_a.json()

        # Get profitability for Agency B
        response_b = await client.get(
            "/api/v1/analytics/profitability",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        profit_b = response_b.json()

        # Should only see their own projects
        assert len(profit_a) == 1
        assert len(profit_b) == 1
        assert profit_a[0]["project_name"] == "Agency A Project"
        assert profit_b[0]["project_name"] == "Agency B Project"
