"""Add performance indexes for common queries (T183).

Revision ID: 010_add_performance_indexes
Revises: 003_create_reminder_events
Create Date: 2026-02-01

This migration adds composite indexes to improve performance of common queries:
- Tasks by agency + status (Kanban board)
- Tasks by assignee + status (user task list)
- Tasks by project + status (project view)
- Tasks by agency + due_date (upcoming deadlines)
- Time entries by user + date (time tracking)
- Messages by conversation + created_at (chat history)
- Conversations by user + archived + created_at (conversation list)
- Projects by agency + status (project list)

These indexes optimize the most frequently executed queries in the application
and are essential for scaling to multiple concurrent users.

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "010_add_performance_indexes"
down_revision = "003_create_reminder_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add composite performance indexes for common query patterns."""

    # ==================== TASKS ====================
    # Index for Kanban board: tasks by agency and status
    # Query: SELECT * FROM tasks WHERE agency_id = ? AND status IN (...)
    op.create_index(
        "ix_tasks_agency_status",
        "tasks",
        ["agency_id", "status"],
        unique=False,
    )

    # Index for user task list: tasks by assignee and status
    # Query: SELECT * FROM tasks WHERE assignee_id = ? AND status != 'ARCHIVED'
    op.create_index(
        "ix_tasks_assignee_status",
        "tasks",
        ["assignee_id", "status"],
        unique=False,
    )

    # Index for project view: tasks by project and status
    # Query: SELECT * FROM tasks WHERE project_id = ? ORDER BY status
    op.create_index(
        "ix_tasks_project_status",
        "tasks",
        ["project_id", "status"],
        unique=False,
    )

    # Index for upcoming deadlines: tasks by agency and due_date
    # Query: SELECT * FROM tasks WHERE agency_id = ? AND due_date <= ? AND status NOT IN ('DONE', 'ARCHIVED')
    op.create_index(
        "ix_tasks_agency_duedate",
        "tasks",
        ["agency_id", "due_date"],
        unique=False,
    )

    # ==================== TIME ENTRIES ====================
    # Index for time tracking reports: entries by user and date
    # Query: SELECT * FROM time_entries WHERE user_id = ? AND entry_date BETWEEN ? AND ?
    op.create_index(
        "ix_time_entries_user_date",
        "time_entries",
        ["user_id", "entry_date"],
        unique=False,
    )

    # Index for task time tracking: entries by task and date
    # Query: SELECT * FROM time_entries WHERE task_id = ? ORDER BY entry_date DESC
    op.create_index(
        "ix_time_entries_task_date",
        "time_entries",
        ["task_id", "entry_date"],
        unique=False,
    )

    # ==================== MESSAGES ====================
    # Index for chat history: messages by conversation and creation time
    # Query: SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at LIMIT ?
    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
        unique=False,
    )

    # ==================== CONVERSATIONS ====================
    # Index for conversation list: user conversations by archived status and time
    # Query: SELECT * FROM conversations WHERE user_id = ? AND is_archived = false ORDER BY updated_at DESC
    op.create_index(
        "ix_conversations_user_archived_updated",
        "conversations",
        ["user_id", "is_archived", "updated_at"],
        unique=False,
    )

    # ==================== PROJECTS ====================
    # Index for project list: projects by agency and status
    # Query: SELECT * FROM projects WHERE agency_id = ? AND status = 'active'
    op.create_index(
        "ix_projects_agency_status",
        "projects",
        ["agency_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    """Remove performance indexes."""

    # Projects
    op.drop_index("ix_projects_agency_status", table_name="projects")

    # Conversations
    op.drop_index("ix_conversations_user_archived_updated", table_name="conversations")

    # Messages
    op.drop_index("ix_messages_conversation_created", table_name="messages")

    # Time entries
    op.drop_index("ix_time_entries_task_date", table_name="time_entries")
    op.drop_index("ix_time_entries_user_date", table_name="time_entries")

    # Tasks
    op.drop_index("ix_tasks_agency_duedate", table_name="tasks")
    op.drop_index("ix_tasks_project_status", table_name="tasks")
    op.drop_index("ix_tasks_assignee_status", table_name="tasks")
    op.drop_index("ix_tasks_agency_status", table_name="tasks")
