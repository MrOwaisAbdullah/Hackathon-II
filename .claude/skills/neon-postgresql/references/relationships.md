# Relationships in SQLModel

Comprehensive guide for managing database relationships with SQLModel.

## Relationship Types

### One-to-One

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)

    # One-to-one: uselist=False
    user_preferences: Optional["UserPreferences"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )

class UserPreferences(SQLModel, table=True):
    __tablename__ = "user_preferences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    theme: str = Field(default="light")
    language: str = Field(default="en")

    # Back reference
    user: User = Relationship(back_populates="user_preferences")
```

### One-to-Many

```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str

    # One-to-many: List of related objects
    chat_sessions: List["ChatSession"] = Relationship(back_populates="user")

class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Many-to-one: Single user
    user: User = Relationship(back_populates="chat_sessions")
```

### Many-to-Many

```python
# Association table (explicit model for many-to-many)
class UserGroupLink(SQLModel, table=True):
    __tablename__ = "user_group_links"

    user_id: int = Field(foreign_key="users.id", primary_key=True)
    group_id: int = Field(foreign_key="groups.id", primary_key=True)

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str

    # Many-to-many: Link through association table
    groups: List["Group"] = Relationship(
        back_populates="users",
        link_model=UserGroupLink
    )

class Group(SQLModel, table=True):
    __tablename__ = "groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    users: List["User"] = Relationship(
        back_populates="groups",
        link_model=UserGroupLink
    )
```

## Querying with Relationships

### Eager Loading (Avoid N+1 Queries)

```python
from sqlalchemy.orm import selectinload, joinedload

# selectinload - Separate queries, good for to-many
statement = select(User).options(
    selectinload(User.chat_sessions)
).where(User.id == user_id)

# joinedload - JOIN query, good for to-one
statement = select(User).options(
    joinedload(User.user_preferences)
).where(User.id == user_id)

# Multiple relationships
statement = select(User).options(
    selectinload(User.chat_sessions),
    joinedload(User.user_preferences)
)
```

### Filtering on Relationships

```python
# Has relationship (exists)
from sqlalchemy import exists

statement = select(User).where(
    exists().where(ChatSession.user_id == User.id)
)

# Join and filter
statement = select(User).join(ChatSession).where(
    ChatSession.title.like("%important%")
)

# Any (for relationships)
statement = select(User).where(
    User.chat_sessions.any(ChatSession.title == "Important")
)
```

### Creating with Relationships

```python
# Create parent with children
async def create_user_with_sessions(db: AsyncSession):
    user = User(email="user@example.com")
    user.chat_sessions = [
        ChatSession(title="Session 1"),
        ChatSession(title="Session 2"),
    ]
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

## Cascading Operations

```python
from sqlalchemy import ForeignKey, Cascade

class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE"  # Delete sessions when user is deleted
    )

    # Or in relationship definition
    user: User = Relationship(
        back_populates="chat_sessions",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        }
    )
```

## Common Relationship Issues

### 1. LazyLoadingError

```python
# Problem: Accessing relationship after session closes
async def get_user_bad(db: AsyncSession, user_id: int):
    statement = select(User).where(User.id == user_id)
    result = await db.execute(statement)
    user = result.scalar_one()
    await db.close()
    return user.chat_sessions  # ERROR: Session is closed!

# Solution: Eager load the relationship
async def get_user_good(db: AsyncSession, user_id: int):
    statement = select(User).options(
        selectinload(User.chat_sessions)
    ).where(User.id == user_id)
    result = await db.execute(statement)
    user = result.scalar_one()
    return user.chat_sessions  # Works!
```

### 2. Circular Imports

```python
# models/__init__.py
from .user import User
from .chat_session import ChatSession
from .user_preferences import UserPreferences

__all__ = ["User", "ChatSession", "UserPreferences"]

# Use TYPE_CHECKING to avoid circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
```

### 3. Missing Back References

```python
# Problem: One-sided relationship
class User(SQLModel, table=True):
    sessions: List["ChatSession"] = Relationship()  # No back_populates!

# Solution: Always define both sides
class User(SQLModel, table=True):
    sessions: List["ChatSession"] = Relationship(
        back_populates="user"
    )

class ChatSession(SQLModel, table=True):
    user_id: int = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="sessions")
```

## Self-Referencing Relationships

```python
class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    parent_id: Optional[int] = Field(
        default=None,
        foreign_key="comments.id"
    )

    # Self-referencing: Replies to this comment
    replies: List["Comment"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "foreign_keys": "[Comment.parent_id]"
        }
    )

    # Parent comment
    parent: Optional["Comment"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={
            "remote_side": "[Comment.id]"
        }
    )
```

## Advanced Patterns

### Polymorphic Relationships

```python
class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    content_type: str  # "message", "post", etc.
    content_id: int    # ID of the related object

# Query with polymorphic relationship
statement = select(Notification).where(
    and_(
        Notification.content_type == "message",
        Notification.content_id == message_id
    )
)
```

### Dynamic Relationships

```python
# For models with configurable relationships
from sqlalchemy.ext.associationproxy import association_proxy

class User(SQLModel, table=True):
    # Direct relationship
    user_preferences: Optional["UserPreferences"] = Relationship()

    # Proxy attribute for convenience
    theme: str = association_proxy(
        "user_preferences",
        "theme"
    )
```
