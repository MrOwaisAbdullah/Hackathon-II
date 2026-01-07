# Data Model: TeamFlow AI Chatbot (Phase 3)

**Feature**: 001-ai-chatbot | **Date**: 2025-01-06

## Overview

This document defines the complete data model for the Phase 3 AI Chatbot feature. It extends the existing Phase II data model with conversation management, user preferences, and RAG storage.

---

## 1. Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   User      │─────────▶│  Conversation    │◀────────│   Message   │
│             │ 1:N     │                  │ 1:N     │             │
│ - id        │         │ - id             │         │ - id        │
│ - email     │         │ - user_id        │         │ - content   │
│ - role      │         │ - title          │         │ - role      │
│             │         │ - created_at     │         │ - created_at│
└─────────────┘         └──────────────────┘         └─────────────┘
       │                                                    │
       │                                                    │
       ▼                                                    ▼
┌──────────────────┐                            ┌─────────────────────┐
│UserChatPreference│                            │    ToolCall          │
│                  │                            │                     │
│ - user_id (PK)   │                            │ - message_id (FK)   │
│ - language       │                            │ - tool_name         │
│ - voice_enabled  │                            │ - parameters (JSON) │
└──────────────────┘                            │ - result (JSON)     │
                                                 └─────────────────────┘
```

---

## 2. New Entities (Phase 3)

### 2.1 Conversation

**Purpose**: Represents a chat session between a user and the AI assistant.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT `gen_random_uuid()` | Unique conversation identifier |
| `user_id` | UUID | FK → `users(id)`, NOT NULL | User who owns this conversation |
| `title` | TEXT | NULLABLE | Auto-generated summary of conversation topic |
| `created_at` | TIMESTAMP | DEFAULT `NOW()` | When conversation was created |
| `updated_at` | TIMESTAMP | DEFAULT `NOW()` | Last message timestamp |
| `is_archived` | BOOLEAN | DEFAULT `FALSE` | Soft-delete flag (7-day retention) |

**SQL Definition**:
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_conversations_is_archived ON conversations(is_archived) WHERE is_archived = FALSE;
```

**Relationships**:
- One user → many conversations
- One conversation → many messages

---

### 2.2 Message

**Purpose**: Individual message within a conversation (user or assistant).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT `gen_random_uuid()` | Unique message identifier |
| `conversation_id` | UUID | FK → `conversations(id)`, NOT NULL | Parent conversation |
| `role` | TEXT | NOT NULL, CHECK IN (`user`, `assistant`, `system`) | Who sent the message |
| `content` | TEXT | NOT NULL | Message text (can be Markdown) |
| `tool_calls` | JSONB | NULL | Array of tool calls made by assistant |
| `created_at` | TIMESTAMP | DEFAULT `NOW()` | When message was created |

**SQL Definition**:
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

**Tool Call Schema (within `tool_calls` JSONB)**:
```json
[
  {
    "id": "call_abc123",
    "tool_name": "add_task",
    "parameters": {
      "title": "Fix navbar bug",
      "priority": "HIGH",
      "project_id": 5
    },
    "result": {
      "status": "success",
      "task_id": 123
    }
  }
]
```

---

### 2.3 UserChatPreference

**Purpose**: Stores user-specific chat settings (language, voice enabled).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `user_id` | UUID | PK, FK → `users(id)` | User reference |
| `language` | TEXT | NOT NULL, DEFAULT `'en'`, CHECK IN (`en`, `ur`) | Preferred language |
| `voice_enabled` | BOOLEAN | DEFAULT `FALSE` | Whether voice input is enabled |

**SQL Definition**:
```sql
CREATE TABLE user_chat_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    language TEXT NOT NULL DEFAULT 'en' CHECK (language IN ('en', 'ur')),
    voice_enabled BOOLEAN DEFAULT FALSE
);
```

---

## 3. Existing Entities (Referenced from Phase II)

### 3.1 User

Reused from Phase II. Key fields for chat:
- `id`: UUID (references in conversations, preferences)
- `email`: User email
- `role`: RBAC role (admin, manager, member, viewer)

**RBAC Permissions for Chat**:
| Role | Can Create Tasks | Can Assign Tasks | Can Delete Tasks | Can View All Tasks |
|------|-----------------|------------------|------------------|-------------------|
| `admin` | ✅ | ✅ | ✅ | ✅ |
| `manager` | ✅ | ✅ | ✅ | ✅ (team only) |
| `member` | ✅ | ❌ | ❌ | Own only |
| `viewer` | ❌ | ❌ | ❌ | Read-only |

---

### 3.2 Task, Project, TimeEntry, etc.

All existing Phase II entities are accessible via MCP tools wrapping `TaskService`, `ProjectService`, `AnalyticsService`, etc.

---

## 4. Qdrant Vector Store (RAG)

### 4.1 Collection: `teamflow_kb`

**Purpose**: Stores embedded chunks of project documentation for semantic search.

**Configuration**:
```python
from qdrant_client.models import Distance, VectorParams, PayloadSchema

client.create_collection(
    collection_name="teamflow_kb",
    vectors_config=VectorParams(
        size=1536,  # OpenAI text-embedding-3-small dimension
        distance=Distance.COSINE
    ),
    payload_schema={
        "source": PayloadSchema.VALUE_TYPE_KEYWORD,
        "title": PayloadSchema.VALUE_TYPE_KEYWORD,
        "file_path": PayloadSchema.VALUE_TYPE_KEYWORD,
        "chunk_index": PayloadSchema.VALUE_TYPE_INTEGER,
        "last_modified": PayloadSchema.VALUE_TYPE_DATETIME
    }
)
```

**Point Structure**:
```python
PointStruct(
    id=str(uuid.uuid4()),
    vector=embedding,  # 1536-dimensional float array
    payload={
        "text": chunk_text,
        "source": "specs/001-ai-chatbot/spec.md",
        "title": "AI Chatbot Specification",
        "file_path": "/path/to/spec.md",
        "chunk_index": 3,
        "last_modified": "2025-01-06T10:00:00Z"
    }
)
```

**Documents to Ingest**:
1. `.specify/memory/constitution.md` - Project principles
2. `specs/001-ai-chatbot/spec.md` - Feature specification
3. `TEAMFLOW-PLAN.md` - Project plan and phases
4. Any project README or technical docs

**Ingestion Pipeline** (from `rag-pipeline-builder`):
1. Extract text from Markdown files
2. Split into chunks (500-1000 chars, 100-char overlap)
3. Generate embeddings via OpenAI `text-embedding-3-small`
4. Upsert to Qdrant with metadata
5. Schedule refresh on file changes

---

## 5. State Transitions

### 5.1 Conversation Lifecycle

```
[Created] → [Active] → [Archived] → [Deleted (after 7 days)]
```

**States**:
- **Created**: Initial state, no messages yet
- **Active**: At least one message exchanged
- **Archived**: User archived or 7-day threshold reached
- **Deleted**: Hard delete after retention period

---

### 5.2 Message Processing Flow

```
[User Input]
    ↓
[Agent Processing]
    ↓
[Tool Execution] ← → [MCP Tool Call]
    ↓                ↓
[Knowledge Retrieval] [Service Layer]
    ↓                ↓
[Response Generation]
    ↓
[Assistant Output]
```

---

## 6. Validation Rules

### 6.1 Conversation

| Rule | Enforcement |
|------|-------------|
| `user_id` must exist | FK constraint |
| `title` max length 200 chars | Application-level |
| One active conversation per user | Application-level (soft limit) |

---

### 6.2 Message

| Rule | Enforcement |
|------|-------------|
| `conversation_id` must exist | FK constraint |
| `role` must be valid | CHECK constraint |
| `content` min 1 char, max 10000 chars | Application-level |
| `tool_calls` valid JSON | Application-level |

---

### 6.3 UserChatPreference

| Rule | Enforcement |
|------|-------------|
| `language` must be `en` or `ur` | CHECK constraint |
| One preference per user | PK constraint |

---

## 7. Indexes & Performance

### 7.1 Query Patterns

**Primary Queries**:
1. Get conversation history for a user (ordered by updated_at)
2. Get messages for a conversation (ordered by created_at)
3. Cleanup old conversations (older than 7 days)

**Indexes**:
- `idx_conversations_user_id`: Fast user lookup
- `idx_conversations_updated_at`: Sorting for "recent chats"
- `idx_messages_conversation_id`: Message retrieval
- `idx_messages_created_at`: Chronological ordering
- `idx_conversations_is_archived`: Active conversation filter

---

### 7.2 Qdrant Queries

**Search Pattern**:
```python
# Semantic search
results = client.search(
    collection_name="teamflow_kb",
    query_vector=embedding,
    limit=5,
    score_threshold=0.7  # Cosine similarity threshold
)
```

**Optimization**:
- Payload filtering: Filter by `source` or `last_modified`
- Score threshold: Only return results with >0.7 similarity
- Limit: Top 5 results (from spec QI-003)

---

## 8. Migration Strategy

### 8.1 Schema Migration

**Migration File**: `backend/app/db/migrations/003_add_chat_tables.sql`

```sql
-- Migration: Add Phase 3 chat tables
-- Date: 2025-01-06

-- Conversations table
CREATE TABLE conversations (...);

-- Messages table
CREATE TABLE messages (...);

-- User preferences table
CREATE TABLE user_chat_preferences (...);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);

-- Cleanup job (cron)
-- DELETE FROM messages WHERE created_at < NOW() - INTERVAL '7 days';
```

---

### 8.2 Data Seeding

**Seed Initial Preferences**:
```sql
INSERT INTO user_chat_preferences (user_id, language, voice_enabled)
SELECT id, 'en', FALSE FROM users;
```

---

## 9. Retention & Cleanup

### 9.1 7-Day Retention Policy

**Scheduled Job** (runs daily):
```python
@cron.schedule(daily)
async def cleanup_old_conversations():
    cutoff = datetime.now() - timedelta(days=7)

    # Delete messages
    await db.execute(
        "DELETE FROM messages WHERE created_at < :cutoff",
        {"cutoff": cutoff}
    )

    # Delete orphaned conversations
    await db.execute(
        "DELETE FROM conversations WHERE id NOT IN (SELECT DISTINCT conversation_id FROM messages)"
    )
```

**Rationale**:
- Privacy compliance (minimize stored chat data)
- Performance (smaller tables)
- Cost (reduced storage)

---

## 10. Summary

**New Tables**: 3 (`conversations`, `messages`, `user_chat_preferences`)
**New Indexes**: 5
**Qdrant Collections**: 1 (`teamflow_kb`)
**Migration Files**: 1 (`003_add_chat_tables.sql`)

---

**Status**: ✅ Complete

All entities, relationships, and validation rules defined. Ready for API contract generation.
