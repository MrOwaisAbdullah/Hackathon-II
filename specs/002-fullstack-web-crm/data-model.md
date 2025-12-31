# Data Model: TeamFlow Web (Phase 2)

**Branch**: `002-fullstack-web-crm` | **Date**: 2025-01-29 | **Plan**: [plan.md](./plan.md)

## Summary

This document defines the database schema for TeamFlow Phase 2. The data model supports multi-tenant agency isolation with JWT-scoped queries, task management with status workflows, team assignment, time tracking, and profitability calculations.

---

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Agency    │ 1    *│    User     │ *    *│    Task     │
│─────────────│───────│─────────────│───────│─────────────│
│ id          │       │ id          │       │ id          │
│ name        │       │ email       │       │ title       │
│ created_at  │       │ name        │       │ description │
└─────────────┘       │ agency_id   │       │ status      │
                      │ created_at  │       │ project_id  │
                      └─────────────┘       │ assignee_id │
                                            │ agency_id   │
                                            │ created_at  │
                                            └─────────────┘
                                                  │ 1
                                                  │
                                                  │ 1
┌─────────────┐ 1     *│─────────────│ *     1┌─────────────┐
│ TimeEntry   │───────│    Task     │───────│  Project    │
│─────────────│       │─────────────│       │─────────────│
│ id          │       │ (see above) │       │ id          │
│ task_id     │       └─────────────┘       │ name        │
│ user_id     │                              │ agency_id   │
│ duration    │                              │ created_at  │
│ date        │                              └─────────────┘
│ created_at  │
└─────────────┘
```

---

## Entities

### 1. Agency (Tenant)

The Agency entity represents a creative agency or team. All other entities are scoped to an agency for multi-tenant isolation.

**Table**: `agencies`

**Fields**:

| Name | Type | Constraints | Description |
|------|------|-------------|-------------|
| `id` | UUID | PK, default=uuid4 | Unique agency identifier |
| `name` | VARCHAR(255) | NOT NULL | Agency display name |
| `created_at` | TIMESTAMP | default=now() | Creation timestamp |
| `updated_at` | TIMESTAMP | onupdate=now() | Last update timestamp |

**Indexes**:
- `idx_agencies_id` on `id`

**SQLModel Definition**:

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import uuid4

class Agency(SQLModel, table=True):
    __tablename__ = "agencies"

    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
```

---

### 2. User (Team Member)

The User entity represents team members within an agency. Users can be assigned tasks and log time entries.

**Table**: `users`

**Fields**:

| Name | Type | Constraints | Description |
|------|------|-------------|-------------|
| `id` | UUID | PK, default=uuid4 | Unique user identifier |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | User email (login) |
| `name` | VARCHAR(255) | NOT NULL | Display name |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `agency_id` | UUID | FK, NOT NULL | Agency (tenant) |
| `created_at` | TIMESTAMP | default=now() | Creation timestamp |
| `updated_at` | TIMESTAMP | onupdate=now() | Last update timestamp |

**Indexes**:
- `idx_users_id` on `id`
- `idx_users_agency_id` on `agency_id`
- `idx_users_email` on `email` (UNIQUE)

**Foreign Keys**:
- `agency_id` → `agencies.id` (CASCADE DELETE)

**SQLModel Definition**:

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    agency_id: str = Field(foreign_key="agencies.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
```

---

### 3. Project

The Project entity groups related tasks. Projects are scoped to agencies and can have associated time entries.

**Table**: `projects`

**Fields**:

| Name | Type | Constraints | Description |
|------|------|-------------|-------------|
| `id` | UUID | PK, default=uuid4 | Unique project identifier |
| `name` | VARCHAR(255) | NOT NULL | Project name |
| `description` | TEXT | NULLABLE | Project description |
| `agency_id` | UUID | FK, NOT NULL | Agency (tenant) |
| `created_at` | TIMESTAMP | default=now() | Creation timestamp |
| `updated_at` | TIMESTAMP | onupdate=now() | Last update timestamp |

**Indexes**:
- `idx_projects_id` on `id`
- `idx_projects_agency_id` on `agency_id`

**Foreign Keys**:
- `agency_id` → `agencies.id` (CASCADE DELETE)

**SQLModel Definition**:

```python
class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    agency_id: str = Field(foreign_key="agencies.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
```

---

### 4. Task (Core Entity)

The Task entity represents work items on the Kanban board. Tasks have status, assignees, projects, and time entries.

**Table**: `tasks`

**Fields**:

| Name | Type | Constraints | Description |
|------|------|-------------|-------------|
| `id` | UUID | PK, default=uuid4 | Unique task identifier |
| `title` | VARCHAR(255) | NOT NULL | Task title |
| `description` | TEXT | NULLABLE | Detailed description |
| `status` | VARCHAR(50) | NOT NULL, default='todo' | Status: todo/doing/review/done |
| `priority` | VARCHAR(50) | NULLABLE | Priority: low/medium/high |
| `project_id` | UUID | FK, NULLABLE | Associated project |
| `assignee_id` | UUID | FK, NULLABLE | Assigned user (set to NULL on user delete) |
| `agency_id` | UUID | FK, NOT NULL | Agency (tenant) |
| `due_date` | DATE | NULLABLE | Task due date |
| `created_at` | TIMESTAMP | default=now() | Creation timestamp |
| `updated_at` | TIMESTAMP | onupdate=now() | Last update timestamp |

**Indexes**:
- `idx_tasks_id` on `id`
- `idx_tasks_agency_id` on `agency_id`
- `idx_tasks_status` on `status`
- `idx_tasks_project_id` on `project_id`
- `idx_tasks_assignee_id` on `assignee_id`
- `idx_tasks_agency_status` on `(agency_id, status)` (composite)

**Foreign Keys**:
- `agency_id` → `agencies.id` (CASCADE DELETE)
- `project_id` → `projects.id` (SET NULL on delete)
- `assignee_id` → `users.id` (SET NULL on delete - FR-047)

**SQLModel Definition**:

```python
from enum import Enum
from datetime import date

class TaskStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    REVIEW = "review"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    priority: Optional[TaskPriority] = Field(default=None)
    project_id: Optional[str] = Field(default=None, foreign_key="projects.id")
    assignee_id: Optional[str] = Field(default=None, foreign_key="users.id")
    agency_id: str = Field(foreign_key="agencies.id", index=True)
    due_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
```

---

### 5. TimeEntry

The TimeEntry entity tracks time logged against tasks for profitability calculations.

**Table**: `time_entries`

**Fields**:

| Name | Type | Constraints | Description |
|------|------|-------------|-------------|
| `id` | UUID | PK, default=uuid4 | Unique entry identifier |
| `task_id` | UUID | FK, NOT NULL | Associated task |
| `user_id` | UUID | FK, NOT NULL | User who logged time |
| `duration` | INTEGER | NOT NULL | Duration in minutes |
| `date` | DATE | NOT NULL | Date of work |
| `description` | TEXT | NULLABLE | Work description |
| `created_at` | TIMESTAMP | default=now() | Creation timestamp |

**Indexes**:
- `idx_time_entries_id` on `id`
- `idx_time_entries_task_id` on `task_id`
- `idx_time_entries_user_id` on `user_id`
- `idx_time_entries_date` on `date`

**Foreign Keys**:
- `task_id` → `tasks.id` (CASCADE DELETE)
- `user_id` → `users.id` (CASCADE DELETE)

**SQLModel Definition**:

```python
class TimeEntry(SQLModel, table=True):
    __tablename__ = "time_entries"

    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    duration: int = Field(index=True)  # minutes
    date: date = Field(index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Relationships

### Agency Relationships

| Entity | Relationship | Type | Cascade |
|--------|-------------|------|---------|
| Agency → Users | One-to-Many | 1:N | CASCADE |
| Agency → Projects | One-to-Many | 1:N | CASCADE |
| Agency → Tasks | One-to-Many | 1:N | CASCADE |

### Task Relationships

| Entity | Relationship | Type | Cascade |
|--------|-------------|------|---------|
| Task → Project | Many-to-One | N:1 | SET NULL |
| Task → Assignee | Many-to-One | N:1 | SET NULL (FR-047) |
| Task → TimeEntries | One-to-Many | 1:N | CASCADE |

### Project Relationships

| Entity | Relationship | Type | Cascade |
|--------|-------------|------|---------|
| Project → Tasks | One-to-Many | 1:N | CASCADE (via task.project_id) |

### User Relationships

| Entity | Relationship | Type | Cascade |
|--------|-------------|------|---------|
| User → AssignedTasks | One-to-Many | 1:N | SET NULL (via task.assignee_id) |
| User → TimeEntries | One-to-Many | 1:N | CASCADE |

### TimeEntry Relationships

| Entity | Relationship | Type | Cascade |
|--------|-------------|------|---------|
| TimeEntry → Task | Many-to-One | N:1 | CASCADE |
| TimeEntry → User | Many-to-One | N:1 | CASCADE |

---

## Multi-Tenant Isolation

**Tenant Scoping**: All queries MUST include `agency_id` filter to enforce tenant isolation.

**JWT Claims**:
```json
{
  "sub": "user_id",
  "agency_id": "agency_uuid",
  "email": "user@example.com"
}
```

**Middleware Pattern**:
```python
# All API endpoints receive current_user with verified agency_id
@router.get("/tasks")
def get_tasks(
    session: SessionDep,
    current_user: CurrentUser  # From JWT, includes agency_id
):
    # Query scoped to agency_id automatically
    tasks = session.exec(
        select(Task).where(Task.agency_id == current_user.agency_id)
    ).all()
    return tasks
```

---

## Database Migration Strategy

**Migration Tool**: Alembic (FastAPI integration)

**Migration Files**:
```
backend/migrations/versions/
├── 001_initial_schema.py
├── 002_add_indexes.py
└── 003_add_priority_column.py
```

**Rollback Strategy**:
- Downgrade scripts for each migration
- Database backup before major schema changes
- Feature flags for breaking changes

---

## Data Retention

| Entity | Retention Policy | Rationale |
|--------|-----------------|-----------|
| Agency | Indefinite | Core tenant data |
| User | Indefinite | Audit trail |
| Project | Indefinite | Agency history |
| Task | 90 days soft delete | Recovery window |
| TimeEntry | 7 years | Financial compliance |

---

## Performance Considerations

**Indexing Strategy**:
- All foreign keys indexed
- Composite index on `(agency_id, status)` for filtered queries
- Date index on time_entries for analytics queries

**Query Optimization**:
```python
# Efficient: uses composite index
select(Task).where(Task.agency_id == agency_id).where(Task.status == "done")

# Inefficient: two separate filters (use AND instead)
select(Task).where(Task.agency_id == agency_id).filter(Task.status == "done")
```

**Connection Pooling**:
- Neon provides built-in connection pooling
- Pool size: 10 connections (default)
- Timeout: 30 seconds

---

## Next Steps

1. ✅ Data model defined
2. Generate API contracts (OpenAPI spec)
3. Create quickstart guide
4. Implement SQLModel migrations
