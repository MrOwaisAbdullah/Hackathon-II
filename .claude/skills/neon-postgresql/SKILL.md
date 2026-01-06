---
name: neon-postgresql
description: PostgreSQL with Neon database setup and best practices. Use when setting up PostgreSQL databases, configuring SQLModel with async engines, integrating Better-Auth v1.4.x, or working with FastAPI database patterns. Covers connection pooling, migrations with Alembic, common async/sync pitfalls, and production-ready configurations. Includes reference patterns for user authentication, session management, and email verification workflows.
---

# Neon PostgreSQL Skill

Complete guide for PostgreSQL with Neon database, SQLModel, Better-Auth, and FastAPI integration.

## Quick Start

### Database Connection Setup

```python
from sqlmodel import SQLModel, create_engine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator

# SYNC engine (required for table creation)
sync_engine = create_engine(DATABASE_URL)

# ASYNC engine (for queries)
async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=0,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Critical Requirements

- **Both sync and async engines required** (sync for DDL, async for queries)
- **SSL mode required**: `DATABASE_URL` must include `sslmode=require`
- **Dependencies**: `asyncpg` (async) + `psycopg2-binary` (sync)

## Common Pitfalls

### 1. Sync/Async Mismatch

**Problem**: Using sync SQLAlchemy with async PostgreSQL driver.

```python
# WRONG - This fails
user = db.query(User).filter(User.email == email).first()

# CORRECT - Async pattern
statement = select(User).where(User.email == email.lower())
result = await db.execute(statement)
user = result.scalar_one_or_none()
```

### 2. Wrong Session Import

```python
# WRONG
from sqlmodel import AsyncSession

# CORRECT
from sqlmodel.ext.asyncio.session import AsyncSession
```

### 3. Missing Sync Engine for Migrations

Alembic migrations need sync engine. Always create both.

### 4. Enum Case Sensitivity

Database stores lowercase but enum expects capitalized.

```python
# Normalize enum values
exp_level = str(value).lower()
if exp_level == "beginner":
    enum_value = ExperienceLevel.BEGINNER
```

## SQLModel Patterns

### Model Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    full_name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    chat_sessions: List["ChatSession"] = Relationship(back_populates="user")
    user_preferences: Optional["UserPreferences"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )
```

### Query Patterns

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# Single record
statement = select(User).where(User.email == email.lower())
result = await db.execute(statement)
user = result.scalar_one_or_none()

# With relationships (avoids N+1 queries)
statement = select(User).options(
    selectinload(User.user_preferences)
).where(User.id == user_id)
result = await db.execute(statement)
user = result.scalar_one()
```

## Better-Auth Integration

### Version Note

Use **Better Auth v1.4.x** (stable), NOT v2 (beta).

### JWT Token Management

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=10080)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### Authentication Middleware

```python
from fastapi import Request
from fastapi.middleware import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def auth_middleware(request: Request, call_next):
    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, token = authorization.split()
        if scheme.lower() == "bearer":
            user = await verify_token_and_get_user(token)
            request.state.user = user
    response = await call_next(request)
    return response
```

### Current User Dependency

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    statement = select(User).where(User.id == payload.get("sub"))
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

## Database Migrations (Alembic)

### Setup

```bash
uv add alembic
cd backend
uv run alembic init alembic
```

### alembic/env.py Configuration

```python
from sqlmodel import SQLModel
from config import DATABASE_URL, sync_engine

# Set target metadata
target_metadata = SQLModel.metadata

# Use sync engine for migrations
engine = sync_engine
```

### Migration Commands

```bash
# Generate migration
uv run alembic revision --autogenerate -m "Initial schema"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

## Environment Configuration

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@host/dbname?sslmode=require

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Email (for verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourapp.com

# Frontend
FRONTEND_URL=http://localhost:3000
```

## FastAPI Application Setup

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="API Backend",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth.router, prefix="/api/v1")
```

## Testing Database Connection

```bash
# Connect using psql
psql postgresql://username:password@host/dbname

# Verify tables
\dt

# Check relationships
SELECT u.full_name, up.theme FROM users u
LEFT JOIN user_preferences up ON u.id = up.user_id;

# Verify indexes
\di
```

## Performance Optimizations

- **Connection Pool Tuning**: Set `pool_size` based on concurrent connections
- **Statement Cache**: Enable in production for better performance
- **Use selectinload**: Avoid N+1 queries with relationships
- **Index Strategy**: Index frequently queried fields (email, user_id)
- **pool_pre_ping**: Detect and recycle stale connections

## Security Best Practices

1. **SSL Required**: All connections use `sslmode=require`
2. **Environment Variables**: Never commit credentials
3. **SQL Injection Prevention**: SQLModel parameterized queries
4. **Password Hashing**: Use bcrypt with passlib
5. **Token Expiry**: 7-day maximum for access tokens
6. **Rate Limiting**: Apply to auth endpoints

---

## Common Deployment Issues

### Issue 1: "Connection refused" to localhost

**Error Message:**
```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

**Cause**: `DATABASE_URL` environment variable is not set or defaults to `localhost`. Application is using the default value from config instead of the actual Neon database URL.

**Solution**: Set `DATABASE_URL` in deployment platform environment variables:

**HuggingFace Spaces:**
1. Go to Space Settings > Variables
2. Add: `DATABASE_URL = postgresql://user:pass@ep-xxx.aws.neon.tech/dbname?sslmode=require`
3. Click Save
4. Restart the Space

**Vercel:**
1. Go to Project Settings > Environment Variables
2. Add: `DATABASE_URL` with your Neon connection string
3. Redeploy

**Environment Variable Format:**
```env
# CORRECT - Full Neon connection string with SSL
DATABASE_URL=postgresql://username:password@ep-cool-name.us-east-2.aws.neon.tech/teamflow?sslmode=require

# WRONG - Missing SSL mode (will fail in production)
DATABASE_URL=postgresql://username:password@ep-cool-name.us-east-2.aws.neon.tech/teamflow

# WRONG - Localhost (default fallback, will fail)
DATABASE_URL=postgresql://user:pass@localhost:5432/teamflow
```

### Issue 2: "No module named 'psycopg2'"

**Cause**: Missing sync PostgreSQL driver. Async engines use `asyncpg`, but some operations (migrations, table creation) need sync driver.

**Solution:**
```bash
# Add both drivers
uv add asyncpg psycopg2-binary
```

### Issue 3: Connection pool exhaustion

**Error Message:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection is closed
```

**Cause**: Neon free tier closes idle connections after 5 minutes. Pool giving stale connections.

**Solution**: Configure engine with proper pool settings:
```python
async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    pool_pre_ping=True,  # CRITICAL: Verify connections before use
    pool_recycle=1800,   # 30 min (Neon idle timeout is 5 min)
    pool_size=3,         # Smaller for async
    max_overflow=5,
    pool_use_lifo=True,  # Use most recent connections first
)
```

### Issue 4: Alembic migrations fail with async driver

**Error Message:**
```
sqlalchemy.exc.MovedIn20Error: The 'asyncpg' dialect is not supported in Alembic migrations
```

**Cause**: Alembic requires sync engine for migrations, async engines don't work.

**Solution**: Create separate sync engine:
```python
# For Alembic migrations
sync_engine = create_engine(DATABASE_URL)  # NOT asyncpg!

# For queries
async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
)
```

### Issue 5: Database URL validation fails

**Error Message:**
```
ValueError: Database URL must use postgresql:// scheme
```

**Cause**: Connection string uses wrong protocol or missing prefix.

**Solution**: Ensure proper URL format:
```env
# Must start with postgresql://
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require

# NOT postgres:// or pg://
```

### Environment Variables Checklist

Before deploying, ensure these are set:

| Variable | Required? | Format | Example |
|----------|-----------|--------|---------|
| `DATABASE_URL` | ✅ Yes | `postgresql://...?sslmode=require` | Neon connection string |
| `SECRET_KEY` | ✅ Yes | 32+ char random string | Use `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | ✅ Yes | 32+ char random string | Same as SECRET_KEY or separate |
| `ENVIRONMENT` | ⚪ No | `production` or `development` | Defaults to `development` |
| `FRONTEND_URL` | ⚪ No | Comma-separated URLs | `https://yourapp.vercel.app` |

### Quick Verification Commands

```bash
# Test connection from local machine
psql $DATABASE_URL -c "SELECT 1;"

# Check if environment variable is set
echo $DATABASE_URL

# Verify SSL mode in connection string
echo $DATABASE_URL | grep sslmode
```

## References

For advanced patterns and specific scenarios, see:

- [references/async-patterns.md](references/async-patterns.md) - Deep async/sync patterns
- [references/relationships.md](references/relationships.md) - Relationship management
- [references/migration-patterns.md](references/migration-patterns.md) - Alembic workflows
- [references/security.md](references/security.md) - Security hardening
