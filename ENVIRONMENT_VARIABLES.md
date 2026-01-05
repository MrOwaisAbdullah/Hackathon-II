# TeamFlow Environment Variables Reference

Complete reference for all environment variables used in TeamFlow deployment.

## Quick Setup Checklist

### GitHub Secrets (for CI/CD)
- [ ] `VERCEL_TOKEN`
- [ ] `VERCEL_ORG_ID`
- [ ] `VERCEL_PROJECT_ID`
- [ ] `HF_TOKEN`
- [ ] `HF_SPACE_NAME`
- [ ] `BACKEND_API_URL`

### HuggingFace Space Secrets (Backend)
- [ ] `DATABASE_URL` (Required)
- [ ] `SECRET_KEY` (Required)
- [ ] `ENVIRONMENT` (Optional)
- [ ] `FRONTEND_URL` (Optional - for CORS)

### Vercel Environment Variables (Frontend)
- [ ] `NEXT_PUBLIC_API_URL` (Required)

---

## Detailed Configuration

### Backend Variables (HuggingFace Spaces)

#### DATABASE_URL (Required)
**Description**: Neon PostgreSQL connection string

**Format**:
```
postgresql://username:password@ep-xyz.aws.neon.tech/teamflow?sslmode=require
```

**How to Get**:
1. Go to [Neon Console](https://console.neon.tech)
2. Create a project
3. Copy the connection string
4. Ensure it includes `?sslmode=require`

**Example**:
```
DATABASE_URL=postgresql://teamflow_user:abc123@ep-cool-darkness-123456.aws.neon.tech/teamflow?sslmode=require
```

---

#### SECRET_KEY (Required)
**Description**: JWT secret key for authentication

**How to Generate**:
```bash
openssl rand -hex 32
```

**Format**: 64-character hexadecimal string

**Example**:
```
SECRET_KEY=a1b2c3d4e5f6...64 characters total...x9y8z7
```

**Security Notes**:
- Must be at least 32 characters
- Keep this secret!
- Don't commit to git
- Rotate periodically in production

---

#### ENVIRONMENT (Optional)
**Description**: Application environment

**Values**: `development`, `staging`, `production`

**Example**:
```
ENVIRONMENT=production
```

**Default**: `development`

---

#### FRONTEND_URL (Optional)
**Description**: Allowed CORS origins for frontend

**Format**: Comma-separated list of URLs

**Example**:
```
FRONTEND_URL=https://teamflow.vercel.app,https://localhost:3000
```

**Default**: `http://localhost:3000,http://localhost:8000`

---

#### API_V1_PREFIX (Optional)
**Description**: API version prefix

**Example**:
```
API_V1_PREFIX=/api/v1
```

**Default**: `/api/v1`

---

### Frontend Variables (Vercel)

#### NEXT_PUBLIC_API_URL (Required)
**Description**: Backend API URL for frontend to connect to

**Format**: Full URL to HuggingFace Space

**Example**:
```
NEXT_PUBLIC_API_URL=https://username-teamflow-backend.hf.space
```

**How to Get**:
1. Deploy backend to HuggingFace Spaces
2. Copy the Space URL
3. Set in Vercel environment variables

**Important Notes**:
- Must start with `https://`
- Don't include trailing slash
- Don't include `/api/v1` (appended automatically)

---

### GitHub Actions Secrets (CI/CD)

#### VERCEL_TOKEN
**Description**: Vercel authentication token

**How to Get**:
1. Go to [Vercel Dashboard](https://vercel.com/account/tokens)
2. Create a new token
3. Copy the token

**Permissions**: Full account deployment

---

#### VERCEL_ORG_ID
**Description**: Vercel organization ID

**How to Get**:
```bash
cd teamflow-web/frontend
vercel link
cat .vercel/project.json
```

**Format**: String like `team_xxxxxxxxx`

---

#### VERCEL_PROJECT_ID
**Description**: Vercel project ID

**How to Get**:
```bash
cd teamflow-web/frontend
vercel link
cat .vercel/project.json
```

**Format**: String like `prj_xxxxxxxxx`

---

#### HF_TOKEN
**Description**: HuggingFace authentication token

**How to Get**:
1. Go to [HF Settings > Tokens](https://huggingface.co/settings/tokens)
2. Create a new token
3. Select **Write** permissions
4. Copy the token (starts with `hf_`)

**Format**: `hf_...`

**Permissions**: Write (required for pushing to Spaces)

---

#### HF_SPACE_NAME
**Description**: HuggingFace Space name

**Format**: `username/space-name`

**Example**:
```
HF_SPACE_NAME=johndoe/teamflow-backend
```

**How to Get**:
1. Create a Space on HuggingFace
2. Use `username/space-name` format

---

#### BACKEND_API_URL
**Description**: Full URL to backend for build-time operations

**Format**: Same as `NEXT_PUBLIC_API_URL`

**Example**:
```
BACKEND_API_URL=https://username-teamflow-backend.hf.space
```

---

## Environment-Specific Values

### Development
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/teamflow
SECRET_KEY=dev-secret-key-not-for-production
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Staging
```bash
# Backend (HuggingFace Space - Staging)
DATABASE_URL=postgresql://...staging-db...
SECRET_KEY=staging-secret-key
ENVIRONMENT=staging
FRONTEND_URL=https://teamflow-staging.vercel.app

# Frontend (Vercel - Staging)
NEXT_PUBLIC_API_URL=https://teamflow-backend-staging.hf.space
```

### Production
```bash
# Backend (HuggingFace Space - Production)
DATABASE_URL=postgresql://...production-db...
SECRET_KEY=strong-production-secret-key
ENVIRONMENT=production
FRONTEND_URL=https://teamflow.vercel.app

# Frontend (Vercel - Production)
NEXT_PUBLIC_API_URL=https://teamflow-backend.hf.space
```

---

## Variable Naming Conventions

### Backend (FastAPI)
- **UPPER_CASE**: Standard environment variables
- **snake_case**: Database URLs, API keys

### Frontend (Next.js)
- **NEXT_PUBLIC_***: Variables exposed to browser
- Only `NEXT_PUBLIC_*` variables are accessible in client-side code

### GitHub Actions
- **ALL_CAPS**: Consistent with backend naming
- Used in CI/CD workflows

---

## Security Best Practices

### ✅ DO
- Use strong, randomly generated secrets
- Rotate secrets periodically
- Use different secrets for different environments
- Restrict token permissions to minimum required
- Enable audit logging where available

### ❌ DON'T
- Commit secrets to git
- Share secrets in chat/email
- Use production secrets in development
- Reuse secrets across projects
- Leave default/placeholder values in production

---

## Testing Your Configuration

### Test Backend Variables
```bash
# From backend directory
cd teamflow-web/backend

# Load and validate
python -c "
from app.core.config import settings
print('Database URL:', settings.database_url[:20] + '...')
print('Environment:', settings.environment)
print('API Prefix:', settings.api_v1_prefix)
print('CORS Origins:', settings.cors_origins)
"
```

### Test Frontend Variables
```bash
# From frontend directory
cd teamflow-web/frontend

# Check Next.js can access
npm run build
```

### Test GitHub Actions Variables
```bash
# Create test workflow
cat > .github/workflows/test-env.yml << 'EOF'
name: Test Environment Variables
on: workflow_dispatch
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test variables
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          echo "Vercel token: ${VERCEL_TOKEN:0:10}..."
          echo "HF token: ${HF_TOKEN:0:10}..."
EOF
```

---

## Troubleshooting

### Issue: Variables not loading
**Solution**:
- Check file names (`.env` vs `.env.local`)
- Verify no typos in variable names
- Ensure variables are in correct location

### Issue: CORS errors
**Solution**:
- Add frontend URL to `FRONTEND_URL` in backend
- Ensure protocol matches (http vs https)
- Check for trailing slashes

### Issue: Build failures
**Solution**:
- Verify all required variables are set
- Check variable formats (URLs, tokens)
- Rebuild after adding variables

---

## Quick Reference Card

| Platform | Variables Required | Where to Set |
|----------|-------------------|--------------|
| **HuggingFace** | DATABASE_URL, SECRET_KEY | Space Settings > Variables |
| **Vercel** | NEXT_PUBLIC_API_URL | Project Settings > Environment Variables |
| **GitHub Actions** | VERCEL_TOKEN, HF_TOKEN, etc. | Repository > Settings > Secrets |

---

For deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)
