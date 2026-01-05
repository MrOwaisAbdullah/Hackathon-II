"""Add status field to projects table

Revision ID: 008
Revises: 007_add_user_management_fields
Create Date: 2026-01-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_project_status'
down_revision = '007_add_user_management_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add status column to projects table."""
    # Add status column with default value 'active'
    op.add_column(
        'projects',
        sa.Column(
            'status',
            sa.String(length=50),
            server_default='active',
            nullable=False
        )
    )

    # Create index on status for filtering
    op.create_index('ix_projects_status', 'projects', ['status'])


def downgrade() -> None:
    """Remove status column from projects table."""
    op.drop_index('ix_projects_status', table_name='projects')
    op.drop_column('projects', 'status')
