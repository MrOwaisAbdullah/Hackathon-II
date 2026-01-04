"""Add user management fields for Phase 2: team management.

Adds:
- active: bool (default=True) for soft delete
- is_project_manager: bool (default=False) for project permissions
- password_expires_at: timestamp (nullable) for temporary password expiration
- must_change_password: bool (default=False) to force password change on login

Revision ID: 007_add_user_management_fields
Revises: 006_add_time_entries
Create Date: 2026-01-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "007_add_user_management_fields"
down_revision: Union[str, None] = "006_add_time_entries"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user management fields to users table."""

    # Add active column for soft delete (with default True)
    op.execute("""
        ALTER TABLE users
        ADD COLUMN active BOOLEAN NOT NULL DEFAULT TRUE
    """)

    # Add index on active for filtering queries
    op.execute("CREATE INDEX ix_users_active ON users(active)")

    # Add is_project_manager column for PM permissions
    op.execute("""
        ALTER TABLE users
        ADD COLUMN is_project_manager BOOLEAN NOT NULL DEFAULT FALSE
    """)

    # Add password_expires_at column for temporary password expiration
    op.execute("""
        ALTER TABLE users
        ADD COLUMN password_expires_at TIMESTAMP WITH TIME ZONE
    """)

    # Add must_change_password column to force password change on login
    op.execute("""
        ALTER TABLE users
        ADD COLUMN must_change_password BOOLEAN NOT NULL DEFAULT FALSE
    """)


def downgrade() -> None:
    """Remove user management fields from users table."""

    # Drop columns in reverse order
    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS must_change_password
    """)

    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS password_expires_at
    """)

    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS is_project_manager
    """)

    # Drop index on active
    op.execute("DROP INDEX IF EXISTS ix_users_active")

    op.execute("""
        ALTER TABLE users
        DROP COLUMN IF EXISTS active
    """)
