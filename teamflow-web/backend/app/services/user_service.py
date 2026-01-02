"""User service for user operations."""
from typing import List
from uuid import UUID

from sqlmodel import Session, select, col

from app.models.user import User


class UserService:
    """Service for user operations."""

    def list_users(self, agency_id: UUID, session: Session) -> List[User]:
        """List all users in an agency."""
        return session.exec(
            select(User)
            .where(User.agency_id == agency_id)
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
