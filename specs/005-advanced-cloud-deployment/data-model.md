# Data Model: TeamFlow Advanced Cloud Deployment (Phase 5)

**Feature**: 005-advanced-cloud-deployment | **Date**: 2026-01-29

## Overview

This document defines the complete data model for the Phase 5 Advanced Cloud Deployment feature. It extends the existing Phase II/IV data model with event streaming entities, recurrence rules, reminder settings, and WebSocket connections.

---

## 1. Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   User      │─────────▶│      Task        │◀────────│ Recurrence  │
│             │ 1:N     │                  │ 1:1     │    Rule     │
│ - id        │         │ - id             │         │             │
│ - email     │         │ - title          │         │ - frequency │
│ - role      │         │ - status         │         │ - interval  │
│             │         │ - recurrence_id ──┼────────▶│ - end_date  │
└─────────────┘         │ - reminder_id ───┼────────▶└─────────────┘
         │              │                  │
         │              │ - next_instance──┼────────────────────┐
         │              └──────────────────┘                    │
         │                                                    │
         ▼                                                    ▼
┌──────────────────┐                            ┌─────────────────────┐
│Reminder Settings │                            │   Task Event        │
│                  │                            │                     │
│ - task_id (PK)   │                            │ - id (PK)           │
│ - offsets        │                            │ - event_type        │
│ - channels       │                            │ - task_id (FK)      │
│ - preferences    │                            │ - user_id (FK)      │
└──────────────────┘                            │ - payload (JSON)    │
                                                 │ - timestamp         │
         │                                       └─────────────────────┘
         │                                                    │
         ▼                                                    ▼
┌──────────────────┐                            ┌─────────────────────┐
│ WebSocket Conn.  │                            │    Reminder Event   │
│                  │                            │                     │
│ - id (PK)        │                            │ - id (PK)           │
│ - user_id (FK)   │                            │ - task_id (FK)      │
│ - connected_at   │                            │ - user_id (FK)      │
│ - last_ping      │                            │ - remind_at         │
└──────────────────┘                            │ - status (sent/queued│
                                                 │ - sent_at           │
                                                 └─────────────────────┘
```

---

## 2. Extended Entities (Phase 5)

### 2.1 Task (Extended)

**Purpose**: Core task entity with new recurrence and reminder fields.

**New Fields Added**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `recurrence_rule` | JSONB | NULL | Recurrence configuration (see RecurrenceRule entity) |
| `reminder_settings` | JSONB | NULL | Reminder configuration (see ReminderSettings entity) |
| `next_instance_id` | UUID | FK → `tasks(id)`, NULL | Link to next occurrence of recurring task |

**SQL Migration**:
```sql
-- Add new columns to existing tasks table
ALTER TABLE tasks
ADD COLUMN recurrence_rule JSONB NULL,
ADD COLUMN reminder_settings JSONB NULL,
ADD COLUMN next_instance_id UUID NULL REFERENCES tasks(id) ON DELETE SET NULL;

-- Add indexes for recurrence queries
CREATE INDEX idx_tasks_recurrence_rule ON tasks(recurrence_rule) WHERE recurrence_rule IS NOT NULL;
CREATE INDEX idx_tasks_next_instance ON tasks(next_instance_id) WHERE next_instance_id IS NOT NULL;
```

**Recurrence Rule Schema** (within `recurrence_rule` JSONB):
```json
{
  "frequency": "daily" | "weekly" | "monthly" | "yearly",
  "interval": 1,
  "days_of_week": ["Monday", "Wednesday", "Friday"],
  "day_of_month": 15,
  "end_date": "2026-12-31T23:59:59Z",
  "max_occurrences": 10
}
```

**Reminder Settings Schema** (within `reminder_settings` JSONB):
```json
{
  "offsets": ["15m", "1h", "1d", "1w"],
  "channels": ["email", "push"],
  "custom_message": "Don't forget to complete this task!"
}
```

---

### 2.2 RecurrenceRule

**Purpose**: Defines recurrence pattern for recurring tasks. Embedded in `tasks.recurrence_rule` JSONB field.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `frequency` | TEXT | NOT NULL, CHECK IN (`daily`, `weekly`, `monthly`, `yearly`) | How often task repeats |
| `interval` | INTEGER | NOT NULL, DEFAULT 1, CHECK >= 1 | Frequency multiplier (e.g., 2 = every 2 weeks) |
| `days_of_week` | TEXT[] | NULL | For `weekly` frequency: which days of week |
| `day_of_month` | INTEGER | NULL, CHECK 1-31 | For `monthly` frequency: which day of month |
| `end_date` | TIMESTAMP | NULL | Recurrence stops after this date |
| `max_occurrences` | INTEGER | NULL, CHECK >= 1 | Recurrence stops after N occurrences |

**Python Model**:
```python
# teamflow-web/backend/app/models/recurrence.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime

class RecurrenceRule(BaseModel):
    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    interval: int = Field(default=1, ge=1)
    days_of_week: Optional[List[Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]] = None
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = Field(None, ge=1)

    @validator("days_of_week")
    def validate_days_for_weekly(cls, v, values):
        if values.get("frequency") == "weekly" and not v:
            raise ValueError("days_of_week required for weekly frequency")
        return v

    @validator("day_of_month")
    def validate_day_for_monthly(cls, v, values):
        if values.get("frequency") == "monthly" and not v:
            raise ValueError("day_of_month required for monthly frequency")
        return v
```

**Example Values**:
```python
# Daily task (every day)
RecurrenceRule(frequency="daily", interval=1)

# Weekly task (every Monday and Wednesday)
RecurrenceRule(frequency="weekly", interval=1, days_of_week=["Monday", "Wednesday"])

# Monthly task (every 15th of the month)
RecurrenceRule(frequency="monthly", interval=1, day_of_month=15)

# Biweekly task (every 2 weeks on Fridays)
RecurrenceRule(frequency="weekly", interval=2, days_of_week=["Friday"])

# Daily task with 10 occurrence limit
RecurrenceRule(frequency="daily", interval=1, max_occurrences=10)

# Weekly task ending on December 31, 2026
RecurrenceRule(
    frequency="weekly",
    interval=1,
    days_of_week=["Monday"],
    end_date=datetime(2026, 12, 31, 23, 59, 59)
)
```

---

### 2.3 ReminderSettings

**Purpose**: Defines when and how to send reminders for a task. Embedded in `tasks.reminder_settings` JSONB field.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `offsets` | TEXT[] | NOT NULL | Time offsets before due date (e.g., `["15m", "1h", "1d", "1w"]`) |
| `channels` | TEXT[] | NOT NULL, DEFAULT `["email"]` | Notification channels |
| `custom_message` | TEXT | NULL | Custom reminder message (optional) |

**Python Model**:
```python
# teamflow-web/backend/app/models/reminder.py
from pydantic import BaseModel, Field, validator
from typing import List, Literal, Optional

class ReminderSettings(BaseModel):
    offsets: List[Literal["15m", "1h", "1d", "1w"]] = Field(default=["1d"])
    channels: List[Literal["email", "push"]] = Field(default=["email"])
    custom_message: Optional[str] = Field(None, max_length=500)

    @validator("offsets")
    def validate_offsets_not_empty(cls, v):
        if not v:
            raise ValueError("offsets cannot be empty")
        return v
```

**Example Values**:
```python
# Default reminder (1 day before)
ReminderSettings()

# Multiple reminders (15 min, 1 hour, 1 day before)
ReminderSettings(offsets=["15m", "1h", "1d"])

# Email and push notifications
ReminderSettings(offsets=["1d"], channels=["email", "push"])

# Custom message
ReminderSettings(
    offsets=["1d"],
    channels=["email"],
    custom_message="This task is critical for the client deadline!"
)
```

---

### 2.4 TaskEvent

**Purpose**: Event log for all task state changes. Enables event replay and audit trail.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT `gen_random_uuid()` | Unique event identifier |
| `event_type` | TEXT | NOT NULL, CHECK IN (`created`, `updated`, `completed`, `deleted`, `assigned`) | Type of event |
| `task_id` | UUID | FK → `tasks(id)`, NOT NULL | Task that triggered event |
| `user_id` | UUID | FK → `users(id)`, NOT NULL | User who triggered event |
| `payload` | JSONB | NOT NULL | Event-specific data |
| `created_at` | TIMESTAMP | DEFAULT `NOW()` | When event occurred |

**SQL Definition**:
```sql
CREATE TABLE task_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL CHECK (event_type IN ('created', 'updated', 'completed', 'deleted', 'assigned')),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for event replay queries
CREATE INDEX idx_task_events_task_id ON task_events(task_id);
CREATE INDEX idx_task_events_created_at ON task_events(created_at DESC);
CREATE INDEX idx_task_events_event_type ON task_events(event_type);

-- Index for event replay by time range
CREATE INDEX idx_task_events_replay ON task_events(created_at DESC, task_id);
```

**Payload Schema** (per `event_type`):

**Created Event**:
```json
{
  "event_type": "created",
  "task": {
    "id": "task-uuid",
    "title": "Fix navbar bug",
    "description": "Navbar overlaps with hero section on mobile",
    "status": "todo",
    "priority": "high",
    "project_id": "project-uuid",
    "assignee_id": "user-uuid"
  }
}
```

**Updated Event**:
```json
{
  "event_type": "updated",
  "changes": {
    "status": {"from": "todo", "to": "doing"},
    "priority": {"from": "high", "to": "urgent"}
  }
}
```

**Completed Event**:
```json
{
  "event_type": "completed",
  "completed_at": "2026-01-29T12:00:00Z",
  "next_instance_id": "task-uuid-2"  // If task is recurring
}
```

**Assigned Event**:
```json
{
  "event_type": "assigned",
  "assignee_id": "user-uuid",
  "assigned_by": "admin-uuid"
}
```

**Python Model**:
```python
# teamflow-web/backend/app/models/event.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from enum import Enum

class EventType(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"
    ASSIGNED = "assigned"

class TaskEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    task_id: str
    user_id: str
    payload: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True  # SQLModel compatibility
```

---

### 2.5 ReminderEvent

**Purpose**: Tracks reminder notifications sent for tasks. Enables delivery tracking and escalation.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT `gen_random_uuid()` | Unique reminder identifier |
| `task_id` | UUID | FK → `tasks(id)`, NOT NULL | Task being reminded |
| `user_id` | UUID | FK → `users(id)`, NOT NULL | User receiving reminder |
| `remind_at` | TIMESTAMP | NOT NULL | When reminder should be sent |
| `due_at` | TIMESTAMP | NOT NULL | Task due date |
| `status` | TEXT | NOT NULL, DEFAULT `pending`, CHECK IN (`pending`, `sent`, `failed`) | Delivery status |
| `sent_at` | TIMESTAMP | NULL | When reminder was actually sent |
| `error_message` | TEXT | NULL | Error if sending failed |
| `created_at` | TIMESTAMP | DEFAULT `NOW()` | When reminder was scheduled |

**SQL Definition**:
```sql
CREATE TABLE reminder_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    remind_at TIMESTAMP NOT NULL,
    due_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    sent_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for reminder queries
CREATE INDEX idx_reminder_events_remind_at ON reminder_events(remind_at) WHERE status = 'pending';
CREATE INDEX idx_reminder_events_user_id ON reminder_events(user_id);
CREATE INDEX idx_reminder_events_task_id ON reminder_events(task_id);
```

**Python Model**:
```python
# teamflow-web/backend/app/models/reminder_event.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ReminderStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class ReminderEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    user_id: str
    remind_at: datetime
    due_at: datetime
    status: ReminderStatus = ReminderStatus.PENDING
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
```

---

### 2.6 WebSocketConnection

**Purpose**: Tracks active WebSocket connections for real-time updates. Stored in-memory (not persisted).

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `connection_id` | str | Unique connection identifier (UUID) |
| `user_id` | str | User who owns this connection |
| `websocket` | WebSocket | WebSocket object (FastAPI) |
| `connected_at` | datetime | When connection was established |
| `last_ping` | datetime | Last heartbeat timestamp |

**Python Model**:
```python
# teamflow-web/backend/microservices/realtime_sync_service/connection_manager.py
from fastapi import WebSocket
from datetime import datetime
from typing import Dict, List
import uuid

class WebSocketConnection:
    def __init__(self, user_id: str, websocket: WebSocket):
        self.connection_id = str(uuid.uuid4())
        self.user_id = user_id
        self.websocket = websocket
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()

    async def send(self, data: dict):
        """Send JSON data to this connection."""
        await self.websocket.send_json(data)

    async def ping(self):
        """Send ping to keep connection alive."""
        self.last_ping = datetime.utcnow()
        await self.websocket.send_json({"type": "ping", "timestamp": self.last_ping.isoformat()})

class ConnectionManager:
    def __init__(self):
        # user_id -> list of WebSocketConnection
        self.active_connections: Dict[str, List[WebSocketConnection]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept and register new WebSocket connection."""
        await websocket.accept()
        connection = WebSocketConnection(user_id, websocket)

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(connection)

        return connection

    async def disconnect(self, user_id: str, connection_id: str):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                c for c in self.active_connections[user_id]
                if c.connection_id != connection_id
            ]

    async def broadcast(self, user_id: str, data: dict):
        """Send data to all connections for a user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send(data)

    async def broadcast_all(self, data: dict):
        """Send data to all connected users."""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                await connection.send(data)
```

---

## 3. Kafka Event Schemas

### 3.1 CloudEvents Envelope Format

All Kafka events follow CloudEvents specification:

```json
{
  "specversion": "1.0",
  "id": "event-uuid",
  "source": "/teamflow/backend",
  "type": "com.teamflow.{entity}.{action}",
  "datacontenttype": "application/json",
  "subject": "task-uuid",
  "time": "2026-01-29T12:00:00Z",
  "data": { /* Event-specific payload */ }
}
```

---

### 3.2 Task Events Topic (`task-events`)

**Event Types**:
- `com.teamflow.task.created`
- `com.teamflow.task.updated`
- `com.teamflow.task.completed`
- `com.teamflow.task.deleted`
- `com.teamflow.task.assigned`

**Example - Task Created**:
```json
{
  "specversion": "1.0",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "source": "/teamflow/backend",
  "type": "com.teamflow.task.created",
  "datacontenttype": "application/json",
  "subject": "task-123",
  "time": "2026-01-29T12:00:00Z",
  "data": {
    "task_id": "123",
    "user_id": "user-abc",
    "project_id": "5",
    "title": "Fix navbar bug",
    "description": "Navbar overlaps with hero section",
    "status": "todo",
    "priority": "high",
    "assignee_id": "user-def",
    "due_at": "2026-02-01T17:00:00Z",
    "recurrence_rule": null,
    "reminder_settings": {
      "offsets": ["1d"],
      "channels": ["email"]
    }
  }
}
```

**Example - Task Completed**:
```json
{
  "specversion": "1.0",
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "source": "/teamflow/backend",
  "type": "com.teamflow.task.completed",
  "datacontenttype": "application/json",
  "subject": "task-123",
  "time": "2026-01-29T14:00:00Z",
  "data": {
    "task_id": "123",
    "user_id": "user-abc",
    "completed_at": "2026-01-29T14:00:00Z",
    "next_instance_id": "124",
    "recurrence_rule": {
      "frequency": "weekly",
      "interval": 1,
      "days_of_week": ["Monday"]
    }
  }
}
```

---

### 3.3 Reminders Topic (`reminders`)

**Event Types**:
- `com.teamflow.reminder.due`
- `com.teamflow.reminder.overdue`

**Example - Reminder Due**:
```json
{
  "specversion": "1.0",
  "id": "750e8400-e29b-41d4-a716-446655440002",
  "source": "/teamflow/backend",
  "type": "com.teamflow.reminder.due",
  "datacontenttype": "application/json",
  "subject": "task-123",
  "time": "2026-01-29T16:00:00Z",
  "data": {
    "task_id": "123",
    "user_id": "user-abc",
    "title": "Fix navbar bug",
    "due_at": "2026-02-01T17:00:00Z",
    "remind_at": "2026-01-31T17:00:00Z",
    "offset": "1d",
    "channels": ["email"],
    "custom_message": "Don't forget this task!"
  }
}
```

---

### 3.4 Task Updates Topic (`task-updates`)

**Event Types**:
- `com.teamflow.task.updated` (all updates for real-time sync)

**Example**:
```json
{
  "specversion": "1.0",
  "id": "850e8400-e29b-41d4-a716-446655440003",
  "source": "/teamflow/backend",
  "type": "com.teamflow.task.updated",
  "datacontenttype": "application/json",
  "subject": "task-123",
  "time": "2026-01-29T16:30:00Z",
  "data": {
    "task_id": "123",
    "event_type": "updated",
    "changes": {
      "status": "doing"
    },
    "updated_by": "user-abc",
    "timestamp": "2026-01-29T16:30:00Z"
  }
}
```

---

## 4. Database Migrations

### 4.1 Migration Scripts

**Migration 001: Add Recurrence and Reminder Fields**

```python
# alembic/versions/001_add_recurrence_reminder_fields.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('recurrence_rule', postgresql.JSONB(), nullable=True))
    op.add_column('tasks', sa.Column('reminder_settings', postgresql.JSONB(), nullable=True))
    op.add_column('tasks', sa.Column('next_instance_id', sa.UUID(), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_tasks_next_instance',
        'tasks', 'tasks',
        ['next_instance_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create indexes
    op.create_index('idx_tasks_recurrence_rule', 'tasks', ['recurrence_rule'], postgresql_where=sa.text("recurrence_rule IS NOT NULL"))
    op.create_index('idx_tasks_next_instance', 'tasks', ['next_instance_id'], postgresql_where=sa.text("next_instance_id IS NOT NULL"))

def downgrade():
    op.drop_index('idx_tasks_next_instance', table_name='tasks')
    op.drop_index('idx_tasks_recurrence_rule', table_name='tasks')
    op.drop_constraint('fk_tasks_next_instance', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'next_instance_id')
    op.drop_column('tasks', 'reminder_settings')
    op.drop_column('tasks', 'recurrence_rule')
```

**Migration 002: Create Task Events Table**

```python
# alembic/versions/002_create_task_events.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'task_events',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.CheckConstraint("event_type IN ('created', 'updated', 'completed', 'deleted', 'assigned')", name='ck_event_type')
    )

    # Foreign keys
    op.create_foreign_key('fk_task_events_task', 'task_events', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_task_events_user', 'task_events', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Indexes
    op.create_index('idx_task_events_task_id', 'task_events', ['task_id'])
    op.create_index('idx_task_events_created_at', 'task_events', [sa.text('created_at DESC')])
    op.create_index('idx_task_events_event_type', 'task_events', ['event_type'])

def downgrade():
    op.drop_index('idx_task_events_event_type', table_name='task_events')
    op.drop_index('idx_task_events_created_at', table_name='task_events')
    op.drop_index('idx_task_events_task_id', table_name='task_events')
    op.drop_constraint('fk_task_events_user', 'task_events', type_='foreignkey')
    op.drop_constraint('fk_task_events_task', 'task_events', type_='foreignkey')
    op.drop_table('task_events')
```

**Migration 003: Create Reminder Events Table**

```python
# alembic/versions/003_create_reminder_events.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'reminder_events',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('remind_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('due_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
        sa.CheckConstraint("status IN ('pending', 'sent', 'failed')", name='ck_reminder_status')
    )

    # Foreign keys
    op.create_foreign_key('fk_reminder_events_task', 'reminder_events', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_reminder_events_user', 'reminder_events', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Indexes
    op.create_index('idx_reminder_events_remind_at', 'reminder_events', ['remind_at'], postgresql_where=sa.text("status = 'pending'"))
    op.create_index('idx_reminder_events_user_id', 'reminder_events', ['user_id'])
    op.create_index('idx_reminder_events_task_id', 'reminder_events', ['task_id'])

def downgrade():
    op.drop_index('idx_reminder_events_task_id', table_name='reminder_events')
    op.drop_index('idx_reminder_events_user_id', table_name='reminder_events')
    op.drop_index('idx_reminder_events_remind_at', table_name='reminder_events')
    op.drop_constraint('fk_reminder_events_user', 'reminder_events', type_='foreignkey')
    op.drop_constraint('fk_reminder_events_task', 'reminder_events', type_='foreignkey')
    op.drop_table('reminder_events')
```

---

## 5. Data Access Patterns

### 5.1 Event Publishing Pattern

```python
# teamflow-web/backend/app/services/event_publisher.py
from httpx import AsyncClient
from datetime import datetime
from typing import Dict, Any
import os

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

class EventPublisher:
    def __init__(self):
        self.dapr_url = f"http://localhost:{DAPR_HTTP_PORT}"
        self.client = AsyncClient()

    async def publish_task_event(
        self,
        event_type: str,
        task_id: str,
        user_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Publish task event to Kafka via Dapr."""
        cloud_event = {
            "specversion": "1.0",
            "id": str(uuid.uuid4()),
            "source": "/teamflow/backend",
            "type": f"com.teamflow.task.{event_type}",
            "datacontenttype": "application/json",
            "subject": task_id,
            "time": datetime.utcnow().isoformat(),
            "data": data
        }

        try:
            response = await self.client.post(
                f"{self.dapr_url}/v1.0/publish/kafka-pubsub/task-events",
                json=cloud_event,
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
```

### 5.2 Recurrence Calculation Pattern

```python
# teamflow-web/backend/app/services/recurrence_calculator.py
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
from datetime import datetime, timedelta
from typing import Optional

class RecurrenceCalculator:
    @staticmethod
    def calculate_next_instance(
        completed_at: datetime,
        rule: dict
    ) -> Optional[datetime]:
        """Calculate next occurrence based on recurrence rule."""
        frequency = rule["frequency"]
        interval = rule.get("interval", 1)

        if frequency == "daily":
            return completed_at + timedelta(days=interval)

        elif frequency == "weekly":
            days_map = {
                "Monday": MO, "Tuesday": TU, "Wednesday": WE,
                "Thursday": TH, "Friday": FR, "Saturday": SA, "Sunday": SU
            }
            weekdays = [days_map[d] for d in rule.get("days_of_week", [MO])]
            next_dates = list(rrule(WEEKLY, interval=interval, byweekday=weekdays, dtstart=completed_at, count=2))
            return next_dates[1] if len(next_dates) > 1 else None

        elif frequency == "monthly":
            day = rule.get("day_of_month", completed_at.day)
            month = completed_at.month + interval
            year = completed_at.year
            if month > 12:
                year += 1
                month = month % 12
            return datetime(year, month, day)

        elif frequency == "yearly":
            return datetime(completed_at.year + interval, completed_at.month, completed_at.day)

        return None
```

---

## 6. Validation Rules

### 6.1 Recurrence Rule Validation

- ✅ `frequency` must be one of: `daily`, `weekly`, `monthly`, `yearly`
- ✅ `interval` must be >= 1
- ✅ If `frequency == "weekly"`, `days_of_week` is required
- ✅ If `frequency == "monthly"`, `day_of_month` is required (1-31)
- ✅ `end_date` must be in the future
- ✅ `max_occurrences` must be >= 1

### 6.2 Reminder Settings Validation

- ✅ `offsets` cannot be empty
- ✅ `offsets` must contain valid values: `["15m", "1h", "1d", "1w"]`
- ✅ `channels` must contain valid values: `["email", "push"]`
- ✅ `custom_message` max length: 500 characters

### 6.3 Task Event Validation

- ✅ `event_type` must be one of: `created`, `updated`, `completed`, `deleted`, `assigned`
- ✅ `task_id` must reference existing task
- ✅ `user_id` must reference existing user
- ✅ `payload` must be valid JSON

---

## 7. Performance Considerations

### 7.1 Index Strategy

- ✅ **Task queries**: Index on `recurrence_rule` for filtering recurring tasks
- ✅ **Event replay**: Composite index on `(created_at DESC, task_id)` for time-range queries
- ✅ **Reminder scheduling**: Partial index on `remind_at WHERE status = 'pending'`
- ✅ **User notifications**: Index on `user_id` for all event tables

### 7.2 Partitioning (Future Enhancement)

For high-volume event streams, consider table partitioning:

```sql
-- Partition task_events by month (PostgreSQL 11+)
CREATE TABLE task_events (
    -- columns
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE task_events_2026_01 PARTITION OF task_events
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

---

## 8. Data Retention

| Table | Retention Period | Cleanup Strategy |
|-------|------------------|------------------|
| `task_events` | 90 days | Scheduled job deletes old records |
| `reminder_events` | 30 days | Scheduled job deletes old records |
| `WebSocketConnection` | In-memory only | Cleared on disconnect |

**Cleanup Job** (via Dapr cron binding):
```yaml
# bindings/task-cleanup.cron.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-cleanup-cron
  namespace: teamflow
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "0 2 * * *"  # Daily at 2 AM
```

---

**Data Model Status**: ✅ Complete - All entities defined, migrations scripted, Kafka schemas specified.
