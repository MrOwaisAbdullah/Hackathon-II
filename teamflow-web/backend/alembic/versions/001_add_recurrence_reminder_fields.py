"""
T037: Alembic migration - Add recurrence and reminder fields to tasks table

This migration adds:
- recurrence_rule: JSONB field for recurrence pattern
- reminder_settings: JSONB field for reminder configuration
- next_instance_id: UUID foreign key to next task instance
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "001_add_recurrence_reminder_fields"
down_revision = None  # First migration
branch_labels = None
depends_on = None


def upgrade():
    """Add recurrence and reminder fields to the tasks table"""

    # Check if tasks table exists, if not create it
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'todo',
            priority VARCHAR(50) DEFAULT 'medium',
            due_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            project_id UUID,
            assigned_to_id UUID,
            created_by_id UUID
        );
        """
    )

    # Add recurrence_rule column (JSONB for flexible recurrence patterns)
    op.add_column(
        "tasks",
        sa.Column(
            "recurrence_rule",
            postgresql.JSONB,
            nullable=True,
            comment="Recurrence pattern: frequency, interval, days_of_week, end_date, etc.",
        ),
    )

    # Add reminder_settings column (JSONB for reminder configuration)
    op.add_column(
        "tasks",
        sa.Column(
            "reminder_settings",
            postgresql.JSONB,
            nullable=True,
            comment="Reminder settings: offsets, channels, custom_message",
        ),
    )

    # Add next_instance_id column (UUID foreign key to next occurrence)
    op.add_column(
        "tasks",
        sa.Column(
            "next_instance_id",
            postgresql.UUID,
            nullable=True,
            sa.ForeignKey("tasks.id", ondelete="SET NULL"),
            comment="Link to the next instance of this recurring task",
        ),
    )

    # Create index on recurrence_rule for faster queries
    op.create_index(
        "ix_tasks_recurrence_rule",
        "tasks",
        ["recurrence_rule"],
        postgresql_using="gin",
    )


def downgrade():
    """Remove recurrence and reminder fields from the tasks table"""

    # Drop the index first
    try:
        op.drop_index("ix_tasks_recurrence_rule", table_name="tasks")
    except Exception:
        pass  # Index may not exist

    # Drop columns
    op.drop_column("tasks", "next_instance_id")
    op.drop_column("tasks", "reminder_settings")
    op.drop_column("tasks", "recurrence_rule")
