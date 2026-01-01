"""Contract tests for authentication endpoints.

These tests verify that the API responses match the OpenAPI specification
for authentication-related endpoints.
"""
import pytest
from pydantic import ValidationError

from app.models.agency import AgencyCreate, AgencyRead
from app.models.user import UserCreate, UserLogin, UserRead


class TestRegisterContract:
    """Contract tests for POST /auth/register endpoint."""

    def test_register_request_contract(self):
        """Verify register request matches AgencyCreate + UserCreate schema."""
        # Valid request data should match schema
        agency_data = {
            "name": "Test Agency",
            "email": "test@agency.com",
        }
        user_data = {
            "name": "Admin User",
            "email": "admin@test.com",
            "password": "password123",
            "role": "admin",
        }

        # Should validate successfully
        agency = AgencyCreate(**agency_data)
        user = UserCreate(**user_data)

        assert agency.name == "Test Agency"
        assert agency.email == "test@agency.com"
        assert user.name == "Admin User"
        assert user.email == "admin@test.com"
        assert user.role.value == "admin"

    def test_register_request_invalid_email(self):
        """Verify register rejects invalid email."""
        with pytest.raises(ValidationError):
            AgencyCreate(
                name="Test Agency",
                email="not-an-email",
            )

    def test_register_request_weak_password(self):
        """Verify register rejects weak passwords."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="Admin",
                email="admin@test.com",
                password="short",  # Too short
            )

    def test_register_response_contract(self):
        """Verify register response structure."""
        response_data = {
            "agency": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Test Agency",
                "email": "test@agency.com",
                "created_at": "2025-01-29T12:00:00",
                "updated_at": None,
            },
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Admin User",
                "email": "admin@test.com",
                "role": "admin",
                "agency_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2025-01-29T12:00:00",
                "updated_at": None,
            },
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
        }

        # Should validate successfully
        agency = AgencyRead(**response_data["agency"])
        user = UserRead(**response_data["user"])

        assert str(agency.id) == "123e4567-e89b-12d3-a456-426614174000"
        assert str(user.id) == "123e4567-e89b-12d3-a456-426614174001"
        assert response_data["token_type"] == "bearer"
        assert isinstance(response_data["access_token"], str)


class TestLoginContract:
    """Contract tests for POST /auth/login endpoint."""

    def test_login_request_contract(self):
        """Verify login request matches UserLogin schema."""
        login_data = {
            "email": "admin@test.com",
            "password": "password123",
        }

        # Should validate successfully
        login = UserLogin(**login_data)

        assert login.email == "admin@test.com"
        assert login.password == "password123"

    def test_login_response_contract(self):
        """Verify login response structure."""
        response_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Admin User",
                "email": "admin@test.com",
                "role": "admin",
                "agency_id": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2025-01-29T12:00:00",
                "updated_at": None,
            },
        }

        # Should validate successfully
        user = UserRead(**response_data["user"])

        assert response_data["token_type"] == "bearer"
        assert isinstance(response_data["access_token"], str)
        assert user.email == "admin@test.com"


class TestMeContract:
    """Contract tests for GET /auth/me endpoint."""

    def test_me_response_contract(self):
        """Verify /me response matches UserRead schema."""
        response_data = {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "name": "Admin User",
            "email": "admin@test.com",
            "role": "admin",
            "agency_id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2025-01-29T12:00:00",
            "updated_at": None,
        }

        # Should validate successfully
        user = UserRead(**response_data)

        assert str(user.id) == "123e4567-e89b-12d3-a456-426614174001"
        assert user.name == "Admin User"
        assert user.email == "admin@test.com"
        assert user.role.value == "admin"
        assert str(user.agency_id) == "123e4567-e89b-12d3-a456-426614174000"
