"""Add time entries table for tracking work hours.

Revision ID: 006_add_time_entries
Revises: 005_add_archived_status
Create Date: 2026-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "006_add_time_entries"
down_revision: Union[str, None] = "005_add_archived_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create time_entries table."""

    # Create time_entries table
    op.execute("""
        CREATE TABLE time_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            agency_id UUID NOT NULL REFERENCES agencies(id) ON DELETE CASCADE,
            duration_minutes INTEGER NOT NULL,
            note VARCHAR(1000),
            entry_date DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            CONSTRAINT check_duration_positive CHECK (duration_minutes > 0)
        )
    """)

    # Create indexes for performance
    op.execute("CREATE INDEX ix_time_entries_task_id ON time_entries(task_id)")
    op.execute("CREATE INDEX ix_time_entries_user_id ON time_entries(user_id)")
    op.execute("CREATE INDEX ix_time_entries_agency_id ON time_entries(agency_id)")
    op.execute("CREATE INDEX ix_time_entries_entry_date ON time_entries(entry_date)")
    op.execute("CREATE INDEX ix_time_entries_duration ON time_entries(duration_minutes)")


def downgrade() -> None:
    """Drop time_entries table."""

    # Drop indexes
    op.execute("DROP INDEX IF EXISTS ix_time_entries_duration")
    op.execute("DROP INDEX IF EXISTS ix_time_entries_entry_date")
    op.execute("DROP INDEX IF EXISTS ix_time_entries_agency_id")
    op.execute("DROP INDEX IF EXISTS ix_time_entries_user_id")
    op.execute("DROP INDEX IF EXISTS ix_time_entries_task_id")

    # Drop table
    op.execute("DROP TABLE time_entries")
