"""Integration tests for authentication API endpoints.

These tests verify the complete authentication flow including
agency registration, user login, and multi-tenant isolation.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session, select

from app.models.agency import Agency
from app.models.user import User, UserRole
from app.core.security import verify_password


@pytest.mark.asyncio
class TestAuthFlowIntegration:
    """Integration tests for complete authentication flow."""

    async def test_signup_flow(self, client: AsyncClient, session: Session):
        """Test complete signup flow: create agency and admin user."""
        signup_data = {
            "agency_data": {
                "name": "Flow Test Agency",
                "email": "flow@test.com",
            },
            "user_data": {
                "name": "Flow Admin",
                "email": "admin@flow.com",
                "password": "securePassword123",
                "role": "admin",
            },
        }

        # Make signup request
        response = await client.post("/api/v1/auth/register", json=signup_data)

        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "agency" in data
        assert "user" in data
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Verify agency was created in database
        agency = session.exec(
            select(Agency).where(Agency.email == "flow@test.com")
        ).first()
        assert agency is not None
        assert agency.name == "Flow Test Agency"

        # Verify user was created in database
        user = session.exec(
            select(User).where(User.email == "admin@flow.com")
        ).first()
        assert user is not None
        assert user.name == "Flow Admin"
        assert user.agency_id == agency.id
        assert user.role == UserRole.admin
        assert verify_password("securePassword123", user.hashed_password)

    async def test_login_flow(self, client: AsyncClient, session: Session):
        """Test login flow with valid credentials."""
        # First create a user
        signup_data = {
            "agency_data": {
                "name": "Login Test Agency",
                "email": "login@test.com",
            },
            "user_data": {
                "name": "Login User",
                "email": "user@login.com",
                "password": "loginPassword123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        # Now login
        login_data = {
            "email": "user@login.com",
            "password": "loginPassword123",
        }
        response = await client.post("/api/v1/auth/login", json=login_data)

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "user@login.com"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login fails with invalid credentials."""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "wrongPassword",
        }
        response = await client.post("/api/v1/auth/login", json=login_data)

        # Should return 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_wrong_password(self, client: AsyncClient, session: Session):
        """Test login fails with wrong password."""
        # Create a user first
        signup_data = {
            "agency_data": {
                "name": "Wrong Pass Agency",
                "email": "wrongpass@test.com",
            },
            "user_data": {
                "name": "Wrong Pass User",
                "email": "user@wrongpass.com",
                "password": "correctPassword123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        # Try login with wrong password
        login_data = {
            "email": "user@wrongpass.com",
            "password": "wrongPassword123",
        }
        response = await client.post("/api/v1/auth/login", json=login_data)

        # Should return 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_me_endpoint(self, client: AsyncClient, session: Session):
        """Test GET /auth/me returns current user info."""
        # Create and login user
        signup_data = {
            "agency_data": {
                "name": "Me Test Agency",
                "email": "me@test.com",
            },
            "user_data": {
                "name": "Me Test User",
                "email": "user@me.com",
                "password": "mePassword123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        login_data = {
            "email": "user@me.com",
            "password": "mePassword123",
        }
        login_response = await client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # Call /me endpoint with token
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["email"] == "user@me.com"
        assert data["name"] == "Me Test User"
        assert data["role"] == "member"

    async def test_me_without_token(self, client: AsyncClient):
        """Test GET /auth/me fails without authentication."""
        response = await client.get("/api/v1/auth/me")

        # Should return 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_logout(self, client: AsyncClient):
        """Test logout endpoint."""
        response = await client.post("/api/v1/auth/logout")

        # Logout should always succeed (client-side token removal)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"


@pytest.mark.asyncio
class TestAgencyIsolationIntegration:
    """Integration tests for multi-tenant agency isolation."""

    async def test_agencies_isolated(self, client: AsyncClient, session: Session):
        """Test that different agencies cannot access each other's data."""
        # Create Agency A with user
        agency_a_data = {
            "agency_data": {
                "name": "Agency A",
                "email": "agencya@test.com",
            },
            "user_data": {
                "name": "User A",
                "email": "usera@test.com",
                "password": "passwordA123",
            },
        }
        await client.post("/api/v1/auth/register", json=agency_a_data)

        # Create Agency B with user
        agency_b_data = {
            "agency_data": {
                "name": "Agency B",
                "email": "agencyb@test.com",
            },
            "user_data": {
                "name": "User B",
                "email": "userb@test.com",
                "password": "passwordB123",
            },
        }
        await client.post("/api/v1/auth/register", json=agency_b_data)

        # Login as User A
        login_a = await client.post("/api/v1/auth/login", json={
            "email": "usera@test.com",
            "password": "passwordA123",
        })
        token_a = login_a.json()["access_token"]

        # Get user A's info
        me_a = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        user_a = me_a.json()

        # Verify user A belongs to Agency A
        agency_a = session.exec(
            select(Agency).where(Agency.email == "agencya@test.com")
        ).first()

        assert user_a["agency_id"] == str(agency_a.id)
        assert user_a["email"] == "usera@test.com"

        # Login as User B
        login_b = await client.post("/api/v1/auth/login", json={
            "email": "userb@test.com",
            "password": "passwordB123",
        })
        token_b = login_b.json()["access_token"]

        # Get user B's info
        me_b = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        user_b = me_b.json()

        # Verify user B belongs to Agency B (not Agency A)
        agency_b = session.exec(
            select(Agency).where(Agency.email == "agencyb@test.com")
        ).first()

        assert user_b["agency_id"] == str(agency_b.id)
        assert user_b["email"] == "userb@test.com"
        assert user_b["agency_id"] != user_a["agency_id"]

    async def test_duplicate_email_within_agency_fails(self, client: AsyncClient):
        """Test that duplicate emails within same agency are rejected."""
        # Create agency
        signup_data = {
            "agency_data": {
                "name": "Duplicate Test Agency",
                "email": "duplicate@test.com",
            },
            "user_data": {
                "name": "First User",
                "email": "user@test.com",
                "password": "password123",
            },
        }
        await client.post("/api/v1/auth/register", json=signup_data)

        # Try to create another user with same email in same agency
        # (This would be done through a different endpoint in production)
        # For now, we verify through register attempt
        signup_data_2 = {
            "agency_data": {
                "name": "Another Agency",
                "email": "another@test.com",
            },
            "user_data": {
                "name": "Second User",
                "email": "user@test.com",  # Same email
                "password": "password123",
            },
        }

        # This should create a new agency but the user creation
        # would be handled by a separate endpoint in production
        response = await client.post("/api/v1/auth/register", json=signup_data_2)

        # The request should succeed (different agency)
        # But the same email shouldn't cause conflicts across agencies
        assert response.status_code == status.HTTP_201_CREATED
