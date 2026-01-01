# Email Setup with Resend and SMTP

Complete guide for email integration with Resend, including domain verification, SMTP fallback, and PostgreSQL integration.

## Resend Setup

### 1. Get API Key

1. Sign up at [resend.com](https://resend.com)
2. Navigate to **API Keys**
3. Create new API key (full-access or domain-restricted)
4. **Important:** Save immediately - only shown once!

### 2. Environment Configuration

```env
# Resend Configuration
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=onboarding@yourdomain.com
RESEND_FROM_NAME="Your App Name"

# SMTP Fallback (uses same API key as password)
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USERNAME=resend
SMTP_PASSWORD=re_xxxxxxxxxxxxxxxxxxxxxx
SMTP_USE_TLS=true
```

### 3. Install SDK

```bash
pip install resend
```

## Domain Verification for Production

### Why Domain Verification Matters

Without verification:
- Emails go to spam folder
- DKIM signatures fail
- Delivery rates are poor
- Professional appearance suffers

### DNS Records Required

When adding a domain in Resend, you'll receive specific DNS records. Add these to your domain provider (Cloudflare, GoDaddy, Namecheap, etc.):

#### SPF Record (TXT)

**Purpose:** Authorizes Resend to send email for your domain

```
Type: TXT
Name: send
Value: "v=spf1 include:resend.com ~all"
TTL: 3600
```

#### DKIM Records (CNAME)

You'll receive 3 DKIM records from Resend. Add all 3:

```
Type: CNAME
Name: resend1._domainkey
Value: resend1._domainkey.yourdomain.com.resend.com.
TTL: Auto

Type: CNAME
Name: resend2._domainkey
Value: resend2._domainkey.yourdomain.com.resend.com.
TTL: Auto

Type: CNAME
Name: resend3._domainkey
Value: resend3._domainkey.yourdomain.com.resend.com.
TTL: Auto
```

**Important:** The exact names/values will be provided in your Resend dashboard - copy exactly!

#### DMARC Record (TXT)

**Purpose:** Tells receivers what to do with spam/failing emails

```
Type: TXT
Name: _dmarc
Value: "v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarcreports@yourdomain.com"
TTL: 3600
```

**DMARC Policy Options:**
- `p=none` - No action (don't use in production)
- `p=quarantine` - Send to spam (recommended starting point)
- `p=reject` - Reject email (strictest, use after warming up)

### Verification Process

1. Add all DNS records to your domain provider
2. **Wait for DNS propagation** (5 min to 48 hours, usually 10-30 min)
3. Click "Verify" in Resend dashboard
4. Resend automatically checks DNS records

### Verify DNS Propagation

```bash
# Check DNS propagation
dig TXT send.yourdomain.com

# Or use online tools:
# - https://dns.google
# - https://dns.email
```

### Common DNS Issues

| Issue | Solution |
|-------|----------|
| Records not verifying | Wait longer for DNS propagation; use `dig` to verify |
| Wrong location | Add `send` subdomain records, NOT root domain |
| Quotes in TXT | Include quotes in value: `"v=spf1..."` |
| DKIM ends with dot | CNAME target must end with `.` |
| Multiple SPF records | Combine into one SPF record with `include:` |

## Email Templates

### Creating Templates via API

```python
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

def create_verification_template():
    params = resend.Templates.CreateParams(
        name="email-verification",
        subject="Verify Your Email Address",
        html="""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Verify Your Email Address</h2>
        <p>Hi {{{USER_NAME}}},</p>
        <p>Please click the button below to verify your email:</p>
        <p><a href="{{{VERIFICATION_URL}}}" class="button">Verify Email</a></p>
        <p><strong>This link expires in 24 hours.</strong></p>
        <p>If you didn't request this, please ignore this email.</p>
    </div>
</body>
</html>
        """,
    )
    template = resend.Templates.create(params)

    # Publish template (required before using)
    resend.Templates.publish(template["id"])

    return template["id"]
```

### Sending with Templates

```python
def send_verification_email(to_email: str, user_name: str, verification_url: str):
    template_id = os.getenv("RESEND_VERIFICATION_TEMPLATE_ID")

    email_template: resend.EmailTemplate = {
        "id": template_id,
        "variables": {
            "USER_NAME": user_name,
            "VERIFICATION_URL": verification_url,
        },
    }

    params: resend.Emails.SendParams = {
        "from": f"MyApp <{os.environ['RESEND_FROM_EMAIL']}>",
        "to": [to_email],
        "template": email_template,
    }

    try:
        email = resend.Emails.send(params)
        return {"success": True, "email_id": email["id"]}
    except resend.exceptions.ResendError as e:
        return {"success": False, "error": f"{e.code}: {e.message}"}
```

### Sending without Templates (Quick & Dirty)

```python
def send_simple_email(to_email: str, subject: str, content: str):
    params = resend.Emails.SendParams = {
        "from": f"MyApp <{os.environ['RESEND_FROM_EMAIL']}>",
        "to": [to_email],
        "subject": subject,
        "html": f"<p>{content}</p>",
    }

    try:
        email = resend.Emails.send(params)
        return {"success": True, "email_id": email["id"]}
    except resend.exceptions.ResendError as e:
        return {"success": False, "error": f"{e.code}: {e.message}"}
```

## SMTP Fallback

Resend supports SMTP! Use it as backup when API fails.

### SMTP Configuration

```
Host: smtp.resend.com
Port: 25, 465, 587, or 2465
  - 465/2465: Implicit SSL/TLS
  - 25/587: STARTTLS (recommended)
Username: resend
Password: YOUR_RESEND_API_KEY
```

### Python SMTP Implementation

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_via_smtp(to: list, subject: str, html: str):
    """Send email via SMTP fallback."""
    from_email = os.environ["RESEND_FROM_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["From"] = from_email
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.resend.com", 587) as server:
            server.starttls()
            server.login("resend", os.environ["RESEND_API_KEY"])
            server.send_message(msg)
        return {"success": True, "method": "smtp"}
    except Exception as e:
        return {"success": False, "error": str(e), "method": "smtp"}
```

### Email Service with Fallback

```python
class EmailService:
    @staticmethod
    async def send_with_fallback(to: list, subject: str, html: str):
        """Try Resend API first, fallback to SMTP."""
        resend.api_key = os.environ["RESEND_API_KEY"]

        # Try Resend API
        params: resend.Emails.SendParams = {
            "from": f"MyApp <{os.environ['RESEND_FROM_EMAIL']}>",
            "to": to,
            "subject": subject,
            "html": html,
        }

        try:
            email = resend.Emails.send(params)
            return {"success": True, "email_id": email["id"], "method": "api"}
        except Exception as api_error:
            print(f"Resend API failed: {api_error}. Trying SMTP...")

            # Fallback to SMTP
            result = send_via_smtp(to, subject, html)

            if result["success"]:
                return {
                    "success": True,
                    "method": "smtp_fallback",
                    "warning": "API failed, used SMTP fallback",
                }
            else:
                return {
                    "success": False,
                    "error": f"Both failed: {result['error']}",
                }
```

## PostgreSQL Integration

### Email Logging Tables

```sql
-- Track all sent emails
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    email_id VARCHAR(255),  -- Resend email ID
    to_email VARCHAR(255) NOT NULL,
    subject VARCHAR(500),
    status VARCHAR(50),  -- sent, delivered, bounced, opened
    idempotency_key VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Track bounced emails to prevent re-sending
CREATE TABLE bounced_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    bounce_reason TEXT,
    bounce_type VARCHAR(50),  -- hard, soft
    bounced_at TIMESTAMP DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_email_logs_user_id ON email_logs(user_id);
CREATE INDEX idx_email_logs_idempotency ON email_logs(idempotency_key);
```

### SQLAlchemy Model

```python
from sqlalchemy import Column, String, DateTime, UUID, Text
from sqlalchemy.sql import func
from sqlmodel import SQLModel, Field

class EmailLog(SQLModel, table=True):
    __tablename__ = "email_logs"

    id: str = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    email_id: str = Field(max_length=255)
    to_email: str = Field(max_length=255)
    subject: str = Field(max_length=500)
    status: str = Field(max_length=50)
    idempotency_key: str = Field(unique=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Complete Email Service with Logging

```python
import os
import resend
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

resend.api_key = os.environ["RESEND_API_KEY"]

class EmailService:
    @staticmethod
    async def send_and_log(
        db: AsyncSession,
        user_id: str,
        to_email: str,
        subject: str,
        html: str,
        idempotency_key: str,
    ):
        """Send email and log to database."""
        # Check bounced emails
        statement = select(BouncedEmail).where(BouncedEmail.email == to_email)
        result = await db.execute(statement)
        if result.scalar_one_or_none():
            return {"success": False, "error": "Email previously bounced"}

        # Check for duplicate (idempotency)
        statement = select(EmailLog).where(EmailLog.idempotency_key == idempotency_key)
        result = await db.execute(statement)
        if result.scalar_one_or_none():
            return {"success": False, "error": "Email already sent"}

        # Send email
        params = resend.Emails.SendParams = {
            "from": f"MyApp <{os.environ['RESEND_FROM_EMAIL']}>",
            "to": [to_email],
            "subject": subject,
            "html": html,
        }

        options: resend.Emails.SendOptions = {
            "idempotency_key": idempotency_key,
        }

        try:
            email = resend.Emails.send(params, options)

            # Log success
            log = EmailLog(
                user_id=user_id,
                email_id=email["id"],
                to_email=to_email,
                subject=subject,
                status="sent",
                idempotency_key=idempotency_key,
            )
            db.add(log)
            await db.commit()

            return {"success": True, "email_id": email["id"]}

        except resend.exceptions.ResendError as e:
            # Log failure
            log = EmailLog(
                user_id=user_id,
                email_id="",
                to_email=to_email,
                subject=subject,
                status="failed",
                idempotency_key=idempotency_key,
            )
            db.add(log)
            await db.commit()

            return {"success": False, "error": f"{e.code}: {e.message}"}
```

## Webhook Integration

### FastAPI Webhook Endpoint

```python
from fastapi import APIRouter, Request, HTTPException
from typing import Dict
import hmac
import hashlib

router = APIRouter()

WEBHOOK_SECRET = os.getenv("RESEND_WEBHOOK_SECRET")

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Resend webhook signature."""
    hmac_obj = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256,
    )
    expected_signature = hmac_obj.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@router.post("/webhooks/resend")
async def resend_webhook(request: Request):
    """Handle Resend webhook events."""
    # Get signature
    signature = request.headers.get("Resend-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    # Get payload
    payload = await request.body()

    # Verify signature
    if not verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = payload.decode()

    # Parse event (Resend sends JSON)
    import json
    data = json.loads(event)

    event_type = data.get("type")

    if event_type == "email.delivery_delayed":
        # Log delay
        print(f"Email delayed: {data}")

    elif event_type == "email.bounced":
        # Mark email as bounced
        email = data["data"]["to"][0]
        await mark_email_as_bounced(email, data.get("reason", "Unknown"))

    elif event_type == "email.complained":
        # User marked as spam
        email = data["data"]["to"][0]
        await suppress_email(email)

    return {"status": "received"}

async def mark_email_as_bounced(email: str, reason: str):
    """Add email to bounced list."""
    from sqlalchemy import delete

    statement = delete(BouncedEmail).where(BouncedEmail.email == email)
    # Actually implement add...

async def suppress_email(email: str):
    """Optionally suppress sending to this email in future."""
    pass
```

## Rate Limits

### Resend Rate Limits

| Tier | Rate Limit |
|------|------------|
| Free | 3 emails/second, 3,000/day |
| Growth | 50 emails/second, 50,000/day |
| Pro | 100 emails/second, 100,000/day |

### Bounce Rate Requirements

- **Maximum allowed:** 4%
- **Consequence:** Temporary sending pause if exceeded
- **Monitor:** Via dashboard Metrics page or webhooks

### Idempotency Keys

Prevent duplicate emails by using idempotency keys:

```python
options: resend.Emails.SendOptions = {
    "idempotency_key": f"user-{user_id}-verification-{timestamp}",
}
```

## Testing Email

### During Development

Use Resend's test addresses - they never deliver to real inboxes:

```python
test_recipients = [
    "test@resend.dev",
    "test2@resend.dev",
    "test3@resend.dev",
]
```

### Test Your Setup

```python
# Test email
result = send_verification_email(
    "test@resend.dev",  # Use during development
    "Test User",
    "https://localhost:3000/verify?token=test123",
)

print(result)
```

## Production Checklist

Before going live:

### Domain Configuration
- [ ] Domain added in Resend dashboard
- [ ] SPF record added
- [ ] All 3 DKIM records added
- [ ] DMARC record added
- [ ] Domain verified in Resend dashboard
- [ ] DNS propagated (use `dig` to verify)

### Email Configuration
- [ ] `RESEND_FROM_EMAIL` uses verified domain
- [ ] Email templates created and published
- [ ] Test email sent successfully
- [ ] Idempotency keys implemented
- [ ] Webhook endpoint configured
- [ ] Bounce handling implemented

### Database
- [ ] Email logging tables created
- [ ] Bounced emails table created
- [ ] Indexes created for performance
- [ ] Idempotency key unique constraint

### Security
- [ ] `RESEND_API_KEY` stored in environment variable
- [ ] `.env` file in `.gitignore`
- [ ] Webhook signature verification implemented
- [ ] Rate limiting on email endpoints

### Monitoring
- [ ] Dashboard metrics monitored
- [ ] Bounce rate tracked (must stay below 4%)
- [ ] Webhook events logged
- [ ] Failed emails trigger alerts

## Environment Variables

### Local Development
```env
# Use localhost database without SSL
DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb?sslmode=disable

# Use test email addresses during development
RESEND_FROM_EMAIL=test@resend.dev  # Or your actual domain
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx
```

### Production
```env
# Neon with SSL required
DATABASE_URL=postgresql://user:pass@ep-xyz.aws.neon.tech/mydb?sslmode=require

# Your verified domain
RESEND_FROM_EMAIL=noreply@yourdomain.com
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxx

# Strong JWT secret
JWT_SECRET_KEY=<generate-secure-32-char-key>
FRONTEND_URL=https://yourapp.com
```

## Troubleshooting

### Email Not Delivered

1. **Check domain verification status** in Resend dashboard
2. **Verify DNS records** using [dns.email](https://dns.email)
3. **Check spam folder** - might be there
4. **Verify `from` address** matches your domain
5. **Check Resend dashboard logs** for error details

### DNS Records Not Verifying

1. **Wait longer** - DNS propagation can take up to 48 hours
2. **Check record format** - ensure quotes in TXT records
3. **Verify location** - SPF/DKIM on `send` subdomain
4. **Use `dig` to check**:
   ```bash
   dig TXT send.yourdomain.com
   ```

### SMTP Fallback Not Working

1. **Verify credentials** - API key is SMTP password
2. **Check port** - try 587 with STARTTLS
3. **Test with email client first** (Thunderbird, Outlook)
4. **Check firewall** - port 587 must be open

## Best Practices

1. **Always use idempotency keys** for transactional emails
2. **Test with test@resend.dev** during development
3. **Monitor bounce rates** weekly - keep below 4%
4. **Use templates** for consistent branding
5. **Implement webhook handlers** for bounce/complaint events
6. **Log all emails** to database for audit trail
7. **Never hardcode credentials** - always use environment variables
8. **Set up rate limiting** on email endpoints
9. **Use double opt-in** for newsletter subscriptions
10. **Provide unsubscribe links** in marketing emails
