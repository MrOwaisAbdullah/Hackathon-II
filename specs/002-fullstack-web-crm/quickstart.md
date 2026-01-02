# Quickstart Guide: TeamFlow Web (Phase 2)

**Branch**: `002-fullstack-web-crm` | **Date**: 2026-01-03 | **Plan**: [plan.md](./plan.md)

> **Updated for Phase 9 Polish**: Includes keyboard shortcuts (CMD+K command palette), performance optimizations (GZip, rate limiting, structured logging), and accessibility improvements (ARIA labels, error boundaries, skeleton loading).

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.13 or higher
- **Node.js** 20 or higher (LTS)
- **Git** for version control
- **Neon PostgreSQL** account (free tier works)
- **Better Auth** account (for JWT verification)

---

## 1. Repository Setup

### Clone and Configure

```bash
# Clone the repository
git clone https://github.com/your-org/teamflow.git
cd teamflow

# Checkout the Phase 2 branch
git checkout 002-fullstack-web-crm

# Install Python dependencies
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install Node dependencies
cd ../frontend
npm install
```

### Environment Variables

Create `.env` files for both backend and frontend:

**Backend `.env`**:
```bash
# Database
DATABASE_URL=postgresql://user:password@ep-xyz.aws.neon.tech/teamflow?sslmode=require

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET=your-secret-key-here

# Better Auth
BETTER_AUTH_SECRET=your-better-auth-secret

# CORS
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Frontend `.env.local`**:
```bash
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/v1

# Better Auth
NEXT_PUBLIC BETTER_AUTH_URL=https://your-better-auth-instance.com
```

---

## 2. Database Setup

### Create Neon Database

1. Sign up at [Neon](https://neon.tech)
2. Create a new project: `teamflow`
3. Copy the connection string
4. Add to `backend/.env` as `DATABASE_URL`

### Run Migrations

```bash
cd backend

# Run Alembic migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

Expected tables:
- `agencies`
- `users`
- `projects`
- `tasks`
- `time_entries`

---

## 3. Start Development Servers

### Backend (FastAPI)

```bash
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

Backend runs on: **http://localhost:8000**

- API docs: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

### Frontend (Next.js)

```bash
cd frontend
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 4. First Run

### Register Agency

1. Open http://localhost:3000
2. Click "Sign Up"
3. Fill in agency details:
   - Agency Name: "My Creative Studio"
   - Email: "admin@studio.com"
   - Password: "SecurePass123!"
   - Name: "Admin User"
4. Submit

This creates:
- New Agency record
- First User (admin)
- JWT token stored in httpOnly cookie

### Verify Login

```bash
# You should see JWT token in cookie
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@studio.com", "password": "SecurePass123!"}'
```

---

## 5. Development Workflow

### Create a Task

```bash
curl -X POST http://localhost:8000/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Design homepage mockup",
    "description": "Create Figma mockup for landing page",
    "status": "todo",
    "priority": "high"
  }'
```

### List Tasks

```bash
curl http://localhost:8000/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Assign Task

```bash
curl -X POST http://localhost:8000/v1/tasks/{task_id}/assign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"assignee_id": "user_uuid"}'
```

---

## 6. Keyboard Shortcuts

The application includes a **Command Palette** for quick navigation and actions.

### Command Palette

Press **`CMD+K`** (Mac) or **`Ctrl+K`** (Windows) to open the command palette from anywhere in the app.

**Available Commands:**

| Category | Command | Description |
|----------|---------|-------------|
| Navigation | Go to Dashboard | View your agency overview and metrics |
| Navigation | Go to Tasks | View and manage your task board |
| Navigation | Go to Projects | View all your projects |
| Navigation | Go to Team | Manage your team members |
| Navigation | Go to Time Entries | View your logged time entries |
| Navigation | Go to Archive | View archived tasks |
| Navigation | Go to Settings | Manage your account settings |
| Actions | Create New Task | Quickly create a new task (`N` shortcut) |
| Actions | Logout | Sign out of your account |
| Settings | Toggle Theme | Switch between dark and light mode |

**Keyboard Navigation:**
- `Arrow Down/Up` - Navigate through commands
- `Enter` - Execute selected command
- `ESC` - Close palette

---

## 7. New Features (Phase 9 Polish)

### Performance & Security

- **GZip Compression**: All API responses > 1KB are compressed automatically
- **Rate Limiting**: Auth endpoints protected (register: 3/hour, login: 5/minute per IP)
- **Structured Logging**: JSON-formatted logs in production with request timing
- **Code Splitting**: Dashboard and task board components loaded dynamically

### Accessibility & UX

- **Skeleton Loading**: Loading states shown with animated placeholders
- **Error Boundaries**: Graceful error handling with retry options
- **ARIA Labels**: Screen reader support for task cards and columns
- **Manual Refresh**: Refresh button on task board for manual data reload

### Command Palette

- Global keyboard shortcut (`CMD+K` / `Ctrl+K`)
- Searchable command interface
- Theme-aware with smooth animations

---

## 8. Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_task_service.py
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Type checking
npm run type-check
```

---

## 9. Key Development Commands

### Backend

| Command | Description |
|---------|-------------|
| `uvicorn src.main:app --reload` | Start dev server |
| `pytest` | Run tests |
| `alembic revision --autogenerate` | Create migration |
| `alembic upgrade head` | Apply migrations |
| `black .` | Format Python code |
| `pylint src/` | Lint Python code |

### Frontend

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Production build |
| `npm test` | Run unit tests |
| `npm run lint` | Lint TypeScript |
| `npm run type-check` | Type checking |

---

## 10. Project Structure Reference

```
teamflow/
├── backend/                 # FastAPI + SQLModel
│   ├── app/
│   │   ├── api/            # API endpoints (tasks, auth, analytics, users)
│   │   ├── models/         # SQLModel entities (User, Task, Project, etc.)
│   │   ├── services/       # Business logic (auth_service, task_service, etc.)
│   │   ├── core/           # Core utilities (security, rate_limit, logging)
│   │   ├── db/             # Database session management
│   │   └── main.py         # FastAPI app with middleware stack
│   ├── tests/
│   │   ├── unit/           # Service tests
│   │   ├── integration/    # API tests
│   │   └── contract/       # OpenAPI contract tests
│   └── alembic/            # Alembic migrations
│       └── versions/
│
├── frontend/               # Next.js 16 with App Router
│   ├── src/
│   │   ├── app/           # App Router with route groups
│   │   │   ├── (auth)/    # Public auth pages (login, register)
│   │   │   └── (main)/    # Protected pages (dashboard, tasks, etc.)
│   │   ├── components/    # React components
│   │   │   ├── board/     # Kanban board components
│   │   │   ├── dashboard/ # Dashboard components
│   │   │   ├── task/      # Task-related components
│   │   │   └── ui/        # Reusable UI components
│   │   ├── contexts/      # React contexts (ThemeContext, AuthContext)
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utilities and API client
│   └── tests/
│       ├── e2e/           # Playwright E2E tests
│
└── specs/                 # Architecture docs
    └── 002-fullstack-web-crm/
        ├── spec.md
        ├── plan.md
        ├── tasks.md
        └── contracts/
```

---

## 11. Common Issues

### Issue: "Module not found"

**Solution**:
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Issue: "Database connection failed"

**Solution**:
1. Verify `DATABASE_URL` in `.env`
2. Check Neon database is active
3. Ensure `sslmode=require` in connection string

### Issue: "JWT verification failed"

**Solution**:
1. Verify `JWT_SECRET` matches between backend and Better Auth
2. Check token isn't expired (1 hour default)
3. Ensure `agency_id` claim is present

### Issue: "CORS errors"

**Solution**:
1. Verify `FRONTEND_URL` in backend `.env`
2. Check FastAPI CORS middleware includes origin
3. Ensure cookies set with `SameSite=Strict`

---

## 12. Production Deployment

### Backend Deployment (Vercel/Railway)

1. Set environment variables in platform
2. Run migrations: `alembic upgrade head`
3. Deploy: `vercel deploy` or push to Railway

### Frontend Deployment (Vercel)

```bash
cd frontend
npm run build
vercel deploy
```

### Environment Checklist

- [ ] Production `DATABASE_URL` (Neon)
- [ ] Production `JWT_SECRET`
- [ ] Production `BETTER_AUTH_SECRET`
- [ ] `ENVIRONMENT=production`
- [ ] HTTPS enabled
- [ ] CORS configured for production domain

---

## 13. Useful Links

- **Backend API Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: `specs/002-fullstack-web-crm/contracts/openapi.yaml`
- **Data Model**: `specs/002-fullstack-web-crm/data-model.md`
- **Research**: `specs/002-fullstack-web-crm/research.md`
- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **dnd-kit Docs**: https://docs.dndkit.com
- **Motion Docs**: https://motion.dev

---

## 14. Getting Help

- **Spec Questions**: Check `spec.md`
- **Architecture Questions**: Check `plan.md`
- **API Questions**: Check OpenAPI spec in `/contracts/`
- **Bug Reports**: Create GitHub issue with label `bug`
- **Feature Requests**: Create GitHub issue with label `enhancement`

---

## Next Steps

1. ✅ Setup complete
2. Read [spec.md](./spec.md) for feature requirements
3. Review [plan.md](./plan.md) for architecture decisions
4. Run `/sp.tasks` to generate implementation tasks
5. Start building! 🚀
