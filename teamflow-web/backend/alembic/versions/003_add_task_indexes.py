"""Add composite index on tasks table for agency and status queries.

Revision ID: 003_add_task_indexes
Revises: 002_add_tasks_projects
Create Date: 2025-01-29 15:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_task_indexes"
down_revision: Union[str, None] = "002_add_tasks_projects"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create composite index on (agency_id, status) for task queries."""
    # Composite index for efficient agency-scoped status queries
    op.create_index(
        "ix_tasks_agency_id_status",
        "tasks",
        ["agency_id", "status"],
    )


def downgrade() -> None:
    """Drop composite index on tasks table."""
    op.drop_index("ix_tasks_agency_id_status", table_name="tasks")
