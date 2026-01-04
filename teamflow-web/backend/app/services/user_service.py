"""User service for user operations."""
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
import secrets
import string

from fastapi import HTTPException, status
from sqlmodel import Session, select, col
from passlib.context import CryptContext

from app.models.user import User, UserCreate, UserUpdate, UserRead, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user operations."""

    def list_users(self, agency_id: UUID, session: Session) -> List[User]:
        """List all users in an agency."""
        return session.exec(
            select(User)
            .where(User.agency_id == agency_id)
            .where(User.active == True)  # Only return active users
            .order_by(User.name)
        ).all()

    def get_user(self, user_id: str, agency_id: UUID, session: Session) -> User | None:
        """Get a user by ID (scoped to agency)."""
        return session.exec(
            select(User).where(
                User.id == user_id,
                User.agency_id == agency_id,
            )
        ).first()

    def create_user(
        self,
        user_data: UserCreate,
        agency_id: UUID,
        session: Session,
        requesting_user: User,
    ) -> tuple[User, str]:
        """Create a new user with auto-generated temporary password.

        Args:
            user_data: User creation data (name, email, role, is_project_manager)
            agency_id: Agency ID
            session: Database session
            requesting_user: User performing the action (for permission checks)

        Returns:
            Tuple of (created user, temporary_password)

        Raises:
            HTTPException: If permission denied, email exists, or last admin check fails
        """
        # Permission check: only admins can create users
        if requesting_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can create users",
            )

        # Check if email already exists in agency
        existing = session.exec(
            select(User).where(
                User.email == user_data.email,
                User.agency_id == agency_id,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists in this agency",
            )

        # Generate temporary password (12 chars, mixed case + numbers)
        temp_password = self._generate_temp_password()

        # Create user with password_expires_at = 24 hours from now
        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=pwd_context.hash(temp_password),
            role=user_data.role,
            agency_id=agency_id,
            is_project_manager=user_data.is_project_manager or False,
            password_expires_at=datetime.utcnow() + timedelta(hours=24),
            must_change_password=True,
            active=True,
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user, temp_password

    def update_user(
        self,
        user_id: str,
        user_data: UserUpdate,
        agency_id: UUID,
        session: Session,
        requesting_user: User,
    ) -> User:
        """Update an existing user.

        Args:
            user_id: ID of user to update
            user_data: User update data
            agency_id: Agency ID
            session: Database session
            requesting_user: User performing the action (for permission checks)

        Returns:
            Updated user

        Raises:
            HTTPException: If permission denied or last admin check fails
        """
        # Permission check: only admins can update users
        if requesting_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can update users",
            )

        user = self.get_user(user_id, agency_id, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Check if email change and new email already exists
        if user_data.email and user_data.email != user.email:
            existing = session.exec(
                select(User).where(
                    User.email == user_data.email,
                    User.agency_id == agency_id,
                    User.id != user_id,
                )
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists in this agency",
                )

        # Update fields (only allow updating name, email, role, is_project_manager)
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.role is not None:
            # Last admin check: prevent removing admin role from last admin
            if user.role == UserRole.admin and user_data.role != UserRole.admin:
                admin_count = session.exec(
                    select(User).where(
                        User.agency_id == agency_id,
                        User.role == UserRole.admin,
                        User.active == True,
                    )
                ).all()
                if len(admin_count) <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot remove admin role from the last admin",
                    )
            user.role = user_data.role
        if user_data.is_project_manager is not None:
            # Only admins can set is_project_manager (no check needed here, already enforced above)
            user.is_project_manager = user_data.is_project_manager

        user.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(user)

        return user

    def delete_user(
        self,
        user_id: str,
        agency_id: UUID,
        session: Session,
        requesting_user: User,
    ) -> None:
        """Soft delete a user (set active=False).

        Args:
            user_id: ID of user to delete
            agency_id: Agency ID
            session: Database session
            requesting_user: User performing the action

        Raises:
            HTTPException: If permission denied or last admin check fails
        """
        # Permission check: only admins can delete users
        if requesting_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete users",
            )

        user = self.get_user(user_id, agency_id, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Prevent self-deletion
        if user.id == requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself",
            )

        # Last admin check
        if user.role == UserRole.admin:
            admin_count = session.exec(
                select(User).where(
                    User.agency_id == agency_id,
                    User.role == UserRole.admin,
                    User.active == True,
                )
            ).all()
            if len(admin_count) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last admin",
                )

        # Soft delete
        user.active = False
        user.updated_at = datetime.utcnow()
        session.commit()

    def _generate_temp_password(self, length: int = 12) -> str:
        """Generate a secure temporary password.

        Args:
            length: Password length (default 12)

        Returns:
            Generated password with uppercase, lowercase, digits, and special chars
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

