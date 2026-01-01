# Implementation Plan: TeamFlow Web (Phase 2 - Full-Stack Agency CRM)

**Branch**: `002-fullstack-web-crm` | **Date**: 2025-01-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-web-crm/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

TeamFlow Phase 2 transforms the CLI-based task management tool into a **full-stack web application** designed for creative agencies (10-50 team members). The application provides a Kanban-style task board with drag-and-drop, real-time collaboration (10s polling), team assignment, time tracking, and profitability reporting.

**Technical Approach**: Next.js 16 (App Router) frontend with Motion.dev animations, FastAPI backend with SQLModel/Neon PostgreSQL, Better Auth for JWT authentication with multi-tenant agency isolation.

---

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.8+ (Next.js 16)
- Backend: Python 3.13+ (FastAPI 0.115+)

**Primary Dependencies**:
- Frontend: Next.js 16, React Query, Zustand, Motion.dev (Framer Motion), @dnd-kit, Shadcn UI, Tailwind CSS
- Backend: FastAPI, SQLModel, Better Auth, uvicorn
- Database: Neon PostgreSQL (Serverless)

**Storage**:
- Neon PostgreSQL (Serverless PostgreSQL)
- Table structure: Agency, User, Project, Task, TimeEntry
- Multi-tenant isolation via agency_id foreign key

**Testing**:
- Backend: pytest, pytest-cov, httpx (for FastAPI testing)
- Frontend: vitest, @testing-library/react, @testing-library/user-event
- E2E: Playwright (for critical user journeys)

**Target Platform**:
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge) - last 2 versions
- Backend: Linux server (container-ready for K8s deployment)
- Mobile responsive: 320px minimum width

**Project Type**: web (full-stack with separate frontend/backend)

**Performance Goals**:
- API endpoints: < 200ms p95
- Dashboard load: < 2s LCP
- Task board animations: 60fps
- Drag-and-drop latency: < 500ms end-to-end
- Polling for updates: every 10 seconds

**Constraints**:
- LCP must be under 1.5 seconds
- Must support 50 concurrent users without degradation
- Task board renders smoothly with 100+ tasks per column
- All animations must complete within 400ms
- WCAG AA accessibility compliance required

**Scale/Scope**:
- 2-50 team members per agency
- Support 10+ concurrent agencies
- 100+ tasks per column on task board
- 47 functional requirements across 6 feature areas

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance Check

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Specialized Agents & Skills First** | ✅ PASS | Will use `better-auth-specialist` for auth, `frontend-designer` for UI components |
| **II. SOLID Principles** | ✅ PASS | Service layer separation, repository pattern, protocol-based interfaces |
| **III. DRY** | ✅ PASS | Shared utilities in `/backend/shared/` and `/frontend/lib/` |
| **IV. TDD** | ✅ PASS | Unit tests (80%+ coverage), integration tests, E2E tests required |
| **V. Spec-Driven Development** | ✅ PASS | Spec already created via `/sp.specify` |
| **VI. Type Safety** | ✅ PASS | Python: Pydantic + type hints; TypeScript: strict mode |
| **VII. Security** | ✅ PASS | JWT auth, agency_id scoping, input validation on all endpoints |
| **VIII. Performance** | ✅ PASS | Targets defined (200ms API, 2s LCP, 60fps animations) |
| **IX. Code Style** | ✅ PASS | Black/isort/pylint (Python), ESLint/Prettier (TS) |
| **X. MCP Integration** | ✅ PASS | context7 for docs, github for repo, chrome-devtools for testing |
| **XI. Skill Refinement** | ✅ PASS | Errors documented in skills as encountered |
| **XII. Documentation Lookup** | ✅ PASS | context7 MCP used before implementation |

### Phase II Constraints (Constitution)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Better Auth + JWT required | ✅ PLANNED | Using `better-auth-specialist` agent |
| Neon PostgreSQL required | ✅ PLANNED | SQLModel with Neon Serverless |
| RESTful API documentation | ✅ PLANNED | OpenAPI spec generated via FastAPI |

---

**GATE STATUS**: ✅ PASS - All constitution requirements satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# TeamFlow Phase 2: Full-Stack Web Application Structure
backend/                          # FastAPI + SQLModel + Neon PostgreSQL
├── src/
│   ├── api/                      # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── auth.py              # JWT verification, agency scoping
│   │   ├── tasks.py             # Task CRUD endpoints
│   │   ├── projects.py          # Project management
│   │   ├── users.py             # Team member management
│   │   ├── time_entries.py      # Time tracking endpoints
│   │   └── agencies.py          # Agency administration
│   ├── core/                     # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py            # Environment variables, settings
│   │   ├── security.py          # JWT verification, password hashing
│   │   └── middleware.py        # Agency scoping middleware
│   ├── models/                   # SQLModel database models
│   │   ├── __init__.py
│   │   ├── agency.py            # Agency (tenant) entity
│   │   ├── user.py              # User (team member) entity
│   │   ├── project.py           # Project entity
│   │   ├── task.py              # Task entity with status
│   │   └── time_entry.py        # Time tracking entity
│   ├── schemas/                  # Pydantic schemas for API
│   │   ├── __init__.py
│   │   ├── auth.py              # Login, register response models
│   │   ├── task.py              # Task request/response models
│   │   ├── project.py           # Project request/response models
│   │   └── time_entry.py        # Time entry models
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication, agency creation
│   │   ├── task_service.py      # Task CRUD, assignment logic
│   │   ├── project_service.py   # Project management
│   │   └── analytics_service.py # Profitability calculations
│   ├── db/                       # Database session management
│   │   ├── __init__.py
│   │   ├── session.py           # Neon PostgreSQL connection
│   │   └── init_db.py           # Database initialization
│   └── main.py                   # FastAPI application entry point
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests for services
│   │   ├── test_auth_service.py
│   │   ├── test_task_service.py
│   │   └── test_analytics.py
│   ├── integration/             # API endpoint tests
│   │   ├── test_tasks_api.py
│   │   ├── test_auth_api.py
│   │   └── test_projects_api.py
│   └── contract/                # Contract tests for API spec
│       └── test_openapi_spec.py
├── pyproject.toml               # Python project config
├── .env.example                 # Environment variables template
└── README.md

frontend/                         # Next.js 16 + Motion.dev + Shadcn UI
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── layout.tsx           # Root layout with providers
│   │   ├── page.tsx             # Landing page
│   │   ├── dashboard/           # Dashboard pages
│   │   │   ├── layout.tsx       # Dashboard layout
│   │   │   └── page.tsx         # Dashboard home
│   │   ├── projects/            # Project routes
│   │   │   └── [id]/            # Dynamic project pages
│   │   │       └── page.tsx
│   │   ├── auth/                # Authentication routes
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   └── api/                 # Next.js API routes (proxy)
│   │       └── [...].tsx        # Catch-all proxy to backend
│   ├── components/              # React components
│   │   ├── ui/                  # Shadcn UI components
│   │   ├── board/               # Kanban board components
│   │   │   ├── TaskBoard.tsx    # Main board with dnd-kit
│   │   │   ├── TaskColumn.tsx   # Column component
│   │   │   ├── TaskCard.tsx     # Draggable task card
│   │   │   └── DropZone.tsx     # Drop target
│   │   ├── dashboard/           # Dashboard components
│   │   │   ├── StatCard.tsx     # Animated stat cards
│   │   │   └── ProjectList.tsx  # Project grid
│   │   ├── task/                # Task-related components
│   │   │   ├── TaskDrawer.tsx   # Side drawer for task details
│   │   │   ├── TaskForm.tsx     # Create/edit task form
│   │   │   └── AssigneeAvatar.tsx # User assignment chips
│   │   └── auth/                # Auth components
│   │       ├── LoginForm.tsx
│   │       └── RegisterForm.tsx
│   ├── lib/                     # Shared utilities
│   │   ├── api.ts               # API client (fetch wrapper)
│   │   ├── query.ts             # React Query hooks
│   │   ├── store.ts             # Zustand client state
│   │   └── utils.ts             # Common utilities
│   ├── hooks/                   # Custom React hooks
│   │   ├── useTaskBoard.ts      # Task board state + dnd-kit
│   │   ├── useTimeTracking.ts   # Timer state
│   │   └── useAuth.ts           # Auth state
│   ├── types/                   # TypeScript types
│   │   ├── task.ts
│   │   ├── project.ts
│   │   └── user.ts
│   └── styles/                  # Global styles
│       └── globals.css          # Tailwind directives
├── tests/
│   ├── unit/                   # Vitest unit tests
│   │   ├── TaskCard.test.tsx
│   │   └── useTaskBoard.test.ts
│   ├── integration/            # Component integration tests
│   │   └── TaskBoard.test.tsx
│   └── e2e/                    # Playwright E2E tests
│       ├── auth.spec.ts
│       ├── task-board.spec.ts
│       └── drag-drop.spec.ts
├── public/                      # Static assets
├── next.config.js              # Next.js configuration
├── tailwind.config.ts          # Tailwind CSS + custom theme
├── tsconfig.json               # TypeScript config (strict mode)
├── package.json                # Dependencies
└── README.md
```

**Structure Decision**: This is a **full-stack web application** with clear separation between backend (FastAPI) and frontend (Next.js). The backend follows a layered architecture (API → Services → Models) with SOLID principles. The frontend uses Next.js 16 App Router with component colocation and feature-based organization (board/, dashboard/, task/). Both backend and frontend have their own test suites with unit/integration/e2e levels.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | No constitution violations | All principles satisfied |

---

## Architecture Design

### Backend Architecture

#### Layered Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│  (FastAPI Route Handlers - /api/tasks, /api/auth)      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                          │
│  (Business Logic - TaskService, AuthService)           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Layer                             │
│  (SQLModel - Task, User, Project entities)             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Neon PostgreSQL                            │
└─────────────────────────────────────────────────────────┘
```

#### Dependency Injection Flow

```python
# 1. Request arrives
POST /api/tasks

# 2. JWT Middleware verifies token
#    Extracts agency_id, user_id

# 3. Route handler receives dependencies
def create_task(
    task: TaskCreate,           # Pydantic validation
    session: SessionDep,        # DB session
    current_user: CurrentUser   # JWT claims
):
    # 4. Delegates to service
    service = TaskService(session)
    return service.create_task(task, current_user.agency_id)

# 5. Service handles business logic
class TaskService:
    def create_task(self, data, agency_id):
        task = Task(**data.model_dump(), agency_id=agency_id)
        session.add(task)
        session.commit()
        return task
```

#### Middleware Stack

1. **CORSMiddleware**: Handles CORS for frontend origin
2. **JWTMiddleware**: Verifies JWT, extracts claims
3. **AgencyScopingMiddleware**: Ensures agency_id present in JWT
4. **ErrorHandlingMiddleware**: Catches exceptions, returns 500

---

### Frontend Architecture

#### Component Hierarchy

```
App Router (app/)
│
├── Root Layout
│   ├── React Query Provider
│   ├── Zustand Provider
│   └── Theme Provider (with ThemeContext)
│
├── Dashboard Layout
│   ├── Sidebar (collapsible with localStorage persistence)
│   │   ├── Collapse/Expand Button
│   │   ├── Navigation Items
│   │   └── Theme Toggle Button
│   ├── Header
│   │   └── User Menu / Theme Toggle
│   └── Content Area
│       ├── StatCard Grid (with stagger animations)
│       ├── TaskDistributionChart (animated bars)
│       └── WorkflowProgress (animated steps)
│
└── Task Board Page (Server Component)
    ├── TaskBoard (Client - dnd-kit)
    │   ├── TaskColumn (Client - droppable)
    │   │   └── TaskCard (Client - draggable)
    │   └── DragOverlay
    └── TaskDrawer (Client - side drawer)
```

#### State Management Strategy

```typescript
// Server State (React Query)
const {data: tasks} = useTasks()  // Auto-refetch every 10s

// Client State (Zustand)
const {selectedTask, setSelectedTask} = useUIStore()
const {isSidebarCollapsed, toggleSidebar} = useSidebarStore()

// Theme State (ThemeContext)
const {theme, toggleTheme} = useTheme()  // 'light' | 'dark', persisted to localStorage

// Local State (useState)
const [isDragging, setIsDragging] = useState(false)
```

#### Data Flow Pattern

```
User Action (Drag Task)
      │
      ▼
Event Handler (onDragEnd)
      │
      ▼
Optimistic Update (setQueryData)
      │
      ▼
API Call (fetch PATCH /tasks/{id})
      │
      ├─ Success → Invalidate Query (refetch)
      └─ Error → Rollback (setQueryData with previous)
```

---

### Theme Implementation Design

**⭐ PRE-IMPLEMENTATION: Use `@.claude/agents/nextjs-frontend-architect.md` for ALL frontend tasks.**

This agent orchestrates:
- `building-nextjs-apps` skill for Next.js 16 patterns and SSR-safe components
- `theme-factory` skill for professional color palettes
- `frontend-designer` skill for animation choreography
- `gemini-frontend-assistant` skill for code generation

**For theme specifically**, the architect will use `theme-factory` to generate color palette and theme structure BEFORE implementing.

**Approach**: CSS-first theming with Tailwind dark mode, React Context for state, and design tokens for consistency

```typescript
// Theme Context (contexts/ThemeContext.tsx)
interface ThemeContextType {
  theme: 'light' | 'dark'
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'light',
  toggleTheme: () => {}
})

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState<'light' | 'dark'>(() =>
    localStorage.getItem('theme') as 'light' | 'dark' || 'light'
  )

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    localStorage.setItem('theme', newTheme)
    document.documentElement.classList.toggle('dark')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
```

**Tailwind Configuration** (tailwind.config.ts):
```typescript
export default {
  darkMode: 'class',  // Uses .dark class on HTML element
  theme: {
    extend: {
      colors: {
        // Primary brand color - Deep Orange (Creative Industrial)
        primary: {
          DEFAULT: 'var(--color-primary)',        /* #f97316 */
          hover: 'var(--color-primary-hover)',     /* #ea580c */
          light: 'var(--color-primary-light)',     /* #fdba74 */
        },
        // Secondary - Teal (Professional balance)
        secondary: {
          DEFAULT: 'var(--color-secondary)',       /* #14b8a6 */
          hover: 'var(--color-secondary-hover)',   /* #0d9488 */
        },
        // Accent - Electric Blue (Trustworthy tech)
        accent: {
          DEFAULT: 'var(--color-accent)',         /* #3b82f6 */
          hover: 'var(--color-accent-hover)',     /* #2563eb */
        },
        // Light mode
        background: 'hsl(var(--color-bg) / <alpha-value>)',
        foreground: 'hsl(var(--color-fg) / <alpha-value>)',
        // Dark mode override
        dark: {
          background: 'hsl(var(--color-dark-bg) / <alpha-value>)',
          foreground: 'hsl(var(--color-dark-fg) / <alpha-value>)',
        }
      }
    }
  }
}
```

**CSS Variables** (globals.css):
```css
:root {
  /* Primary - Deep Orange (Creative, Industrial) */
  --color-primary: 251 146 22;      /* #f97316 - orange-500 */
  --color-primary-hover: 234 88 12; /* #ea580c - orange-600 */
  --color-primary-light: 251 186 116; /* #fdba74 - orange-400 */

  /* Secondary - Teal */
  --color-secondary: 20 184 166;    /* #14b8a6 - teal-500 */
  --color-secondary-hover: 13 148 136; /* #0d9488 - teal-600 */

  /* Accent - Electric Blue */
  --color-accent: 59 130 246;       /* #3b82f6 - blue-500 */
  --color-accent-hover: 37 99 235;  /* #2563eb - blue-600 */

  /* Light mode */
  --color-bg: 0 0% 100%;            /* white */
  --color-fg: 222 47% 11%;          /* slate-900 */

  /* Dark mode */
  --color-dark-bg: 222 47% 4%;       /* slate-950 */
  --color-dark-fg: 210 40% 98%;      /* slate-50 */
}

.dark {
  --color-bg: var(--color-dark-bg);
  --color-fg: var(--color-dark-fg);
}
```

**Theme Toggle Component** (components/ui/ThemeToggle.tsx):
```typescript
import { motion } from 'framer-motion'
import { useTheme } from '@/contexts/ThemeContext'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <motion.button
      onClick={toggleTheme}
      className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
      whileTap={{ scale: 0.95 }}
      whileHover={{ rotate: 15 }}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <motion.span
        animate={{ rotate: theme === 'dark' ? 360 : 0 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        {theme === 'light' ? '🌙' : '☀️'}
      </motion.span>
    </motion.button>
  )
}
```

---

### Authentication Flow

```
┌─────────┐                    ┌──────────────┐
│ Browser │                    │ Better Auth  │
└────┬────┘                    └──────┬───────┘
     │                                │
     │ 1. POST /auth/register         │
     ├───────────────────────────────>│
     │                                │
     │ 2. Create Agency + User        │
     │    (DB transaction)            │
     │                                │
     │ 3. Generate JWT                │
     │<───────────────────────────────┤
     │                                │
     │ 4. Set httpOnly Cookie         │
     │    (auth_token)                │
     │                                │
     │ 5. Redirect to Dashboard       │
     │                                │
     │ 6. GET /dashboard              │
     │    (Cookie sent automatically) │
     │                                │
     │ 7. JWT Middleware verifies     │
     │    token                       │
     │                                │
     │ 8. Return Dashboard Data       │
     │<───────────────────────────────┤
```

---

### API Contract

**OpenAPI Specification**: `contracts/openapi.yaml`

**Key Endpoints**:

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | /auth/register | Register agency + user | No |
| POST | /auth/login | Login, get JWT | No |
| GET | /tasks | List agency tasks | Yes |
| POST | /tasks | Create task | Yes |
| PATCH | /tasks/{id} | Update task | Yes |
| DELETE | /tasks/{id} | Delete task | Yes |
| POST | /tasks/{id}/assign | Assign to user | Yes |
| POST | /time-entries | Log time | Yes |
| GET | /analytics/profitability | Get report | Yes |

**Response Format**:
```json
{
  "data": {...},
  "total": 42,
  "page": 1
}
```

**Error Format**:
```json
{
  "error": "Validation failed",
  "details": {
    "title": "Field required"
  }
}
```

---

### Security Architecture

#### JWT Token Structure

```json
{
  "sub": "user_uuid",
  "agency_id": "agency_uuid",
  "email": "user@agency.com",
  "exp": 1738368000,
  "iat": 1738364400
}
```

#### Tenant Isolation Strategy

1. **JWT contains agency_id claim**
2. **Middleware extracts agency_id on every request**
3. **All queries filter by agency_id**
4. **No cross-agency data access possible**

#### Input Validation

- **Backend**: Pydantic schemas on all endpoints
- **Frontend**: Client-side validation + server-side validation
- **SQL Injection**: SQLModel prevents via parameterized queries

---

### Performance Optimization

#### Backend

| Optimization | Implementation |
|-------------|----------------|
| Connection Pooling | Neon built-in pooling |
| Query Optimization | Composite indexes on (agency_id, status) |
| Response Compression | FastAPI GZipMiddleware |
| Caching | React Query client-side caching |

#### Frontend

| Optimization | Implementation |
|-------------|----------------|
| Code Splitting | Next.js dynamic imports |
| Image Optimization | next/image component |
| Streaming | Server Components with streaming |
| Animation Performance | GPU acceleration via Motion |

---

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Vercel                              │
│  (Frontend - Next.js 16)                                │
│  - Edge Functions for auth                              │
│  - Static assets for images/CSS                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ HTTPS
┌─────────────────────────────────────────────────────────┐
│                    Railway / Vercel                     │
│  (Backend - FastAPI)                                    │
│  - Containerized deployment                             │
│  - Auto-scaling on demand                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Neon PostgreSQL                      │
│  - Serverless, scales to zero                           │
│  - Automatic backups                                    │
└─────────────────────────────────────────────────────────┘
```

---

### Monitoring Strategy

#### Backend Metrics

- **Response time**: p50, p95, p99 (target: < 200ms p95)
- **Error rate**: 4xx, 5xx percentages
- **Database queries**: Slow query log (> 100ms)
- **JWT verification**: Failure rate

#### Frontend Metrics

- **LCP**: < 1.5s (Core Web Vitals)
- **FID**: < 100ms (First Input Delay)
- **CLS**: < 0.1 (Cumulative Layout Shift)
- **Error tracking**: Sentry for client errors

#### Logging

```python
# Backend structured logging
import logging

logger = logging.getLogger(__name__)
logger.info("Task created", extra={
    "task_id": task.id,
    "user_id": user.id,
    "agency_id": user.agency_id
})
```

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| JWT leaked | Tenant data breach | Short expiration, httpOnly cookies |
| Database downtime | Service unavailable | Neon auto-scaling, retry logic |
| CORS misconfig | XSS vulnerability | Whitelist origins only |
| Drag-and-drop failure | Core feature broken | Fallback to dropdown for status |
| High latency | Poor UX | Optimistic updates, loading states |

---

## Rollback Strategy

### Database Rollback

```bash
# Alembic downgrade
alembic downgrade -1

# Backup before migrations
pg_dump $DATABASE_URL > backup.sql
```

### Application Rollback

```bash
# Git revert
git revert HEAD

# Or deploy previous version
vercel deploy --prebuilt
```

---

## Definition of Done

- [ ] All 47 functional requirements implemented (FR-001 to FR-047)
- [ ] Backend tests: 80%+ coverage
- [ ] Frontend tests: Critical paths covered
- [ ] E2E tests: Login, drag task, create task
- [ ] LCP < 1.5s on dashboard
- [ ] Drag-and-drop latency < 500ms
- [ ] JWT authentication working
- [ ] Agency isolation verified
- [ ] OpenAPI spec matches implementation
- [ ] Production deployment ready
- [ ] Documentation complete (quickstart, API docs)

---

## Related Files

- [spec.md](./spec.md) - Feature requirements
- [research.md](./research.md) - Technology research
- [data-model.md](./data-model.md) - Database schema
- [contracts/openapi.yaml](./contracts/openapi.yaml) - API specification
- [quickstart.md](./quickstart.md) - Developer onboarding
- [AGENT_CONTEXT.md](./AGENT_CONTEXT.md) - AI agent reference

---

## Next Commands

1. `/sp.tasks` - Generate implementation tasks from this plan
2. `/sp.implement` - Execute implementation (after tasks generated)
3. `/sp.adr <title>` - Create ADR for architectural decisions
