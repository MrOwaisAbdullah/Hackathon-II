# Async/Sync Patterns

Deep dive into async and sync patterns with SQLModel and PostgreSQL.

## The Dual-Engine Architecture

### Why Both Engines Are Required

SQLModel/SQLAlchemy requires a **synchronous engine** for DDL operations (table creation, schema modifications) even when using async for queries.

```python
from sqlmodel import create_engine, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

# SYNC engine - ONLY for table creation
sync_engine = create_engine(DATABASE_URL)

# ASYNC engine - for all queries
async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### When to Use Each

| Operation | Engine Type | Example |
|-----------|-------------|---------|
| Create tables | Sync | `SQLModel.metadata.create_all(sync_engine)` |
| Run migrations | Sync | Alembic uses sync engine |
| Query data | Async | `await db.execute(statement)` |
| Insert records | Async | `db.add(model); await db.commit()` |
| Update records | Async | `await db.refresh(model)` |

## Async Query Patterns

### Basic CRUD Operations

```python
from sqlmodel import select, delete, update
from sqlalchemy.orm import selectinload

# CREATE
async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    db_user = User.from_orm(user_data)  # or User(**user_data.dict())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# READ - Single record
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email.lower())
    result = await db.execute(statement)
    return result.scalar_one_or_none()

# READ - Multiple records
async def get_users(db: AsyncSession, offset: int, limit: int) -> List[User]:
    statement = select(User).offset(offset).limit(limit)
    result = await db.execute(statement)
    return result.scalars().all()

# UPDATE
async def update_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# DELETE
async def delete_user(db: AsyncSession, user_id: int) -> bool:
    statement = delete(User).where(User.id == user_id)
    result = await db.execute(statement)
    await db.commit()
    return result.rowcount > 0
```

### Queries with Relationships

```python
# Eager loading to avoid N+1 queries
statement = select(User).options(
    selectinload(User.user_preferences),
    selectinload(User.chat_sessions)
).where(User.id == user_id)

result = await db.execute(statement)
user = result.scalar_one()
```

### Complex Queries

```python
from sqlmodel import and_, or_

# Multiple conditions
statement = select(User).where(
    and_(
        User.is_verified == True,
        User.created_at >= datetime(2025, 1, 1)
    )
)

# OR conditions
statement = select(User).where(
    or_(
        User.email.like("%@gmail.com"),
        User.email.like("%@yahoo.com")
    )
)

# JOIN queries
statement = select(User, UserPreferences).join(
    UserPreferences,
    User.id == UserPreferences.user_id
).where(
    UserPreferences.theme == "dark"
)

result = await db.execute(statement)
for row in result:
    user, prefs = row
```

## Session Management

### Proper Dependency Pattern

```python
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Transaction Management

```python
async def transfer_credits(
    db: AsyncSession,
    from_user: int,
    to_user: int,
    amount: int
) -> bool:
    try:
        # Get users with row lock
        statement = select(User).where(
            User.id.in_([from_user, to_user])
        ).with_for_update()
        result = await db.execute(statement)
        users = {u.id: u for u in result.scalars()}

        # Check balance
        if users[from_user].credits < amount:
            raise ValueError("Insufficient credits")

        # Transfer
        users[from_user].credits -= amount
        users[to_user].credits += amount

        await db.commit()
        return True
    except Exception:
        await db.rollback()
        return False
```

## Common Async Pitfalls

### 1. Forgetting await

```python
# WRONG - Result is coroutine, not data
result = db.execute(statement)
users = result.scalars().all()  # This fails!

# CORRECT - await the execute
result = await db.execute(statement)
users = result.scalars().all()
```

### 2. Using sync methods with async engine

```python
# WRONG - session.exec() is sync only
user = db.exec(select(User).where(User.id == 1)).first()

# CORRECT - use execute with await
result = await db.execute(select(User).where(User.id == 1))
user = result.scalar_one_or_none()
```

### 3. Not closing sessions

```python
# WRONG - Session stays open
async def get_user():
    session = AsyncSessionLocal()
    result = await session.execute(select(User))
    return result.scalar_one()

# CORRECT - Use context manager
async def get_user():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalar_one()
```

## Performance Considerations

### Connection Pool Configuration

```python
async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    future=True,
    pool_pre_ping=True,        # Test connections before use
    pool_recycle=300,          # Recycle after 5 minutes
    pool_size=20,              # Max concurrent connections
    max_overflow=0,            # No extra connections
)
```

### Batch Operations

```python
# Insert multiple records efficiently
async def create_users_batch(db: AsyncSession, users_data: List[dict]):
    users = [User(**data) for data in users_data]
    db.add_all(users)
    await db.commit()

# Bulk insert (faster for large datasets)
from sqlalchemy import insert

async def bulk_insert_users(db: AsyncSession, users_data: List[dict]):
    statement = insert(User).values(users_data)
    await db.execute(statement)
    await db.commit()
```

### Query Optimization

```python
# Select only needed columns
from sqlmodel import col

statement = select(User.id, User.email, User.full_name)

# Count without fetching data
statement = select(func.count(User.id)).where(User.is_verified == True)
result = await db.execute(statement)
count = result.scalar()
```

## Testing Async Code

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
```
