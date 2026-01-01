# Security Hardening

Security best practices for PostgreSQL, Neon, SQLModel, and FastAPI authentication.

## Database Security

### SSL/TLS Configuration

**Always use SSL for production connections:**

```env
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
```

Available SSL modes:
- `disable` - No SSL (never use in production)
- `allow` - Try SSL, allow non-SSL
- `prefer` - Try SSL, allow non-SSL (default)
- `require` - Require SSL (recommended)
- `verify-ca` - Require SSL + verify certificate
- `verify-full` - Require SSL + verify certificate + hostname

### Connection String Security

**Never commit credentials:**

```python
# WRONG - Hardcoded
DATABASE_URL = "postgresql://user:password@host/dbname"

# CORRECT - Environment variable
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

settings = Settings()
DATABASE_URL = settings.DATABASE_URL
```

### Row-Level Security

Create user-specific data isolation:

```sql
-- Enable RLS
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY user_isolation ON sensitive_data
    FOR ALL
    TO app_user
    USING (user_id = current_user_id());
```

## Password Security

### Bcrypt Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Password Requirements

```python
import re
from pydantic import validator, field_validator

class PasswordCreate:
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain digit")
        return v
```

### Password Reset Flow

```python
import secrets
from datetime import datetime, timedelta

def generate_reset_token() -> str:
    """Generate secure token for password reset."""
    return secrets.token_urlsafe(32)

def is_reset_token_valid(expiry: datetime) -> bool:
    """Check if reset token is still valid (1 hour expiry)."""
    return datetime.utcnow() < expiry
```

## JWT Token Security

### Token Configuration

```python
from datetime import timedelta

# Production settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # Minimum 32 characters
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080  # 7 days max recommended

# For shorter sessions (mobile apps)
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
```

### Token Generation

```python
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    # Add expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Add issued at time for detection
    to_encode.update({"iat": datetime.utcnow()})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### Token Validation

```python
def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check expiration manually for more control
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            return None

        return payload
    except JWTError:
        return None
```

## API Security

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Prevent brute force
async def login(credentials: UserLogin):
    pass

@app.post("/api/v1/auth/register")
@limiter.limit("3/hour")  # Prevent spam registration
async def register(user_data: UserCreate):
    pass
```

### Input Validation

```python
from pydantic import EmailStr, field_validator

class UserCreate(SQLModel):
    email: EmailStr
    full_name: str
    password: str

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator('full_name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        # Remove HTML tags
        import re
        return re.sub(r'<[^>]+>', '', v)
```

### SQL Injection Prevention

SQLModel uses parameterized queries by default:

```python
# SAFE - Parameters are escaped
email = "user@example.com"
statement = select(User).where(User.email == email)

# STILL SAFE - Even with user input
user_input = request.form.get("email")
statement = select(User).where(User.email == user_input)

# NEVER use raw SQL with interpolation:
# UNSAFE - DON'T DO THIS
query = f"SELECT * FROM users WHERE email = '{user_input}'"
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[  # Whitelist specific domains
        "https://yourapp.com",
        "https://www.yourapp.com",
        os.getenv("FRONTEND_URL")
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Environment Variable Management

### .env.example

```env
# Database
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require

# JWT (Generate with: openssl rand -hex 32)
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourapp.com

# Frontend
FRONTEND_URL=http://localhost:3000

# Security
BCRYPT_ROUNDS=12
SESSION_EXPIRE_HOURS=24
```

### Validation in Production

```python
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    FRONTEND_URL: str

    @validator('JWT_SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
```

## Email Verification Security

### Verification Tokens

```python
def generate_verification_token() -> str:
    """Generate token with timestamp for expiry check."""
    timestamp = str(int(datetime.utcnow().timestamp()))
    random_part = secrets.token_urlsafe(16)
    return f"{timestamp}.{random_part}"

def verify_token_validity(token: str, max_hours: int = 24) -> bool:
    """Check if verification token is still valid."""
    try:
        timestamp_str, _ = token.split(".")
        created_at = datetime.fromtimestamp(float(timestamp_str))
        return datetime.utcnow() - created_at < timedelta(hours=max_hours)
    except (ValueError, AttributeError):
        return False
```

### Secure Email Links

```python
from urllib.parse import urlencode

def generate_verification_link(email: str, token: str) -> str:
    base_url = settings.FRONTEND_URL
    params = {
        "token": token,
        "email": email
    }
    return f"{base_url}/verify?{urlencode(params)}"

# HTTPS is required in production
if not settings.FRONTEND_URL.startswith("https://"):
    raise ValueError("FRONTEND_URL must use HTTPS in production")
```

## Common Vulnerabilities

### 1. Timing Attack Prevention

```python
import hmac

def verify_password_with_timing_protection(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    # Hash the plain password first
    input_hash = pwd_context.hash(plain_password)

    # Use constant-time comparison
    return hmac.compare_digest(input_hash, hashed_password)
```

### 2. Session Fixation Prevention

```python
from fastapi import Response

@app.post("/api/v1/auth/login")
async def login(credentials: UserLogin, response: Response):
    user = await authenticate(credentials)
    access_token = create_access_token(data={"sub": str(user.id)})

    # Set HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,    # Prevent XSS
        secure=True,      # HTTPS only
        samesite="lax",   # CSRF protection
        max_age=60 * 60 * 24 * 7  # 7 days
    )

    return {"access_token": access_token}
```

### 3. Mass Assignment Prevention

```python
from pydantic import BaseModel

class UserUpdate(BaseModel):
    """Only allow updating these fields."""
    full_name: Optional[str] = None
    theme: Optional[str] = None

    # EXCLUDE: email, id, is_verified, is_admin
```

## Security Checklist

Before deploying to production:

- [ ] SSL required for database connections
- [ ] Strong JWT secret key (32+ characters)
- [ ] Passwords hashed with bcrypt
- [ ] HTTPS enabled on frontend
- [ ] CORS properly configured
- [ ] Rate limiting on auth endpoints
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] Email verification implemented
- [ ] Secure session management (HttpOnly cookies)
- [ ] Environment variables not committed
- [ ] Row-level security for sensitive data
- [ ] Logging for security events
