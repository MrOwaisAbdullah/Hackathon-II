"""Fix task enum case to match Python enum names.

Revision ID: 004_fix_task_enum_case
Revises: 003_add_task_indexes
Create Date: 2026-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_fix_task_enum_case"
down_revision: Union[str, None] = "003_add_task_indexes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update task enum types to use uppercase values matching Python enums."""

    # Step 1: Convert columns to TEXT (this allows us to bypass enum constraints)
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE TEXT USING status::text")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE TEXT USING priority::text")

    # Step 2: Update data from lowercase to uppercase
    op.execute("UPDATE tasks SET status = 'TODO' WHERE status = 'todo'")
    op.execute("UPDATE tasks SET status = 'DOING' WHERE status = 'doing'")
    op.execute("UPDATE tasks SET status = 'REVIEW' WHERE status = 'review'")
    op.execute("UPDATE tasks SET status = 'DONE' WHERE status = 'done'")

    op.execute("UPDATE tasks SET priority = 'LOW' WHERE priority = 'low'")
    op.execute("UPDATE tasks SET priority = 'MEDIUM' WHERE priority = 'medium'")
    op.execute("UPDATE tasks SET priority = 'HIGH' WHERE priority = 'high'")

    # Step 3: Drop old enum types
    op.execute("DROP TYPE taskstatus CASCADE")
    op.execute("DROP TYPE taskpriority CASCADE")

    # Step 4: Create new enum types with uppercase values
    op.execute("CREATE TYPE taskstatus AS ENUM ('TODO', 'DOING', 'REVIEW', 'DONE')")
    op.execute("CREATE TYPE taskpriority AS ENUM ('LOW', 'MEDIUM', 'HIGH')")

    # Step 5: Convert columns back to enum type
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus USING status::text::taskstatus")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE taskpriority USING priority::text::taskpriority")


def downgrade() -> None:
    """Revert to lowercase enum values."""

    # Convert to TEXT first
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE TEXT USING status::text")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE TEXT USING priority::text")

    # Update data back to lowercase
    op.execute("UPDATE tasks SET status = 'todo' WHERE status = 'TODO'")
    op.execute("UPDATE tasks SET status = 'doing' WHERE status = 'DOING'")
    op.execute("UPDATE tasks SET status = 'review' WHERE status = 'REVIEW'")
    op.execute("UPDATE tasks SET status = 'done' WHERE status = 'DONE'")

    op.execute("UPDATE tasks SET priority = 'low' WHERE priority = 'LOW'")
    op.execute("UPDATE tasks SET priority = 'medium' WHERE priority = 'MEDIUM'")
    op.execute("UPDATE tasks SET priority = 'high' WHERE priority = 'HIGH'")

    # Drop uppercase enum types
    op.execute("DROP TYPE taskstatus CASCADE")
    op.execute("DROP TYPE taskpriority CASCADE")

    # Recreate with lowercase values
    op.execute("CREATE TYPE taskstatus AS ENUM ('todo', 'doing', 'review', 'done')")
    op.execute("CREATE TYPE taskpriority AS ENUM ('low', 'medium', 'high')")

    # Convert columns back to enum type
    op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE taskstatus USING status::text::taskstatus")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE taskpriority USING priority::text::taskpriority")
