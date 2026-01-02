"""Integration tests for time entries API endpoints.

These tests verify the complete time logging flow including
CRUD operations and multi-tenant isolation (User Story 5).
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session
from datetime import date

from app.models.task import Task
from app.models.user import User


@pytest.mark.asyncio
class TestTimeEntriesIntegration:
    """Integration tests for time entry CRUD operations."""

    async def test_create_time_entry(self, client: AsyncClient, session: Session):
        """Test creating a new time entry."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Time Entry Agency",
                "email": "timeentry@test.com",
            },
            "user_data": {
                "name": "Time User",
                "email": "timeuser@timeentry.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "timeuser@timeentry.com",
            "password": "password123",
        })
        token = login_response.json()["access_token"]

        # Create a task first
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task for time tracking"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = task_response.json()["id"]

        # Create time entry
        time_entry_data = {
            "task_id": str(task_id),
            "duration_minutes": 120,
            "note": "Worked on feature",
            "entry_date": "2026-01-02",
        }
        response = await client.post(
            "/api/v1/time-entries",
            json=time_entry_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["task_id"] == str(task_id)
        assert data["duration_minutes"] == 120
        assert data["note"] == "Worked on feature"
        assert data["entry_date"] == "2026-01-02"
        assert "id" in data

    async def test_create_time_entry_minimal(self, client: AsyncClient, session: Session):
        """Test creating time entry with minimal fields."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Minimal Time Agency",
                "email": "minimaltime@test.com",
            },
            "user_data": {
                "name": "Minimal Time User",
                "email": "timeuser@minimaltime.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "timeuser@minimaltime.com",
            "password": "password123",
        })
        token = login_response.json()["access_token"]

        # Create a task
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Minimal Task"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = task_response.json()["id"]

        # Create time entry with only required fields
        time_entry_data = {
            "task_id": str(task_id),
            "duration_minutes": 60,
        }
        response = await client.post(
            "/api/v1/time-entries",
            json=time_entry_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["duration_minutes"] == 60
        # entry_date should default to today

    async def test_list_time_entries(self, client: AsyncClient, session: Session):
        """Test listing time entries."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "List Time Agency",
                "email": "listtime@test.com",
            },
            "user_data": {
                "name": "List Time User",
                "email": "timeuser@listtime.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "timeuser@listtime.com",
            "password": "password123",
        })
        token = login_response.json()["access_token"]

        # Create task and time entries
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task with time entries"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = task_response.json()["id"]

        for i in range(3):
            await client.post(
                "/api/v1/time-entries",
                json={
                    "task_id": str(task_id),
                    "duration_minutes": 30 * (i + 1),
                },
                headers={"Authorization": f"Bearer {token}"}
            )

        # List time entries
        response = await client.get(
            "/api/v1/time-entries",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "time_entries" in data
        assert len(data["time_entries"]) == 3

    async def test_list_time_entries_filter_by_task(self, client: AsyncClient, session: Session):
        """Test filtering time entries by task."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Filter Time Agency",
                "email": "filtertime@test.com",
            },
            "user_data": {
                "name": "Filter Time User",
                "email": "timeuser@filtertime.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "timeuser@filtertime.com",
            "password": "password123",
        })
        token = login_response.json()["access_token"]

        # Create two tasks
        task1_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task 1"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task1_id = task1_response.json()["id"]

        task2_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task 2"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task2_id = task2_response.json()["id"]

        # Create time entries for both tasks
        await client.post(
            "/api/v1/time-entries",
            json={"task_id": str(task1_id), "duration_minutes": 60},
            headers={"Authorization": f"Bearer {token}"}
        )
        await client.post(
            "/api/v1/time-entries",
            json={"task_id": str(task2_id), "duration_minutes": 30},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Filter by task
        response = await client.get(
            f"/api/v1/time-entries?task_id={task1_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["time_entries"]) == 1
        assert data["time_entries"][0]["task_id"] == str(task1_id)

    async def test_list_time_entries_filter_by_date(self, client: AsyncClient, session: Session):
        """Test filtering time entries by date range."""
        # Create user and login
        signup_data = {
            "agency_data": {
                "name": "Date Filter Agency",
                "email": "datefilter@test.com",
            },
            "user_data": {
                "name": "Date Filter User",
                "email": "dateuser@datefilter.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_response = await client.post("/api/v1/auth/login", json={
            "email": "dateuser@datefilter.com",
            "password": "password123",
        })
        token = login_response.json()["access_token"]

        # Create task
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Task for date filter"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_id = task_response.json()["id"]

        # Create time entries with different dates
        await client.post(
            "/api/v1/time-entries",
            json={
                "task_id": str(task_id),
                "duration_minutes": 60,
                "entry_date": "2026-01-01",
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        await client.post(
            "/api/v1/time-entries",
            json={
                "task_id": str(task_id),
                "duration_minutes": 30,
                "entry_date": "2026-01-02",
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        # Filter by date
        response = await client.get(
            "/api/v1/time-entries?start_date=2026-01-02&end_date=2026-01-02",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert len(data["time_entries"]) == 1
        assert data["time_entries"][0]["entry_date"] == "2026-01-02"

    async def test_time_entry_cross_agency_isolation(self, client: AsyncClient, session: Session):
        """Test time entries are isolated between agencies."""
        # Create first agency
        signup_data1 = {
            "agency_data": {
                "name": "Time Agency A",
                "email": "timeagencysa@test.com",
            },
            "user_data": {
                "name": "User A",
                "email": "usera@timeagencysa.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data1)

        login_response1 = await client.post("/api/v1/auth/login", json={
            "email": "usera@timeagencysa.com",
            "password": "password123",
        })
        token_a = login_response1.json()["access_token"]

        # Create task in Agency A
        task_response = await client.post(
            "/api/v1/tasks",
            json={"title": "Agency A Task"},
            headers={"Authorization": f"Bearer {token_a}"}
        )
        task_id = task_response.json()["id"]

        # Create time entry for Agency A task
        await client.post(
            "/api/v1/time-entries",
            json={
                "task_id": str(task_id),
                "duration_minutes": 60,
            },
            headers={"Authorization": f"Bearer {token_a}"}
        )

        # Create second agency
        signup_data2 = {
            "agency_data": {
                "name": "Time Agency B",
                "email": "timeagencysb@test.com",
            },
            "user_data": {
                "name": "User B",
                "email": "userb@timeagencysb.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data2)

        login_response2 = await client.post("/api/v1/auth/login", json={
            "email": "userb@timeagencysb.com",
            "password": "password123",
        })
        token_b = login_response2.json()["access_token"]

        # Try to list time entries for Agency A task from Agency B
        response = await client.get(
            "/api/v1/time-entries",
            headers={"Authorization": f"Bearer {token_b}"}
        )

        # Should return empty list or only Agency B's entries
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Agency B should not see Agency A's time entries
        for entry in data.get("time_entries", []):
            assert entry["task_id"] != str(task_id)
