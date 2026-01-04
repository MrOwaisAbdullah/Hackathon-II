"""Integration tests for user CRUD API endpoints.

These tests verify the complete user management workflow including
creation with temporary password, updates with permission checks,
soft deletion, and validation rules.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlmodel import Session, select

from app.models.agency import Agency
from app.models.user import User, UserRole
from app.core.security import verify_password


@pytest.mark.asyncio
class TestUserCreationIntegration:
    """Integration tests for user creation with temporary password."""

    async def test_create_user_with_temp_password(
        self, client: AsyncClient, session: Session, admin_token: str
    ):
        """Test user creation generates valid temporary password."""
        # Create agency and admin first
        agency = Agency(name="User CRUD Test", email="usercrud@test.com")
        session.add(agency)
        session.commit()

        # Create user with temp password
        user_data = {
            "name": "New Team Member",
            "email": "newmember@test.com",
            "role": "member",
            "is_project_manager": False,
        }

        response = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Verify response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "id" in data
        assert data["email"] == "newmember@test.com"
        assert data["name"] == "New Team Member"
        assert data["role"] == "member"
        assert "temp_password" in data

        # Verify temp password format (12 chars, includes special char)
        temp_password = data["temp_password"]
        assert len(temp_password) >= 12
        assert any(c in "!@#$%^&*" for c in temp_password)

        # Verify user was created in database
        user = session.exec(
            select(User).where(User.email == "newmember@test.com")
        ).first()
        assert user is not None
        assert user.name == "New Team Member"
        assert user.active is True
        assert user.must_change_password is True
        assert user.password_expires_at is not None

    async def test_create_project_manager(
        self, client: AsyncClient, session: Session, admin_token: str
    ):
        """Test creating a project manager."""
        user_data = {
            "name": "PM User",
            "email": "pm@test.com",
            "role": "member",
            "is_project_manager": True,
        }

        response = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["is_project_manager"] is True

        # Verify in database
        user = session.exec(
            select(User).where(User.email == "pm@test.com")
        ).first()
        assert user is not None
        assert user.is_project_manager is True

    async def test_duplicate_email_rejected(
        self, client: AsyncClient, admin_token: str
    ):
        """Test duplicate email within agency is rejected."""
        user_data = {
            "name": "First User",
            "email": "duplicate@test.com",
            "role": "member",
        }

        # Create first user
        response1 = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create duplicate
        response2 = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
class TestUserUpdateIntegration:
    """Integration tests for user updates with permission checks."""

    async def test_update_user_name_and_email(
        self, client: AsyncClient, session: Session, admin_token: str
    ):
        """Test updating user name and email."""
        # Create a user first
        user_data = {
            "name": "Original Name",
            "email": "update_test@test.com",
            "role": "member",
        }
        create_response = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        user_id = create_response.json()["id"]

        # Update user
        update_data = {
            "name": "Updated Name",
            "email": "updated@test.com",
        }

        response = await client.patch(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["name"] == "Updated Name"
        assert data["email"] == "updated@test.com"

        # Verify in database
        user = session.get(User, user_id)
        assert user is not None
        assert user.name == "Updated Name"
        assert user.email == "updated@test.com"

    async def test_promote_to_project_manager(
        self, client: AsyncClient, session: Session, admin_token: str
    ):
        """Test promoting user to project manager."""
        # Create a regular user
        user_data = {
            "name": "Regular User",
            "email": "regular@test.com",
            "role": "member",
            "is_project_manager": False,
        }
        create_response = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        user_id = create_response.json()["id"]

        # Promote to PM
        update_data = {
            "is_project_manager": True,
        }

        response = await client.patch(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_project_manager"] is True

    async def test_only_admin_can_set_pm_flag(
        self, client: AsyncClient, member_token: str
    ):
        """Test non-admin cannot set project manager flag."""
        # Create a user as member should fail at permission check
        # (This assumes we have a way to get member_token)
        update_data = {
            "name": "Test",
            "is_project_manager": True,
        }

        response = await client.patch(
            f"/api/v1/users/some-id",
            json=update_data,
            headers={"Authorization": f"Bearer {member_token}"}
        )

        # Should fail with 403 Forbidden
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        ]


@pytest.mark.asyncio
class TestUserSoftDeleteIntegration:
    """Integration tests for user soft deletion."""

    async def test_soft_delete_user(
        self, client: AsyncClient, session: Session, admin_token: str
    ):
        """Test user soft deletion sets active=False."""
        # Create a user
        user_data = {
            "name": "To Delete",
            "email": "todelete@test.com",
            "role": "member",
        }
        create_response = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        user_id = create_response.json()["id"]

        # Soft delete
        response = await client.delete(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify user is soft deleted (still in DB but active=False)
        user = session.get(User, user_id)
        assert user is not None
        assert user.active is False

    async def test_cannot_delete_last_admin(
        self, client: AsyncClient, session: Session, admin_token: str
    ):
        """Test cannot delete the last admin in agency."""
        # Get the admin user (there's only one from fixtures)
        admins = session.exec(
            select(User).where(
                User.role == UserRole.admin,
                User.active == True
            )
        ).all()

        # If there's only one admin, try to delete them
        if len(admins) == 1:
            admin_id = str(admins[0].id)

            response = await client.delete(
                f"/api/v1/users/{admin_id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )

            # Should fail
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "last admin" in response.json()["detail"].lower()

    async def test_cannot_delete_self(
        self, client: AsyncClient, admin_token: str
    ):
        """Test users cannot delete themselves."""
        # Get current user ID from token
        # For this test, we need the admin's user_id
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        user_id = response.json()["id"]

        # Try to delete self
        response = await client.delete(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "yourself" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestUserPermissionValidation:
    """Integration tests for user permission validation."""

    async def test_non_admin_cannot_create_users(
        self, client: AsyncClient, member_token: str
    ):
        """Test non-admin cannot create users."""
        user_data = {
            "name": "Should Fail",
            "email": "fail@test.com",
            "role": "member",
        }

        response = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {member_token}"}
        )

        # Should fail with 403 Forbidden
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        ]

    async def test_non_admin_cannot_delete_users(
        self, client: AsyncClient, member_token: str, admin_token: str
    ):
        """Test non-admin cannot delete users."""
        # Create a user as admin
        user_data = {
            "name": "Victim",
            "email": "victim@test.com",
            "role": "member",
        }
        create_response = await client.post(
            f"/api/v1/users",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        user_id = create_response.json()["id"]

        # Try to delete as member
        response = await client.delete(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {member_token}"}
        )

        # Should fail
        assert response.status_code in [
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED,
        ]
