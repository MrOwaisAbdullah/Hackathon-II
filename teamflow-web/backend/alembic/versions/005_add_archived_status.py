"""Add ARCHIVED status to taskstatus enum.

Revision ID: 005_add_archived_status
Revises: 004_fix_task_enum_case
Create Date: 2026-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "005_add_archived_status"
down_revision: Union[str, None] = "004_fix_task_enum_case"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ARCHIVED status to taskstatus enum."""

    # Step 1: Convert column to TEXT
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE TEXT USING status::text")

    # Step 2: Drop old enum type
    op.execute("DROP TYPE taskstatus CASCADE")

    # Step 3: Create new enum type with ARCHIVED value
    op.execute("CREATE TYPE taskstatus AS ENUM ('TODO', 'DOING', 'REVIEW', 'DONE', 'ARCHIVED')")

    # Step 4: Convert column back to enum type
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus USING status::text::taskstatus")


def downgrade() -> None:
    """Remove ARCHIVED status from taskstatus enum."""

    # Convert to TEXT first
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE TEXT USING status::text")

    # Drop enum with ARCHIVED
    op.execute("DROP TYPE taskstatus CASCADE")

    # Recreate without ARCHIVED
    op.execute("CREATE TYPE taskstatus AS ENUM ('TODO', 'DOING', 'REVIEW', 'DONE')")

    # Convert column back to enum type
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus USING status::text::taskstatus")
