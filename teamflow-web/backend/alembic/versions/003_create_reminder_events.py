"""T067: Create reminder_events table

Revision ID: 003_create_reminder_events
Revises: 002_create_task_events
Create Date: 2026-01-31

This migration creates the reminder_events table to track sent reminders
for due date notifications. This prevents duplicate reminder emails and
enables retry logic for failed sends.

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "003_create_reminder_events"
down_revision = "002_create_task_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create reminder_events table with indexes for efficient querying"""

    # Create reminder_events table
    op.create_table(
        "reminder_events",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("task_id", sa.UUID(), nullable=False, index=True),
        sa.Column("agency_id", sa.UUID(), nullable=False, index=True),
        sa.Column("user_id", sa.UUID(), nullable=False, index=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "SENT", "FAILED", name="remindereventstatus"),
            nullable=False,
            default="PENDING",
            index=True,
        ),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("task_title", sa.String(), nullable=False),
        sa.Column("task_description", sa.Text(), nullable=True),
        sa.Column("user_email", sa.String(), nullable=False),
        sa.Column("user_name", sa.String(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, default=0),
        sa.Column("last_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            onupdate=sa.text("NOW()"),
        ),
        # Foreign key constraints
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["agency_id"],
            ["agencies.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )

    # Create composite index for querying pending reminders (cron job)
    # This efficiently finds reminders that need to be sent now
    op.create_index(
        "ix_reminder_events_pending_lookup",
        "reminder_events",
        ["status", "remind_at"],
        unique=False,
    )

    # Create index for user's reminder history
    op.create_index(
        "ix_reminder_events_user_history",
        "reminder_events",
        ["user_id", "created_at"],
        unique=False,
    )

    # Create unique constraint to prevent duplicate reminders for same task+time
    # This ensures we don't send multiple identical reminders
    op.create_unique_constraint(
        "uq_reminder_events_task_remind_at",
        "reminder_events",
        ["task_id", "remind_at"],
    )


def downgrade() -> None:
    """Remove reminder_events table and indexes"""

    # Drop unique constraint
    op.drop_constraint(
        "uq_reminder_events_task_remind_at",
        "reminder_events",
        type_="unique",
    )

    # Drop indexes
    op.drop_index("ix_reminder_events_user_history", table_name="reminder_events")
    op.drop_index("ix_reminder_events_pending_lookup", table_name="reminder_events")

    # Drop table
    op.drop_table("reminder_events")

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS remindereventstatus")
