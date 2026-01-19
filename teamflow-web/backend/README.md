---
title: TeamFlow Backend API
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: "3.13"
app_file: app/main.py
app_port: 7860
pinned: false
license: mit
---

# TeamFlow Backend API

FastAPI backend with async/await, multi-tenancy, MCP server, and RAG pipeline for AI-powered agency management.

---

## Overview

TeamFlow Backend is a production-ready FastAPI application built for creative agencies. It features a multi-tenant architecture, MCP server for AI tool integration, RAG pipeline with Qdrant, and comprehensive task/project/time management.

**Key Capabilities:**
- Multi-tenant agency isolation with JWT auth
- 21 MCP tools for AI agent integration
- RAG pipeline with Qdrant vector DB
- Async/await for high performance
- OpenAPI/Swagger documentation
- HuggingFace Spaces deployment ready

---

## Tech Stack

```yaml
Framework: FastAPI 0.115+
Language: Python 3.13+
ORM: SQLModel (SQLAlchemy 2.0 async)
Database: PostgreSQL (Neon Serverless)
Auth: JWT tokens (agency-scoped)
AI: OpenAI Agents SDK, OpenRouter, GPT-5 fallback
Vector DB: Qdrant (for RAG)
MCP: FastMCP server framework
Testing: Pytest
Deployment: Docker (HuggingFace Spaces)
```

---

## Architecture Highlights

### Multi-Tenancy

```python
# Agency-scoped data isolation
class Agency(BaseModel):
    id: str
    name: str

class User(BaseModel):
    agency_id: str  # All queries filtered by agency
    role: Literal["admin", "member", "viewer"]

# JWT includes agency_id
token = encode({"sub": user_id, "agency_id": agency_id})
```

**Features:**
- All queries automatically filtered by `agency_id`
- Separate admin/member/viewer roles
- Agency-scoped sessions
- Data isolation guarantees

### MCP Server

```python
# Mounted at /mcp endpoint
# 21 tools for AI agent integration
from app.chatkit.server import mcp_app

app.mount("/mcp", mcp_app)
```

**Tools:**
- Task Management (4 tools)
- Project Management (3 tools)
- Time Tracking (5 tools)
- Analytics (2 tools)
- AI Features (1 tool)
- RAG Search (1 tool)

### RAG Pipeline

```python
# Qdrant vector database for semantic search
from app.services.rag import search_knowledge_base

results = search_knowledge_base("project deadlines")
# Returns contextually relevant documents
```

**Features:**
- Semantic search over documentation
- Context-aware AI responses
- Knowledge base integration
- Vector embeddings with OpenAI

---

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                    # Dependencies (auth, session)
│   │   └── endpoints/
│   │       ├── auth.py                # Login, register, token refresh
│   │       ├── tasks.py               # Task CRUD operations
│   │       ├── projects.py            # Project management
│   │       ├── time_entries.py        # Time tracking
│   │       ├── analytics.py           # Dashboard stats
│   │       └── users.py               # User management
│   │
│   ├── chatkit/
│   │   ├── server.py                  # MCP server setup (21 tools)
│   │   └── tools/
│   │       ├── tasks.py               # Task MCP tools
│   │       ├── projects.py            # Project MCP tools
│   │       ├── time_entries.py        # Time tracking tools
│   │       └── analytics.py           # Analytics tools
│   │
│   ├── core/
│   │   ├── config.py                  # Environment configuration
│   │   ├── security.py                # JWT, password hashing
│   │   └── logging.py                 # Structured logging
│   │
│   ├── models/
│   │   ├── agency.py                  # Agency model
│   │   ├── user.py                    # User model
│   │   ├── project.py                 # Project model
│   │   ├── task.py                    # Task model
│   │   ├── time_entry.py              # Time entry model
│   │   ├── conversation.py            # Chat conversations
│   │   └── message.py                 # Chat messages
│   │
│   ├── services/
│   │   ├── auth_service.py            # Authentication logic
│   │   ├── task_service.py            # Task business logic
│   │   ├── project_service.py         # Project logic
│   │   ├── analytics_service.py       # Dashboard analytics
│   │   └── rag_service.py             # RAG pipeline
│   │
│   ├── db/
│   │   └── session.py                 # Async database session
│   │
│   └── main.py                        # FastAPI app entry point
│
├── alembic/
│   ├── versions/                      # Migration files
│   └── env.py                         # Alembic configuration
│
├── tests/
│   ├── test_auth.py                   # Auth tests
│   ├── test_tasks.py                  # Task tests
│   ├── test_projects.py               # Project tests
│   └── conftest.py                    # Pytest fixtures
│
├── Dockerfile                         # HuggingFace deployment
├── pyproject.toml                     # Python project config
└── .env.example                       # Environment template
```

---

## Database Schema

```sql
-- Agencies (multi-tenant root)
CREATE TABLE agencies (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users (agency-scoped)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    agency_id UUID REFERENCES agencies(id),
    role VARCHAR(20) NOT NULL, -- admin, member, viewer
    active BOOLEAN DEFAULT TRUE
);

-- Projects (agency-scoped)
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL, -- active, on_hold, completed, archived
    agency_id UUID REFERENCES agencies(id)
);

-- Tasks (agency-scoped)
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL, -- todo, in_progress, in_review, done
    priority VARCHAR(10), -- high, medium, low
    assignee_id UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    agency_id UUID REFERENCES agencies(id),
    due_date TIMESTAMP
);

-- Time Entries (agency-scoped)
CREATE TABLE time_entries (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    user_id UUID REFERENCES users(id),
    duration_minutes INT NOT NULL,
    billable BOOLEAN DEFAULT FALSE,
    description TEXT,
    agency_id UUID REFERENCES agencies(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations (chat history)
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    agency_id UUID REFERENCES agencies(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Messages (chat messages with tool calls)
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT,
    tool_calls JSONB, -- MCP tool invocations
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Development Setup

### Prerequisites

- Python 3.13+
- PostgreSQL database (or Neon free tier)
- Virtual environment tool (venv, uv, or conda)

### Installation

```bash
# Navigate to backend directory
cd teamflow-web/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Or use uv (faster)
uv pip install -e ".[dev]"
```

### Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

```env
# Required
DATABASE_URL=postgresql://user:pass@ep-xyz.aws.neon.tech/teamflow?sslmode=require
SECRET_KEY=your-super-secret-jwt-key-at-least-32-characters-long

# AI Features
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...

# Optional
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000

# Vector DB (Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Optional, for cloud Qdrant

# Logging
LOG_LEVEL=INFO
```

### Database Migrations

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the CLI
python -m app.main
```

**API Endpoints:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health Check: http://localhost:8000/health

---

## MCP Tools

### Task Management (4 tools)

```python
@app.mcp_tool()
async def create_task(title: str, assignee_id: str, ...) -> Task:
    """Create a new task and assign it to a team member."""

@app.mcp_tool()
async def list_tasks(status: str | None = None, ...) -> list[Task]:
    """List all tasks with optional filtering."""

@app.mcp_tool()
async def update_task(task_id: str, ...) -> Task:
    """Update an existing task."""

@app.mcp_tool()
async def delete_task(task_id: str) -> bool:
    """Delete a task by ID."""
```

### Project Management (3 tools)

```python
@app.mcp_tool()
async def create_project(name: str, description: str) -> Project:
    """Create a new project."""

@app.mcp_tool()
async def list_projects(status: str | None = None) -> list[Project]:
    """List all projects with optional filtering."""

@app.mcp_tool()
async def update_project(project_id: str, ...) -> Project:
    """Update an existing project."""
```

### Time Tracking (5 tools)

```python
@app.mcp_tool()
async def create_time_entry(task_id: str, duration: int, ...) -> TimeEntry:
    """Log time spent on a task."""

@app.mcp_tool()
async def list_time_entries(task_id: str | None = None) -> list[TimeEntry]:
    """List time entries with optional filtering."""

@app.mcp_tool()
async def get_task_time(task_id: str) -> dict:
    """Get total time logged for a task."""

@app.mcp_tool()
async def update_time_entry(entry_id: str, ...) -> TimeEntry:
    """Update a time entry."""

@app.mcp_tool()
async def delete_time_entry(entry_id: str) -> bool:
    """Delete a time entry."""
```

### Analytics (2 tools)

```python
@app.mcp_tool()
async def get_dashboard_stats() -> dict:
    """Get dashboard statistics (tasks, projects, time)."""

@app.mcp_tool()
async def get_team_workload() -> list[dict]:
    """Get workload distribution across team members."""
```

### AI Features (1 tool)

```python
@app.mcp_tool()
async def recommend_assignee(task_title: str, task_description: str) -> User:
    """AI-powered task assignment recommendation."""
```

### RAG Search (1 tool)

```python
@app.mcp_tool()
async def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    """Semantic search over project documentation."""
```

---

## API Documentation

### Authentication

All endpoints (except `/auth/login` and `/auth/register`) require JWT authentication:

```bash
# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { ... }
}

# Use token in subsequent requests
Authorization: Bearer eyj...
```

### Task Endpoints

```bash
# List tasks
GET /api/v1/tasks?status=todo&assignee_id=xxx

# Create task
POST /api/v1/tasks
{
  "title": "Fix bug",
  "description": "...",
  "status": "todo",
  "priority": "high",
  "assignee_id": "xxx",
  "project_id": "yyy"
}

# Update task
PATCH /api/v1/tasks/{task_id}

# Delete task
DELETE /api/v1/tasks/{task_id}
```

### Project Endpoints

```bash
# List projects
GET /api/v1/projects?status=active

# Create project
POST /api/v1/projects
{
  "name": "Website Redesign",
  "description": "...",
  "status": "active"
}

# Update project
PATCH /api/v1/projects/{project_id}
```

### Analytics Endpoints

```bash
# Dashboard stats
GET /api/v1/analytics/dashboard

# Team workload
GET /api/v1/analytics/team-workload
```

---

## Testing

### Run All Tests

```bash
# Using pytest
pytest

# With coverage
pytest --cov=app --cov-report=html

# With verbose output
pytest -v

# Run specific test file
pytest tests/test_tasks.py

# Run specific test
pytest tests/test_tasks.py::test_create_task
```

### Example Test

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_task(authenticated_client: AsyncClient):
    response = await authenticated_client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "status": "todo",
            "priority": "high"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
```

### Test Fixtures

```python
# conftest.py
@pytest.fixture
async def authenticated_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Login and set token
        response = await client.post("/api/v1/auth/login", json={...})
        token = response.json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client
```

---

## Deployment

### HuggingFace Spaces (Recommended)

1. **Create Space:**
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Create new Space → Docker SDK
   - Clone: `git clone https://huggingface.co/spaces/your-username/teamflow-backend`

2. **Configure Environment:**
   - Go to Space Settings → Variables
   - Add secrets:
     - `DATABASE_URL`
     - `SECRET_KEY`
     - `OPENAI_API_KEY`
     - `OPENROUTER_API_KEY`

3. **Deploy:**
   ```bash
   git remote add hf https://huggingface.co/spaces/your-username/teamflow-backend
   git push hf main
   ```

4. **Verify:**
   - Visit: `https://huggingface.co/spaces/your-username/teamflow-backend`
   - Health check: `{space_url}/health`

### Docker Deployment

```bash
# Build image
docker build -t teamflow-backend .

# Run container
docker run -d \
  -p 8000:7860 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="your-secret" \
  -e OPENAI_API_KEY="sk-..." \
  --name teamflow-api \
  teamflow-backend
```

### Production Checklist

- [ ] Set `DATABASE_URL` to Neon production
- [ ] Set `SECRET_KEY` to strong random value (32+ chars)
- [ ] Set `OPENAI_API_KEY` for AI features
- [ ] Set `ENVIRONMENT=production`
- [ ] Run Alembic migrations: `alembic upgrade head`
- [ ] Enable CORS for frontend domain
- [ ] Configure rate limiting
- [ ] Set up logging/monitoring
- [ ] Configure backup strategy
- [ ] Test health check endpoint

---

## Troubleshooting

### Connection Refused

**Error:** `psycopg2.OperationalError: could not connect`

**Solution:**
- Check `DATABASE_URL` format (must include `?sslmode=require` for Neon)
- Verify database is accessible
- Check firewall/network settings

### 429 Rate Limit

**Error:** `RateLimitError: Rate limit exceeded`

**Solution:**
- Automatic fallback to OpenAI is enabled
- Increase timeout in MCP server config
- Use OpenAI API key directly for higher limits

### MCP Timeout

**Error:** `TimeoutError: MCP tool execution timeout`

**Solution:**
```python
# Increase timeout in app/chatkit/server.py
mcp_app = FastMCP(
    "teamflow",
    timeout=30.0,  # Increase from default
)
```

### Alembic Downgrade

**Command:** Rollback one migration

```bash
alembic downgrade -1
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

---

## Performance Optimization

### Database Queries

```python
# Use selectinload for relationships
from sqlalchemy.orm import selectinload

result = await session.exec(
    select(Task)
    .options(selectinload(Task.assignee))
    .where(Task.agency_id == agency_id)
)
```

### Async Operations

```python
# Use async/await for I/O operations
async def get_tasks():
    # Database query
    tasks = await session.exec(select(Task))
    # External API call
    analytics = await httpx.get_async("https://api.example.com")
    return tasks, analytics
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_agency_config(agency_id: str):
    # Cache frequently accessed config
    return fetch_agency_config(agency_id)
```

---

## Security Best Practices

### JWT Secrets

```python
# Generate strong secret key
import secrets
SECRET_KEY = secrets.token_urlsafe(32)  # 32+ chars
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd_context.hash(password)
verified = pwd_context.verify(plain_password, hashed)
```

### Agency Isolation

```python
# All queries MUST filter by agency_id
async def get_tasks(agency_id: str):
    return await session.exec(
        select(Task).where(Task.agency_id == agency_id)
    )
```

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    priority: Literal["high", "medium", "low"]

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

---

## Related Documentation

- [Root README](../../README.md) - Overall project overview
- [Frontend README](../frontend/README.md) - Frontend documentation
- [Phase 2 Spec](../../specs/002-fullstack-web-crm/) - Backend API specifications
- [Phase 3 Spec](../../specs/001-ai-chatbot/) - AI/MCP integration specs

---

## License

MIT © 2025 Owais Abdullah

---

**Built with FastAPI, SQLModel, and modern Python technologies**
