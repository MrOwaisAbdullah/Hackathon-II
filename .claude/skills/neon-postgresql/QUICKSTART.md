# Quick Start Guide

Get your PostgreSQL database with Neon up and running in 15 minutes.

## Prerequisites

- Python 3.11+
- PostgreSQL account (get free at [neon.tech](https://neon.tech))
- Resend account for emails (optional, get free at [resend.com](https://resend.com))

## Step 1: Project Setup (2 minutes)

```bash
# Create project directory
mkdir myapp && cd myapp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi sqlmodel psycopg2-binary asyncpg alembic resend pydantic-settings
```

## Step 2: Environment Configuration (3 minutes)

### Create `.env` file:

```bash
# === DATABASE ===
# Local development
DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb?sslmode=disable

# Production (Neon)
# DATABASE_URL=postgresql://username:password@ep-xyz.aws.neon.tech/mydb?sslmode=require

# === EMAIL (Resend) ===
# Get API key from: https://resend.com/api-keys
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=noreply@yourdomain.com
RESEND_FROM_NAME="Your App Name"

# === JWT ===
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# === CORS ===
FRONTEND_URL=http://localhost:3000
```

## Step 3: Database Connection Code (5 minutes)

Create `database.py`:

```python
from sqlmodel import SQLModel, create_engine, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    RESEND_API_KEY: str
    FRONTEND_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

# SYNC engine (required for table creation)
sync_engine = create_engine(settings.DATABASE_URL)

# ASYNC engine (for queries)
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
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

## Step 4: Define Models (3 minutes)

Create `models/user.py`:

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    hashed_password: str
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Step 5: Initialize Database (2 minutes)

Run this initialization script:

```bash
python -c "
from database import sync_engine, SQLModel
from models.user import User
SQLModel.metadata.create_all(sync_engine)
print('✓ Database initialized')
"
```

Or use the skill's built-in script:
```bash
python .claude/skills/neon-postgresql/scripts/init_db.py
```

## Step 6: Email Setup (Optional - 5 minutes)

### Get Resend API Key:

1. Go to [resend.com](https://resend.com) and sign up
2. Navigate to **API Keys**
3. Create new API key and save it (shown only once!)

### Add Domain & Verify DNS:

1. In Resend dashboard, add your domain
2. Add these DNS records to your domain provider:

```
Type: TXT
Name: _dmarc
Value: "v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com"

Type: TXT
Name: send
Value: "v=spf1 include:resend.com ~all"

Type: CNAME
Name: resend1._domainkey
Value: resend1._domainkey.yourdomain.com.resend.com
```

3. Wait 5-30 minutes for DNS propagation
4. Click "Verify" in Resend dashboard

### Create Email Service:

Create `services/email.py`:

```python
import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_verification_email(email: str, verification_url: str):
    params = {
        "from": f"MyApp <noreply@yourdomain.com>",
        "to": [email],
        "subject": "Verify Your Email",
        "html": f"""
            <p>Click the link below to verify:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
        """,
    }
    try:
        email = resend.Emails.send(params)
        return {"success": True, "email_id": email["id"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Step 7: Test Everything (2 minutes)

Create `test.py`:

```python
import asyncio
from database import async_engine
from sqlalchemy import text

async def test():
    # Test database connection
    async with async_engine.begin() as conn:
        result = await conn.execute(text("SELECT version()"))
        print(f"✓ Database connected: {result.scalar()}")

    # Test email (Resend)
    # During development, use test addresses: test@resend.dev
    result = send_verification_email(
        "test@resend.dev",
        "https://yourapp.com/verify?token=abc123"
    )
    print(f"✓ Email sent: {result}")

asyncio.run(test())
```

## Step 8: Common Issues & Solutions

### Issue: "SSL error: sslmode=require"

**Local Development:**
```bash
# Add ?sslmode=disable to your DATABASE_URL
DATABASE_URL=postgresql://user:pass@localhost:5432/db?sslmode=disable
```

**Production:**
```bash
# Use ?sslmode=require (default for Neon)
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
```

### Issue: "ImportError: cannot import name 'AsyncSession'"

```python
# WRONG
from sqlmodel import AsyncSession

# CORRECT
from sqlmodel.ext.asyncio.session import AsyncSession
```

### Issue: Email not delivered in production

**Checklist:**
- [ ] Domain verified in Resend dashboard?
- [ ] DNS records properly configured?
- [ ] SPF/DKIM records correct?
- [ ] `from` email domain matches verified domain?
- [ ] Check Resend dashboard logs

### Issue: "ModuleNotFoundError: No module named 'resend'"

```bash
pip install resend
```

## Production Deployment Checklist

### Database:
- [ ] Change `DATABASE_URL` to production Neon URL
- [ ] Set `sslmode=require`
- [ ] Verify connection pooling settings
- [ ] Test connection before deploying

### Authentication:
- [ ] Generate secure `JWT_SECRET_KEY` (32+ characters)
- [ ] Set appropriate token expiry
- [ ] Enable HTTPS only
- [ ] Remove any test users/data

### Email:
- [ ] Add production domain in Resend
- [ ] Configure DNS records (SPF, DKIM, DMARC)
- [ ] Verify domain in Resend dashboard
- [ ] Update `RESEND_FROM_EMAIL` to production domain
- [ ] Test email delivery
- [ ] Set up webhook for bounce handling

### Security:
- [ ] All environment variables set
- [ ] `.env` file in `.gitignore`
- [ ] CORS configured for production domain
- [ ] Rate limiting enabled
- [ ] Password hashing implemented

## Next Steps

1. **Set up Alembic migrations:**
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head
   ```

2. **Create authentication endpoints:**
   - POST `/api/v1/auth/register`
   - POST `/api/v1/auth/login`
   - POST `/api/v1/auth/verify-email`
   - POST `/api/v1/auth/forgot-password`

3. **Add connection pooling for production:**
   - Monitor connection usage
   - Adjust `pool_size` based on load
   - Enable `pool_pre_ping` for stale connections

## Need Help?

- **Database issues:** Check `scripts/test_db.py`
- **Migration issues:** Check `scripts/migrate.py`
- **Email issues:** Check Resend dashboard logs

## Reference

For detailed patterns and advanced topics, see:
- [references/async-patterns.md](references/async-patterns.md) - Async/sync patterns
- [references/relationships.md](references/relationships.md) - Database relationships
- [references/migration-patterns.md](references/migration-patterns.md) - Migrations
- [references/security.md](references/security.md) - Security best practices
- [references/email-setup.md](references/email-setup.md) - Complete email integration guide
