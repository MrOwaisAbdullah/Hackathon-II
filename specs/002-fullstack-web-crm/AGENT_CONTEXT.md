# Agent Context: TeamFlow Web (Phase 2)

**Branch**: `002-fullstack-web-crm` | **Date**: 2026-01-03 | **Plan**: [plan.md](./plan.md)

> **Phase 10 (Complete Workflow Improvement)**: Planning phase for adding missing User/Project CRUD operations, mobile responsiveness, and navigation enhancements. See "Phase 10 Planning" section below for new requirements.

## Purpose

This file provides context for AI agents working on TeamFlow Phase 2. Use this to understand the project state, architecture decisions, and implementation guidelines.

---

## Project Overview

**TeamFlow Phase 2** is a full-stack agency CRM transforming the CLI task manager into a web application with:

- Kanban-style task board with drag-and-drop
- Real-time collaboration (10s polling)
- Team assignment and time tracking
- Profitability reporting
- Multi-tenant agency isolation

**Tech Stack**:
- Backend: FastAPI + SQLModel + Neon PostgreSQL
- Frontend: Next.js 16 (App Router) + Motion.dev + dnd-kit
- Auth: Better Auth + JWT

---

## Current State

### Completed

| Phase | Artifact | Status | Location |
|-------|----------|--------|----------|
| Spec | Feature Specification | ✅ Complete | `spec.md` |
| Spec | Clarification Session | ✅ Complete | `spec.md` (Clarifications section) |
| Plan | Research | ✅ Complete | `research.md` |
| Plan | Data Model | ✅ Complete | `data-model.md` |
| Plan | API Contracts | ✅ Complete | `contracts/openapi.yaml` |
| Plan | Quickstart | ✅ Complete | `quickstart.md` |
| Implementation | Phases 1-8 (Core Features) | ✅ Complete | `teamflow-web/` |
| Implementation | Phase 9 (Polish) | ✅ Complete | See tasks.md T150-T163 |
| Implementation | Phase 10 (Complete Workflow) | ✅ Complete | See tasks.md T173-T234 |
| Implementation | Phase 11 (Theme & UI Fixes) | ✅ Complete | See tasks.md T300-T325 |
| Features | Dashboard Components | ✅ Complete | UpcomingDeadlines, TaskDistributionChart |
| Features | Project Management | ✅ Complete | ProjectDrawer, ProjectForm, ProjectCard, Dynamic Routes |
| Features | Rich Text Editing | ✅ Complete | RichTextEditor, Markdown rendering |
| Features | Task Management | ✅ Complete | TaskDrawer with time entries, total time calc |

### Pending

| Phase | Task | Status |
|-------|------|--------|
| Validation | Lighthouse/WCAG audits (T160-T161) | ⏳ Requires dev server |
| Validation | Test suite execution (T166-T170) | ⏳ Requires dev server |
| Documentation | Analysis report update (T172) | ⏳ Pending |

---

## Key Architecture Decisions

### 1. Multi-Tenant Isolation

**Decision**: JWT-based tenant scoping via `agency_id` claim

**Rationale**:
- Single database, logical separation
- JWT verified per-request via middleware
- All queries automatically scoped to `agency_id`

**Implementation**:
```python
# Middleware extracts agency_id from JWT
async def verify_agency_access(token: str) -> AgencyUser:
    payload = jwt.decode(token, SECRET)
    return AgencyUser(agency_id=payload["agency_id"], user_id=payload["sub"])

# All endpoints use CurrentUser dependency
@router.get("/tasks")
def get_tasks(current_user: CurrentUser):
    # Query scoped via agency_id automatically
    pass
```

### 2. Drag-and-Drop Library

**Decision**: @dnd-kit/core (not react-beautiful-dnd)

**Rationale**:
- Active maintenance and TypeScript support
- Better performance and accessibility
- Hooks-based API for React 19 compatibility

### 3. Real-Time Updates

**Decision**: Polling every 10 seconds (not WebSockets)

**Rationale**:
- Simpler implementation for hackathon scope
- React Query supports `refetchInterval` natively
- Sufficient for 10-50 person agencies

### 4. Animation Library

**Decision**: Motion.dev (Framer Motion v11+)

**Rationale**:
- Declarative API with spring physics
- AnimatePresence for exit animations
- Layout animations for Kanban reordering

### 5. Conflict Resolution

**Decision**: Last-write-wins (FR-044 from clarifications)

**Rationale**:
- Simplest approach for hackathon scope
- No distributed locking complexity
- Optimistic updates with rollback on error

---

## Recent Feature Implementations (2026-01-05)

### Dashboard Improvements

**UpcomingDeadlines Component** (`components/dashboard/UpcomingDeadlines.tsx`)
- Replaces WorkflowProgress for more actionable deadline visibility
- Displays tasks with due dates sorted by urgency (overdue first, then upcoming)
- Shows overdue badges with pulsing animation for critical items
- Theme-aware priority badges (HIGH/MEDIUM/LOW) with light/dark variants
- Links tasks directly to their project pages for quick navigation
- Displays count summary: "X overdue · Y due soon"
- Limits to 8 most urgent tasks to prevent information overload
- Empty state with calendar icon when no deadlines exist
**File**: `teamflow-web/frontend/src/components/dashboard/UpcomingDeadlines.tsx`

**TaskDistributionChart Color Fix**
- **Issue**: Hex color values not compatible with chart rendering
- **Solution**: Convert HSL values to RGB for chart library compatibility
- **File**: `teamflow-web/frontend/src/components/dashboard/TaskDistributionChart.tsx`

### Project Management Enhancements

**ProjectDrawer Component** (`components/project/ProjectDrawer.tsx`)
- Side panel for editing project details (mirrors TaskDrawer design)
- Editable fields: name, description (rich text), status
- Rich text editor for project descriptions with markdown rendering
- Status dropdown with 4 options: Active, On Hold, Completed, Archived
- Auto-save detection with disabled save button when no changes
- Spring animation for slide-in/slide-out
- Backdrop blur overlay for focus
**File**: `teamflow-web/frontend/src/components/project/ProjectDrawer.tsx`

**Dynamic Project View Page** (`app/(main)/projects/[id]/page.tsx`)
- Dynamic route for individual project pages
- Displays project metadata: name, status badge, creation date
- Renders project description with markdown
- Stats grid: Total Tasks, Completed, Progress percentage
- Animated progress bar showing completion percentage
- Lists all project tasks with priority badges and due dates
- Back button navigation with arrow icon
- Loading state with spinner
- Error handling redirects to projects page on 404
**File**: `teamflow-web/frontend/src/app/(main)/projects/[id]/page.tsx`

**Project Status Field**
- Extended Project model with `status` enum field
- Four states: ACTIVE, ON_HOLD, COMPLETED, ARCHIVED
- Visual badges with color coding (emerald/amber/blue/gray)
- Theme-aware styling with light/dark mode support
- Status filtering on Projects page
**Files**: `backend/app/models/project.py`, `frontend/src/types/index.ts`

### Rich Text & Markdown Features

**Markdown Rendering System** (`lib/markdown.ts`)
- Custom `renderMarkdown()` function for converting markdown to HTML
- Supports: headers (H1-H3), bold, italic, links, lists, inline code, horizontal rules
- Escapes HTML first for security (XSS prevention)
- Applies Tailwind classes for consistent styling
- Theme-aware link colors (lime-600/lime-400)
- Used throughout: TaskCard descriptions, Project descriptions, TaskDrawer
**File**: `teamflow-web/frontend/src/lib/markdown.ts`

**RichTextEditor Component** (`components/task/RichTextEditor.tsx`)
- Toolbar with: Bold, Italic, H1, H2, List, Link, HR buttons
- Auto-expanding textarea based on content height
- Keyboard shortcuts: Ctrl+B (bold), Ctrl+I (italic)
- Always in edit mode (markdown renders on cards, editor in forms)
- Custom lime-themed scrollbar for overflow content
- Used in: TaskForm, TaskDrawer, ProjectDrawer
**File**: `teamflow-web/frontend/src/components/task/RichTextEditor.tsx`

### Task Management Improvements

**TaskDrawer Time Entries Display**
- Shows all time entries logged against the task
- Displays duration, description, date, and user who logged time
- Calculates and displays total time automatically
- "Add Time Entry" button opens TimeLoggingForm
- Time entries listed in chronological order
- Empty state when no time entries exist
**File**: `teamflow-web/frontend/src/components/task/TaskDrawer.tsx`

**Total Time Calculation Fix**
- **Issue**: Total time not displaying in TaskDrawer
- **Solution**: Added `useMemo` to sum time entry durations
- Displays formatted total (e.g., "2h 30m")
- Updates automatically when time entries change
**File**: `teamflow-web/frontend/src/components/task/TaskDrawer.tsx`

### Theme System Fixes

**Issue**: Hardcoded colors throughout the app causing inconsistent theming
**Solution**: Systematically replaced hardcoded colors with theme variables

| Component | Fixed |
|-----------|-------|
| `Button.tsx` (secondary) | `hover:bg-zinc-200` → `hover:bg-secondary/80` |
| `Button.tsx` (ghost) | `hover:bg-zinc-100` → `hover:bg-muted` |
| `Button.tsx` (outline) | `hover:bg-lime-50` → `hover:bg-accent/10` |
| `Button.tsx` (destructive) | Hardcoded rose → `bg-destructive/10` |
| TaskDrawer inputs | `focus:ring-primary` → `focus:ring-accent/10` |
| Time entries page | Updated all form inputs to use `border-input`, `border-accent` |
| Archive page | Search input uses theme variables |
| ProjectForm | All inputs and buttons themed |
| UserFilter | Dropdown uses `border-input`, `text-accent` |

### Custom Component Replacements

**Issue**: Native HTML elements (`<select>`, `<input type="date">`) can't be fully themed
**Solution**: Created custom components with full theme control

| Component | Path | Purpose |
|-----------|------|---------|
| `ProjectSelect` | `components/task/ProjectSelect.tsx` | Custom dropdown for project selection with folder icon, project descriptions, check icons |
| `AssigneeSelect` | `components/task/AssigneeSelect.tsx` | Custom dropdown for assignee selection with avatars |
| `DatePicker` | `components/task/DatePicker.tsx` | Custom date picker with calendar popover, month/year navigation |

### Bug Fixes

**TaskDrawer Save Button Bug**
- **Issue**: Save button always disabled despite making changes
- **Root Cause**: Date comparison using different formats (ISO datetime vs YYYY-MM-DD)
- **Solution**: Added `normalizeDate()` helper function to extract date part before comparison
**File**: `teamflow-web/frontend/src/components/task/TaskDrawer.tsx:112-124`

**DatePicker Navigation Enhancement**
- **Issue**: No way to navigate to different months or years
- **Solution**: Added previous/next month buttons with year transitions
**Features**:
- Left/right arrow buttons for month navigation
- Automatic year transition (Dec → Jan, Jan → Dec of previous year)
- Sync view with selected date when opening
**File**: `teamflow-web/frontend/src/components/task/DatePicker.tsx:44-98`

**TaskBoard Destructuring Fix**
- **Issue**: Tasks not displaying despite successful API responses
- **Root Cause**: Hook returns `{ tasks }` but component was looking for `{ data: tasks }`
- **Solution**: Fixed destructuring in TaskBoard component
**File**: `teamflow-web/frontend/src/components/board/TaskBoard.tsx:39`

**Backend Pydantic Forward Reference Fix**
- **Issue**: 500 error when creating/listing tasks due to Pydantic v2 forward reference
- **Root Cause**: `TaskRead.assignee: Optional["UserRead"]` causes issues
- **Solution**: Changed to `assignee: Optional[Any]` to avoid forward reference problems
**File**: `teamflow-web/backend/app/models/task.py:26`

---

## Phase 9 Implementation Lessons

### Project Structure Adjustments

**Backend: `src/` → `app/`**
- Original plan used `src/` directory structure
- Actual implementation uses `app/` for consistency with FastAPI best practices
- Core utilities organized under `app/core/` (security, rate_limit, logging)

**Frontend: App Router with Route Groups**
- `(auth)` - Public pages (login, register)
- `(main)` - Protected pages (dashboard, tasks, projects, etc.)
- Components organized by domain: `board/`, `dashboard/`, `task/`, `ui/`

### Theme Management

**"Eco-Modern" Visual Identity (DoQuanta Inspired)**
- **Foundation**: High-contrast Black & White foundation (`zinc-950` / `zinc-50`).
- **Primary Accent**: Vibrant **Lime Green** (`lime-400`) used for active states, indicators, and brand markers.
- **Sidebar**: Permanent **Dark Sidebar** (`zinc-950`) regardless of system theme for strong visual anchoring.
- **Typography**: High-impact headers using `font-black tracking-tighter uppercase`.
- **Elevation**: floating cards using `.card-float` with refined shadows (`shadow-slate-200/50`).

**Custom ThemeContext (not next-themes)**
- App uses `@/contexts/ThemeContext` with custom implementation
- Supports three modes: `'light'`, `'dark'`, `'system'`
- Theme stored in localStorage with system preference detection
- **Permanent Dark UI Components**: Sidebar and specific modals are forced to dark mode using the `.sidebar-dark` utility class to maintain brand consistency.


### Command Pattern

**Command Palette Implementation (T157)**
- CMD+K / Ctrl+K global shortcut
- Searchable commands grouped by category (Navigation, Actions, Settings)
- Framer Motion animations for open/close
- Keyboard navigation with circular selection

**Key Pattern: Keyboard Shortcuts**
```typescript
useEffect(() => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      setIsOpen(prev => !prev);
    }
  };
  document.addEventListener('keydown', handleKeyDown);
  return () => document.removeEventListener('keydown', handleKeyDown);
}, [isOpen]);
```

### Performance Optimizations

**1. Code Splitting (T159)**
- Dynamic imports for heavy components (charts, task board)
- `ssr: false` for dnd-kit components (client-only)
- Loading skeletons during component load

**2. GZip Compression (T162)**
- Starlette middleware for responses > 1KB
- Middleware order: GZip → Logging → CORS → Routers

**3. Structured Logging (T155)**
- JSON-formatted logs in production
- Request logging middleware with timing
- `log_api_call()` helper for consistent API logging

### Security Enhancements

**Rate Limiting (T163)**
- In-memory sliding window algorithm
- Per-endpoint limits (auth_register: 3/hour, auth_login: 5/minute)
- Client identification via X-Forwarded-For header

**Pattern**:
```python
from app.core.rate_limit import check_rate_limit

@router.post("/login")
def login(credentials: UserLogin, request: Request):
    check_rate_limit(request, "auth_login")
    # ... endpoint logic
```

### Accessibility Improvements

**ARIA Labels (T156)**
- Task cards: `role="button"`, `draggable="true"`, dynamic `aria-label`
- Task columns: `role="region"`, `aria-dropeffect="move"`
- Focus management: `focus-within:ring` for keyboard users

**Error Boundaries (T154)**
- Root error boundary at `app/error.tsx`
- Main app boundary at `app/(main)/error.tsx`
- Retry functionality with `reset()` action

**Skeleton Loading (T153)**
- `ChartSkeleton`, `ListSkeleton`, `WorkflowSkeleton` components
- Displayed during `isLoading` states
- Falls back to mock data when API unavailable

### API Endpoint Organization

**New Endpoints Added During Implementation**:
- `/v1/analytics` - Dashboard metrics
- `/v1/users` - Team member management
- `/v1/tasks/{id}/assign` - Task assignment
- `/v1/tasks/{id}/time-entries` - Time tracking

**Middleware Stack** (order matters):
```python
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Testing Patterns

**Contract Tests**
- OpenAPI validation with `openapi-spec-validator`
- Test both request/response schemas
- Located in `tests/contract/`

**Integration Tests**
- Full endpoint testing with test database
- Coverage for analytics, tasks, time entries
- Located in `tests/integration/`

### Common Pitfalls Encountered

| Issue | Solution |
|-------|----------|
| dnd-kit SSR errors | Use `ssr: false` in dynamic import |
| Theme context mismatch | Check `contexts/` for existing implementations |
| Rate limiting on multi-worker | Use Redis instead of in-memory for production |
| CORS preflight failures | Ensure OPTIONS method included in CORS config |
| JWT agency_id missing | Verify `agency_id` claim in token creation |

---

## Clarified Requirements

From spec clarification session:

| Question | Answer | FR Reference |
|----------|--------|--------------|
| Concurrent edit resolution | Last-write-wins | FR-044 |
| Network loss during drag | Cancel immediately, return to original column | FR-045 |
| Real-time updates | Polling every 10s + manual refresh | FR-046 |
| Deleted team member tasks | Tasks become unassigned (SET NULL) | FR-047 |

---

## Implementation Guidelines

### Backend Development

**When implementing FastAPI endpoints**:

1. **Use dependency injection** for session and auth:
```python
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

2. **Always scope queries to agency_id**:
```python
# GOOD
select(Task).where(Task.agency_id == current_user.agency_id)

# BAD - bypasses tenant isolation
select(Task)
```

3. **Return Pydantic schemas**, not raw models:
```python
@router.get("/tasks/{task_id}")
def get_task(task_id: str, session: SessionDep, current_user: CurrentUser):
    task = session.get(Task, task_id)
    return TaskRead.model_validate(task)
```

4. **Handle 404s gracefully**:
```python
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

### Frontend Development

**When implementing React components**:

1. **Use Server Components by default**:
```tsx
// GOOD - Server Component
export default function Dashboard() {
  const tasks = await fetchTasks()  // Direct DB access
  return <TaskBoard tasks={tasks} />
}
```

2. **Client Components only for interactivity**:
```tsx
'use client'
import {useDraggable} from '@dnd-kit/core'

export function TaskCard({task}: {task: Task}) {
  const {attributes, listeners, setNodeRef} = useDraggable({id: task.id})
  return <div ref={setNodeRef} {...listeners} {...attributes}>{task.title}</div>
}
```

3. **Use React Query for server state**:
```tsx
export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => fetch('/api/tasks').then(r => r.json()),
    refetchInterval: 10000,  // Poll every 10s
  })
}
```

4. **Motion for animations**:
```tsx
import {motion, AnimatePresence} from 'motion/react'

<AnimatePresence>
  {tasks.map(task => (
    <motion.div
      key={task.id}
      layout
      initial={{opacity: 0, y: 20}}
      animate={{opacity: 1, y: 0}}
      exit={{opacity: 0, scale: 0.9}}
    >
      {task.title}
    </motion.div>
  ))}
</AnimatePresence>
```

### Testing

**Backend tests**:
- Unit tests for services (80%+ coverage target)
- Integration tests for API endpoints
- Contract tests for OpenAPI compliance

**Frontend tests**:
- Vitest for unit tests (hooks, utilities)
- @testing-library/react for components
- Playwright for E2E (critical journeys only)

---

## MCP Tools to Use

When implementing, ALWAYS use these MCP tools:

1. **context7** - Fetch latest docs before coding:
   - `/fastapi/fastapi` - FastAPI patterns
   - `/vercel/next.js` - Next.js App Router
   - `/websites/dndkit` - dnd-kit usage
   - `/websites/motion-dev-docs` - Motion animations

2. **github** - For repo operations (if needed)

3. **chrome-devtools** - For E2E testing verification

---

## Skills and Agents Available

| Skill/Agent | Purpose | When to Use |
|-------------|---------|-------------|
| **`@.claude/agents/nextjs-frontend-architect.md`** ⭐ | **PRIMARY: Orchestrates all Next.js frontend implementation** | **USE FOR ALL FRONTEND TASKS** - Coordinates building-nextjs-apps, theme-factory, frontend-designer, and gemini-frontend-assistant |
| `@.claude/skills/building-nextjs-apps/` | Next.js 16 patterns, SSR-safe components | Reference for Next.js-specific patterns |
| `@.claude/skills/theme-factory/` | Professional color palettes | When establishing visual identity |
| `@.claude/skills/frontend-designer/` | UI design with animations | Before implementing UI components |
| `@.claude/skills/gemini-frontend-assistant/` | Generate frontend code from descriptions | For rapid UI code generation |
| `@.claude/skills/better-auth-integration/` | Auth patterns | When implementing auth flows |
| `.agent-better-auth-specialist` | Better Auth expert | Complex auth scenarios |
| `@.claude/agents/deployment-engineer/` | CI/CD and deployment | When setting up production |

**⭐ CRITICAL: For all frontend implementation, start with `nextjs-frontend-architect` agent.** This agent ensures SSR-safe patterns, proper Next.js 16 architecture, and coordinates all other frontend skills.

---

## File Locations Reference

### Specs
- Feature spec: `specs/002-fullstack-web-crm/spec.md`
- Implementation plan: `specs/002-fullstack-web-crm/plan.md`
- Data model: `specs/002-fullstack-web-crm/data-model.md`
- API contracts: `specs/002-fullstack-web-crm/contracts/openapi.yaml`
- Quickstart: `specs/002-fullstack-web-crm/quickstart.md`

### Code (to be created)
- Backend: `backend/src/`
- Frontend: `frontend/src/`
- Tests: `backend/tests/` and `frontend/tests/`

---

## Success Criteria

From spec.md:

1. User can register agency and login
2. Kanban board displays tasks in 4 columns
3. User can drag tasks between columns
4. User can create, edit, and delete tasks
5. User can assign tasks to team members
6. User can log time against tasks
7. Dashboard displays profitability metrics
8. Changes from other users appear within 10s
9. LCP < 1.5s on dashboard load
10. Drag-and-drop latency < 500ms

---

## Next Commands

1. `/sp.tasks` - Generate implementation tasks
2. `/sp.implement` - Execute implementation (after tasks generated)
3. `/sp.adr` - Create ADR for significant decisions

---

## Constitution Principles

All implementation MUST follow:

- **I. Specialized Agents & Skills First** - Use existing agents/skills
- **II. SOLID Principles** - Service layer separation
- **III. DRY** - Shared utilities in `/lib/`
- **IV. TDD** - Write tests before code
- **V. Spec-Driven Development** - Reference spec.md
- **VI. Type Safety** - Python type hints, TypeScript strict mode
- **VII. Security** - JWT scoping, input validation
- **VIII. Performance** - 200ms API, 2s LCP targets
- **IX. Code Style** - Black/isort, ESLint/Prettier
- **X. MCP Integration** - Use context7 for docs
- **XI. Skill Refinement** - Document errors in skills
- **XII. Documentation Lookup** - Always verify docs

---

## Performance Budgets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API endpoint latency | < 200ms p95 | Server logs |
| Dashboard LCP | < 1.5s | Lighthouse |
| Task board render | 60fps | Chrome DevTools Performance |
| Drag-and-drop latency | < 500ms | End-to-end timing |
| Polling interval | 10s | React Query config |

---

## Security Checklist

- [X] JWT verified on all protected endpoints
- [X] All queries scoped to agency_id
- [X] Input validation via Pydantic schemas
- [X] Passwords hashed with bcrypt
- [X] httpOnly cookies for JWT storage
- [X] CORS configured for frontend origin
- [X] SQL injection prevented (SQLModel)
- [X] XSS prevented (React escaping)
- [X] Rate limiting on auth endpoints (T163)
- [X] GZip compression on API responses (T162)

---

## Phase 10 Planning: Complete Dashboard Workflow

**Date**: 2026-01-03
**Plan**: See [plan.md](./plan.md) for detailed implementation plan

### Overview
Phase 10 adds missing CRUD functionality for Users and Projects, plus mobile responsiveness improvements. This completes the end-to-end workflow for agency teams.

### New User Model Fields (Phase 2)

The User model has been extended with four new fields for team management:

| Field | Type | Default | Purpose |
|-------|------|---------|---------|
| `active` | bool | True | Soft delete flag - queries filter `active=True` |
| `is_project_manager` | bool | False | Permission to create/edit projects |
| `password_expires_at` | datetime? | None | Temporary password expiration (7 days default) |
| `must_change_password` | bool | False | Force password change on first login |

**Migration**: `005_add_user_management_fields.py` (pending implementation)

### New API Endpoints (Planned)

**User Management** (`/api/v1/users`):
- `POST /users` - Create team member with auto-generated temp password
- `PATCH /users/{id}` - Update user fields (admin-only for role/permissions)
- `DELETE /users/{id}` - Soft delete (set active=False, unassign tasks)

**Permission Rules**:
- Only admins can create/update/delete users
- Only admins can modify `role` and `is_project_manager`
- Users can update their own name/email
- Cannot delete the last admin in an agency

### Mobile Responsiveness Patterns

**Navigation**:
- Hamburger menu on mobile (< 768px)
- Shadcn Sheet component with backdrop
- Auto-close on route change

**Dialogs**:
- Full-screen on mobile (< 640px): `fixed inset-0 m-0 h-full w-full`
- Centered modal on desktop: `sm:max-w-md sm:h-auto sm:rounded-lg`

**Touch Targets**:
- Minimum 44x44px per Apple HIG
- Proper padding on buttons and interactive elements

### Frontend Components to Create

| Component | Path | Purpose |
|-----------|------|---------|
| `UserForm.tsx` | `src/components/team/UserForm.tsx` | Add/edit team member modal |
| `UserCard.tsx` | `src/components/team/UserCard.tsx` | Enhanced user card with actions |
| `ProjectForm.tsx` | `src/components/project/ProjectForm.tsx` | Create/edit project modal |
| `ProjectCard.tsx` | `src/components/project/ProjectCard.tsx` | Enhanced project card with actions |
| `MobileNav.tsx` | `src/components/dashboard/MobileNav.tsx` | Hamburger menu for mobile |

### Implementation Phases

1. **Backend User CRUD** (P0) - Add POST, PATCH, DELETE endpoints to `users.py`
2. **Frontend Project Forms** (P0) - Create ProjectForm, ProjectCard components
3. **Frontend Team Forms** (P0) - Create UserForm, UserCard components
4. **Mobile Navigation** (P1) - Add hamburger menu with Sheet
5. **Archive Link** (P2) - Add navigation link to Archive page in Sidebar

---

This context should be used as reference for all implementation work on TeamFlow Phase 2.
