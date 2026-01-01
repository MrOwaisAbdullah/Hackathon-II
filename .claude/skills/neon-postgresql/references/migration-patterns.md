# Migration Patterns with Alembic

Complete guide for database migrations using Alembic with SQLModel and PostgreSQL.

## Initial Setup

### Installation

```bash
uv add alembic
cd backend
uv run alembic init alembic
```

### Configure alembic/env.py

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel
from config import DATABASE_URL, sync_engine

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = SQLModel.metadata

# Use sync engine for migrations
engine = sync_engine
```

### Configure alembic.ini

```ini
[alembic]
script_location = alembic
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s
sqlalchemy.url = postgresql://user:pass@localhost/dbname?sslmode=require

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic
```

## Migration Workflow

### Create Migration

```bash
# Auto-generate from model changes
uv run alembic revision --autogenerate -m "Add user preferences table"

# Create empty migration (for manual SQL)
uv run alembic revision -m "Custom SQL migration"
```

### Apply Migration

```bash
# Upgrade to latest
uv run alembic upgrade head

# Upgrade to specific revision
uv run alembic upgrade <revision_id>

# Show current version
uv run alembic current

# Show history
uv run alembic history
```

### Rollback

```bash
# Rollback one step
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>

# Rollback everything
uv run alembic downgrade base
```

## Migration File Structure

### Auto-Generated Migration

```python
"""Add user preferences table

Revision ID: 00123456789
Revises:
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '00123456789'
down_revision = '00123456788'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(), nullable=True),
        sa.Column('language', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_user_preferences_user_id'),
        'user_preferences',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_user_preferences_user_id'),
        table_name='user_preferences'
    )
    op.drop_table('user_preferences')
```

### Manual SQL Migration

```python
"""Add full-text search index

Revision ID: 00123456790
Revises: 00123456789
Create Date: 2025-01-01 13:00:00.000000

"""
from alembic import op

revision = '00123456790'
down_revision = '00123456789'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Manual SQL for PostgreSQL-specific features
    op.execute("""
        CREATE INDEX idx_users_fulltext ON users
        USING gin(to_tsvector('english', full_name || ' ' || email));
    """)


def downgrade() -> None:
    op.execute("DROP INDEX idx_users_fulltext;")
```

## Common Migration Scenarios

### 1. Add Column to Existing Table

```python
def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('phone', sa.String(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('users', 'phone')
```

### 2. Make Column Required (With Default)

```python
def upgrade() -> None:
    # Step 1: Add column as nullable
    op.add_column('users', sa.Column('status', sa.String(), nullable=True))

    # Step 2: Backfill data
    op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")

    # Step 3: Make non-nullable
    op.alter_column('users', 'status', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'status')
```

### 3. Rename Column

```python
def upgrade() -> None:
    op.alter_column(
        'users',
        'old_name',
        new_column_name='new_name'
    )

def downgrade() -> None:
    op.alter_column(
        'users',
        'new_name',
        new_column_name='old_name'
    )
```

### 4. Add Foreign Key

```python
def upgrade() -> None:
    op.create_foreign_key(
        'fk_chat_sessions_user_id_users',
        'chat_sessions',
        'user_id',
        'users',
        'id'
    )

def downgrade() -> None:
    op.drop_constraint(
        'fk_chat_sessions_user_id_users',
        'chat_sessions',
        type_='foreignkey'
    )
```

### 5. Create Index

```python
def upgrade() -> None:
    # Simple index
    op.create_index(
        'ix_users_email',
        'users',
        ['email']
    )

    # Composite index
    op.create_index(
        'ix_users_email_status',
        'users',
        ['email', 'is_verified']
    )

    # Unique index
    op.create_index(
        'ix_users_email_unique',
        'users',
        ['email'],
        unique=True
    )

def downgrade() -> None:
    op.drop_index('ix_users_email_unique', table_name='users')
```

## Data Migrations

### Migrate Existing Data

```python
def upgrade() -> None:
    # Add new column
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))

    # Migrate data from old columns
    connection = op.get_bind()
    connection.execute(
        "UPDATE users SET full_name = first_name || ' ' || last_name"
    )

    # Drop old columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')

def downgrade() -> None:
    # Re-add old columns
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))

    # Migrate data back
    connection = op.get_bind()
    connection.execute("""
        UPDATE users
        SET first_name = SPLIT_PART(full_name, ' ', 1),
            last_name = SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
    """)

    op.drop_column('users', 'full_name')
```

## PostgreSQL-Specific Migrations

### Enable Extensions

```python
def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')  # Trigram matching

def downgrade() -> None:
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm"')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
```

### JSONB Columns

```python
def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('metadata', sa.JSON(), nullable=True)
    )

    # Add GIN index for JSONB
    op.execute("""
        CREATE INDEX idx_users_metadata_gin
        ON users USING gin (metadata jsonb_path_ops);
    """)

def downgrade() -> None:
    op.execute("DROP INDEX idx_users_metadata_gin;")
    op.drop_column('users', 'metadata')
```

## Best Practices

### 1. Always Write Downgrade

Every migration must be reversible. If you can't reverse it, document why.

### 2. Test Migrations Locally

```bash
# Create test database
createdb test_migration

# Run migration
DATABASE_URL=postgresql://localhost/test_migration uv run alembic upgrade head

# Verify schema
psql test_migration -c "\d users"

# Rollback
uv run alembic downgrade base

# Cleanup
dropdb test_migration
```

### 3. Use Transactions

```python
from alembic import op

def upgrade() -> None:
    # Wrap in transaction for atomicity
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column('new_col', sa.String(), nullable=True))
        batch_op.drop_column('old_col')
```

### 4. Version Control

```bash
# Tag production releases
uv run alembic stamp head
```

## Troubleshooting

### "Target database is not up to date"

```bash
# Check current version
uv run alembic current

# Compare to history
uv run alembic history

# Stamp to correct version if needed
uv run alembic stamp <revision_id>
```

### "Foreign key constraint fails"

Drop data before dropping constraint in downgrade:

```python
def downgrade() -> None:
    # Clear referencing data first
    op.execute("DELETE FROM chat_sessions WHERE user_id IS NOT NULL")
    op.drop_constraint('fk_sessions_user', 'chat_sessions')
```

### Migration Runs Slow

```bash
# Run with verbose SQL to see what's executing
SQLALCHEMY_ECHO=1 uv run alembic upgrade head

# Consider batching for large tables
op.execute("INSERT INTO new_table SELECT * FROM old_table LIMIT 10000")
```
