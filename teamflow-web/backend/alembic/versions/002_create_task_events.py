"""
T038: Alembic migration - Create task_events table for event log

This migration creates the task_events table to log all task-related events
for audit purposes and event replay capability.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "002_create_task_events"
down_revision = "001_add_recurrence_reminder_fields"
branch_labels = None
depends_on = None


def upgrade():
    """Create the task_events table for event sourcing"""

    op.create_table(
        "task_events",
        sa.Column("id", postgresql.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "event_id",
            sa.String(255),
            nullable=False,
            comment="CloudEvents event ID",
        ),
        sa.Column(
            "event_type",
            sa.String(255),
            nullable=False,
            comment="Event type: task.created, task.completed, etc.",
        ),
        sa.Column(
            "event_source",
            sa.String(255),
            nullable=False,
            default="teamflow-backend",
            comment="Event source service",
        ),
        sa.Column(
            "task_id",
            postgresql.UUID,
            nullable=False,
            comment="ID of the task this event relates to",
        ),
        sa.Column(
            "project_id",
            postgresql.UUID,
            nullable=True,
            comment="ID of the project",
        ),
        sa.Column(
            "user_id",
            postgresql.UUID,
            nullable=True,
            comment="ID of the user who triggered the event",
        ),
        sa.Column(
            "event_data",
            postgresql.JSONB,
            nullable=True,
            comment="Full event payload",
        ),
        sa.Column(
            "timestamp",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.text("NOW()"),
            comment="When the event occurred",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            default=sa.text("NOW()"),
        ),
    )

    # Create indexes for common queries
    op.create_index("ix_task_events_task_id", "task_events", ["task_id"])
    op.create_index("ix_task_events_event_type", "task_events", ["event_type"])
    op.create_index("ix_task_events_timestamp", "task_events", ["timestamp"])
    op.create_index("ix_task_events_project_id", "task_events", ["project_id"])

    # Create GIN index on event_data for JSON queries
    op.create_index(
        "ix_task_events_event_data",
        "task_events",
        ["event_data"],
        postgresql_using="gin",
    )


def downgrade():
    """Drop the task_events table"""

    # Drop indexes first
    op.drop_index("ix_task_events_event_data", table_name="task_events")
    op.drop_index("ix_task_events_project_id", table_name="task_events")
    op.drop_index("ix_task_events_timestamp", table_name="task_events")
    op.drop_index("ix_task_events_event_type", table_name="task_events")
    op.drop_index("ix_task_events_task_id", table_name="task_events")

    # Drop table
    op.drop_table("task_events")
