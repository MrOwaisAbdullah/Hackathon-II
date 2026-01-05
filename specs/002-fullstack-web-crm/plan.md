# Implementation Plan: TeamFlow Complete Dashboard Workflow (Phase 2 Improvement)

**Branch**: `002-fullstack-web-crm` | **Date**: 2026-01-03 | **Spec**: [spec-phase2-complete-workflow.md](./spec-phase2-complete-workflow.md)
**Input**: Feature specification for complete dashboard workflow - add projects, teams, settings, full CRUD functionality.

## Summary

This plan implements **missing CRUD functionality** for the Phase 2 web application to complete the end-to-end agency workflow. The foundation exists (authentication, task board, dashboard analytics), but critical user-facing workflows are incomplete:
- **Backend**: User management endpoints missing (POST, PATCH, DELETE for `/api/v1/users`)
- **Frontend**: Project CRUD forms missing
- **Frontend**: Team CRUD forms missing
- **Navigation**: Archive link missing from sidebar
- **Mobile**: Dashboard and board views need mobile optimization

This improvement adds full Create, Read, Update, Delete operations for **Team Management** and **Project Management**, enabling the complete agency workflow from onboarding team members to organizing projects and tracking deliverables.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.8+ (frontend)
**Primary Dependencies**:
  - Backend: FastAPI 0.115+, SQLModel 0.15+, Neon PostgreSQL, python-jose, bcrypt
  - Frontend: Next.js 16 (App Router), Motion.dev (Framer Motion v11+), @dnd-kit/core, React Query, Shadcn UI
**Storage**: Neon Serverless PostgreSQL (multi-tenant via agency_id scoping)
**Testing**: pytest (backend), vitest + @testing-library/react (frontend), Playwright (E2E)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge last 2 versions) + Mobile (320px+)
**Project Type**: Full-stack web application (backend + frontend)
**Performance Goals**: API < 200ms p95, Dashboard LCP < 1.5s, Drag-and-drop < 500ms
**Constraints**:
  - Multi-tenancy required (agency_id isolation)
  - Mobile-responsive (320px minimum width)
  - Touch targets >= 44x44px
  - SSR-safe patterns (Next.js 16 App Router)
**Scale/Scope**: 2-50 person agencies, 10-500 tasks, 5-50 projects per agency

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Specialized Agents & Skills First | ✅ PASS | Will use `nextjs-frontend-architect` agent for ALL frontend tasks. Backend agents checked: none applicable for basic CRUD. |
| II. SOLID Principles | ✅ PASS | Service layer pattern (`UserService`, `ProjectService`) enforces SRP. Dependency injection via FastAPI `Depends`. |
| III. DRY | ✅ PASS | Shared utilities in `/lib/` (frontend), `/core/` (backend). Shadcn components reused. |
| IV. TDD | ✅ PASS | Tests will be written before implementation: contract tests for API, integration tests for workflows. |
| V. Spec-Driven Development | ✅ PASS | This plan follows `/sp.specify` → `/sp.plan` → `/sp.tasks` workflow. |
| VI. Type Safety | ✅ PASS | Python type hints enforced, TypeScript strict mode enabled. Pydantic for all API models. |
| VII. Security | ✅ PASS | JWT authentication, agency_id scoping, rate limiting on auth endpoints, bcrypt password hashing. |
| VIII. Performance | ✅ PASS | Code splitting (dynamic imports), GZip middleware, 10s polling (not WebSockets), pagination for lists. |
| IX. Code Style | ✅ PASS | Black/isort (Python), ESLint/Prettier (TypeScript). |
| X. MCP Integration | ✅ PASS | context7 will be used for docs: `/fastapi/fastapi`, `/vercel/next.js`, `/websites/dndkit`, `/websites/motion-dev-docs`. |
| XI. Skill Refinement | ✅ PASS | Errors and solutions will be documented in relevant skills. |
| XII. Documentation Lookup | ✅ PASS | All library docs will be fetched via context7 before implementation. |

**All gates passed.** Proceeding with Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-crm/
├── spec.md                      # Original Phase 2 spec
├── spec-phase2-complete-workflow.md  # Phase 2 improvement spec (this plan's input)
├── plan.md                      # This file (/sp.plan command output)
├── research.md                  # Phase 0 output (research findings)
├── data-model.md                # Phase 1 output (entity definitions)
├── quickstart.md                # Phase 1 output (developer setup)
├── contracts/                   # Phase 1 output (OpenAPI specs)
│   └── openapi.yaml             # Complete API contract
├── AGENT_CONTEXT.md             # Agent-specific context (updated after Phase 1)
└── tasks.md                     # Phase 2 output (/sp.tasks - not in scope for this command)
```

### Source Code (repository root)

```text
teamflow-web/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       ├── users.py      # TO MODIFY: Add POST, PATCH, DELETE
│   │   │       ├── projects.py   # EXISTS: GET already, verify CRUD
│   │   │       └── auth.py       # EXISTS: Login, register
│   │   ├── core/
│   │   │   ├── config.py         # EXISTS: Settings, environment
│   │   │   ├── security.py       # EXISTS: JWT, password hashing
│   │   │   ├── deps.py           # EXISTS: CurrentUser, SessionDep
│   │   │   ├── logging.py        # EXISTS: Structured logging
│   │   │   └── rate_limit.py     # EXISTS: Rate limiting middleware
│   │   ├── models/
│   │   │   ├── user.py           # TO MODIFY: Add UserUpdate, PM fields
│   │   │   ├── task.py           # EXISTS: Task model
│   │   │   └── project.py        # EXISTS: Project model
│   │   ├── services/
│   │   │   ├── user_service.py   # TO MODIFY: Add create, update, delete
│   │   │   └── auth_service.py   # EXISTS: Authentication logic
│   │   └── main.py               # EXISTS: FastAPI app setup
│   ├── alembic/
│   │   └── versions/
│   │       └── 005_add_user_management_fields.py  # TO CREATE: Migration for new User fields
│   └── tests/
│       ├── contract/
│       │   └── test_users_contract.py  # TO CREATE: OpenAPI validation
│       └── integration/
│           └── test_users_api.py        # TO CREATE: User CRUD tests
│
└── frontend/
    └── src/
        ├── app/
        │   ├── (auth)/            # Public pages (exists)
        │   │   ├── login/
        │   │   └── register/
        │   ├── (main)/            # Protected pages
        │   │   ├── dashboard/
        │   │   │   └── page.tsx   # TO MODIFY: Responsive grid
        │   │   ├── projects/
        │   │   │   └── page.tsx   # TO MODIFY: Add CRUD UI
        │   │   ├── team/
        │   │   │   └── page.tsx   # TO MODIFY: Add CRUD UI
        │   │   ├── archive/
        │   │   │   └── page.tsx   # EXISTS: Archive page
        │   │   └── layout.tsx     # TO MODIFY: Add mobile nav
        │   ├── globals.css        # EXISTS: Theme CSS variables
        │   └── api/               # API proxy routes
        ├── components/
        │   ├── dashboard/
        │   │   ├── Sidebar.tsx    # TO MODIFY: Mobile drawer, Archive link
        │   │   ├── StatCard.tsx   # EXISTS: Stats display
        │   │   └── MobileNav.tsx  # TO CREATE: Hamburger + drawer
        │   ├── project/
        │   │   ├── ProjectForm.tsx  # TO CREATE: Create/edit modal
        │   │   └── ProjectCard.tsx  # TO CREATE: Project card with actions
        │   ├── team/
        │   │   ├── UserForm.tsx     # TO CREATE: Add/edit user modal
        │   │   └── UserCard.tsx     # TO CREATE: User card with actions
        │   ├── ui/                 # Shadcn components (exist)
        │   └── board/              # Task board components (exist)
        ├── lib/
        │   ├── api.ts              # EXISTS: API client
        │   ├── query.ts            # TO MODIFY: Add user/project mutations
        │   ├── permissions.ts      # TO CREATE: Permission hooks
        │   └── utils.ts            # EXISTS: Utility functions
        ├── hooks/
        │   ├── useTasks.ts         # EXISTS: Task hooks
        │   ├── useProjects.ts      # TO MODIFY: Add mutations
        │   └── useUsers.ts         # TO CREATE: User CRUD hooks
        └── types/
            └── index.ts            # TO MODIFY: Add UserUpdate, Project types
```

**Structure Decision**: Web application (Option 2) with separate backend/frontend directories. Backend follows FastAPI best practices with `/app/` structure (not `/src/`). Frontend uses Next.js 16 App Router with route groups `(auth)` and `(main)` for public/protected pages.

## Complexity Tracking

> **No constitution violations requiring justification.** All complexity is justified by spec requirements:
> - User CRUD is required for team management (FR-001 through FR-008-A)
> - Project CRUD is required for project organization (FR-009 through FR-015)
> - Mobile responsiveness is required for SC-009 and FR-009
> - Permission model (is_project_manager) is required by clarifications

---

## Phase 0: Research & Technical Decisions

This section documents research findings and technical decisions for all unknowns identified in the Technical Context.

### Research Topics

The following technical areas required investigation:

1. **User Model Extensions**: Password expiration, temporary password handling, soft delete patterns
2. **Permission Model**: is_project_manager flag access control
3. **Mobile Navigation Patterns**: Hamburger menu, slide-in drawer, backdrop handling
4. **Dialog Mobile Patterns**: Full-screen modals on small screens
5. **Audit Logging**: Existing log_api_call pattern for user CRUD
6. **Rate Limiting**: Existing patterns for user management endpoints

### Research Findings

#### 1. User Model Extensions

**Decision**: Add four new fields to User model
- `active: bool` (default=True) for soft delete
- `is_project_manager: bool` (default=False) for project permissions
- `password_expires_at: Optional[datetime]` for temporary password expiration
- `must_change_password: bool` (default=False) for first-login enforcement

**Rationale**:
- Soft delete pattern preserves data integrity (tasks remain assigned to deleted users in audit trail)
- PM flag enables granular permissions without complex role systems
- Password expiration addresses security requirement from clarifications

**Alternatives Considered**:
- Hard delete: Rejected (breaks task assignee references)
- Complex role system: Rejected (overkill for hackathon scope)
- Password expiration via middleware: Rejected (requires DB access on every request)

#### 2. Permission Model

**Decision**: Boolean flag `is_project_manager` with admin-only control

**Pattern**:
```python
# Backend: Enforce in endpoint
if update_data.get('is_project_manager'):
    if current_user.role != UserRole.admin:
        raise HTTPException(403, "Only admins can modify project manager status")

# Frontend: Hide checkbox from non-admins
{current_user.role === 'admin' && (
  <Checkbox name="is_project_manager" />
)}
```

**Rationale**: Simple, easy to understand, sufficient for agency size (2-50 people)

**Alternatives Considered**:
- RBAC with complex permissions: Rejected (over-engineering)
- Team-based permissions: Rejected (adds complexity without clear benefit)
- Anyone can be PM: Rejected (violates clarification requirement)

#### 3. Mobile Navigation Patterns

**Decision**: Hamburger menu + Sheet component (Shadcn) with backdrop

**Pattern**:
```tsx
// Hamburger button (md: breakpoint)
<Button variant="ghost" size="icon" className="md:hidden" onClick={() => setOpen(true)}>
  <Menu className="h-6 w-6" />
</Button>

// Sheet for drawer
<Sheet open={open} onOpenChange={setOpen}>
  <SheetContent side="left" className="w-64 sidebar-dark">
    <nav> {/* Navigation links */} </nav>
  </SheetContent>
</Sheet>
```

**Rationale**:
- Shadcn Sheet component provides consistent UX
- `.sidebar-dark` utility ensures permanent dark sidebar (brand consistency)
- Auto-close on route change prevents confusion

**Alternatives Considered**:
- Custom drawer implementation: Rejected (reinventing wheel)
- Bottom navigation bar: Rejected (considered for Phase 3, not in current scope)
- Always-visible sidebar on mobile: Rejected (insufficient screen space)

#### 4. Dialog Mobile Patterns

**Decision**: Full-screen modals on mobile (< 640px), centered modals on desktop

**Pattern**:
```tsx
<DialogContent className="
  fixed inset-0 m-0 h-full w-full rounded-none
  sm:max-w-md sm:h-auto sm:rounded-lg sm:p-6
">
  {/* Form content */}
</DialogContent>
```

**Rationale**:
- Full-screen on mobile maximizes usable space
- Centered modal on desktop follows established patterns
- Responsive classes handle breakpoint automatically

**Alternatives Considered**:
- Bottom sheet on mobile: Rejected (adds complexity, Sheet component already used for nav)
- Always centered: Rejected (poor UX on small screens)
- Separate mobile pages: Rejected (duplication, harder to maintain)

#### 5. Audit Logging

**Decision**: Use existing `log_api_call` pattern from `app.core.logging`

**Pattern**:
```python
from app.core.logging import log_api_call, get_logger

logger = get_logger(__name__)
log_api_call(
    logger,
    "POST /api/v1/users",
    "user_created",
    user_id=str(current_user.id),
    target_user_id=str(new_user.id)
)
```

**Rationale**:
- Consistent with existing patterns (T155)
- No new infrastructure required
- Structured JSON logs in production

**Alternatives Considered**:
- Separate audit table: Rejected (adds complexity, not required by spec)
- Third-party audit service: Rejected (overkill for current scope)
- No audit logging: Rejected (violates FR-034 through FR-036)

#### 6. Rate Limiting

**Decision**: Use existing `check_rate_limit` function with in-memory sliding window

**Pattern**:
```python
from app.core.rate_limit import check_rate_limit

@router.post("/users")
def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: CurrentUser,
):
    check_rate_limit(request, "user_create")
    # ... endpoint logic
```

**Limits**:
- `user_create`: 10/hour per agency
- `user_update`: 30/hour per agency
- `user_delete`: 10/hour per agency

**Rationale**:
- Consistent with existing auth endpoint rate limiting (T163)
- Prevents abuse while allowing legitimate bulk operations
- In-memory is sufficient for single-server deployment

**Alternatives Considered**:
- Redis-based rate limiting: Rejected (adds infrastructure dependency)
- No rate limiting: Rejected (security risk)
- Per-user limits: Rejected (too restrictive for team collaboration)

### Migration Strategy

**Alembic Migration**: `005_add_user_management_fields.py`

```python
from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # Add new columns to users table
    op.add_column('users', sa.Column('active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('is_project_manager', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('password_expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default='false'))

    # Create index on active for filtering
    op.create_index('ix_users_active', 'users', ['active'])

def downgrade():
    op.drop_index('ix_users_active', 'users')
    op.drop_column('users', 'must_change_password')
    op.drop_column('users', 'password_expires_at')
    op.drop_column('users', 'is_project_manager')
    op.drop_column('users', 'active')
```

---

## Phase 1: Data Model & API Contracts

This section defines the data entities and API contracts for the Phase 2 improvement.

### Data Model Additions

#### User Entity Extensions

**Existing Fields** (from spec.md):
```python
class User(SQLModel, table=True):
    id: UUID
    email: EmailStr
    name: str
    hashed_password: str
    role: UserRole  # admin, member, client
    agency_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
```

**New Fields** (Phase 2):
```python
# Phase 2: Soft delete and project management fields
active: bool = Field(default=True, index=True)
is_project_manager: bool = Field(default=False)
password_expires_at: Optional[datetime] = Field(default=None)
must_change_password: bool = Field(default=False)
```

#### Schemas

**UserCreate** (existing, enhanced):
```python
class UserCreate(SQLModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8)  # Optional for auto-generation
    role: UserRole = Field(default=UserRole.member)
    is_project_manager: bool = Field(default=False)  # NEW
```

**UserUpdate** (NEW):
```python
class UserUpdate(SQLModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_project_manager: Optional[bool] = None  # Admin-only
    # Password changes handled separately (not in this workflow)
```

**UserRead** (existing, enhanced):
```python
class UserRead(SQLModel):
    id: UUID
    email: EmailStr
    name: str
    role: UserRole
    agency_id: UUID
    active: bool  # NEW
    is_project_manager: bool  # NEW
    created_at: datetime
    updated_at: Optional[datetime]
```

**UserReadWithTempPassword** (NEW - for create response):
```python
class UserReadWithTempPassword(UserRead):
    temporary_password: str  # Only shown on creation to admin
```

### API Endpoints

#### User Management Endpoints

**POST /api/v1/users** - Create team member
```yaml
post:
  summary: Create a new team member
  tags: [users]
  security:
    - BearerAuth: []
  requestBody:
    content:
      application/json:
        schema:
          type: object
          properties:
            name:
              type: string
              minLength: 1
              maxLength: 100
            email:
              type: string
              format: email
            role:
              type: string
              enum: [admin, member, client]
              default: member
          required: [name, email]
  responses:
    '201':
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserReadWithTempPassword'
      description: User created with temporary password
    '400':
      description: Validation error or email already exists
    '403':
      description: Insufficient permissions (non-admin)
```

**PATCH /api/v1/users/{user_id}** - Update team member
```yaml
patch:
  summary: Update team member details
  tags: [users]
  security:
    - BearerAuth: []
  parameters:
    - name: user_id
      in: path
      required: true
      schema:
        type: string
        format: uuid
  requestBody:
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserUpdate'
  responses:
    '200':
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserRead'
    '400':
      description: Validation error
    '403':
      description: Insufficient permissions (non-admin or modifying PM flag)
    '404':
      description: User not found
```

**DELETE /api/v1/users/{user_id}** - Soft delete team member
```yaml
delete:
  summary: Soft delete a team member
  tags: [users]
  security:
    - BearerAuth: []
  parameters:
    - name: user_id
      in: path
      required: true
      schema:
        type: string
        format: uuid
  responses:
    '204':
      description: User soft deleted successfully
    '400':
      description: Cannot delete last admin
    '403':
      description: Insufficient permissions (non-admin)
    '404':
      description: User not found
```

#### Project Management Endpoints (Verify Existence)

**Existing endpoints to verify**:
- `POST /api/v1/projects` - Should exist, verify if not
- `PATCH /api/v1/projects/{project_id}` - Should exist, verify if not
- `DELETE /api/v1/projects/{project_id}` - Should exist, verify if not

### Frontend Data Structures

#### Types

```typescript
// types/index.ts - Additions

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'member' | 'client';
  agency_id: string;
  active: boolean;
  is_project_manager: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserCreate {
  name: string;
  email: string;
  role: 'admin' | 'member' | 'client';
  is_project_manager?: boolean;
}

export interface UserUpdate {
  name?: string;
  email?: string;
  role?: 'admin' | 'member' | 'client';
  is_project_manager?: boolean;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'on-hold' | 'completed';
  agency_id: string;
  created_at: string;
  updated_at?: string;
  // Computed
  task_count?: number;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  status?: 'active' | 'on-hold' | 'completed';
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: 'active' | 'on-hold' | 'completed';
}
```

---

## Implementation Architecture

### Backend Architecture

**Layer Structure**:
```
Request → Router → Endpoint → Service → Model → Database
                ↓
            Middleware (Auth, Rate Limit, Logging)
```

**Service Layer Pattern**:
```python
# app/services/user_service.py

class UserService:
    def create_user(
        self,
        user_data: UserCreate,
        agency_id: UUID,
        session: Session,
        admin_id: UUID  # For audit logging
    ) -> User:
        """Create user with auto-generated temp password."""
        pass

    def update_user(
        self,
        user_id: UUID,
        updates: UserUpdate,
        agency_id: UUID,
        admin_id: UUID,  # For permission check
        session: Session
    ) -> User:
        """Update user with PM permission enforcement."""
        pass

    def delete_user(
        self,
        user_id: UUID,
        agency_id: UUID,
        admin_id: UUID,  # For last-admin check
        session: Session
    ) -> None:
        """Soft delete user and unassign tasks."""
        pass
```

**Dependency Injection**:
```python
# app/core/deps.py (existing)

SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

### Frontend Architecture

**Component Hierarchy**:
```
(app) layout
  └── Sidebar (desktop) / MobileNav (mobile)
      └── (main) layout
          ├── dashboard/page
          ├── projects/page
          │   └── ProjectCard
          │       └── ProjectForm (modal)
          └── team/page
              └── UserCard
                  └── UserForm (modal)
```

**State Management**:
```typescript
// Server state (React Query)
useQuery(['users']) → List users
useMutation({ mutationFn: createUser }) → Create user
useMutation({ mutationFn: updateUser }) → Update user
useMutation({ mutationFn: deleteUser }) → Delete user

// Client state (Zustand - check if exists)
// Otherwise use component state for modals
```

**Permission System**:
```typescript
// lib/permissions.ts (NEW)

export function usePermissions() {
  // Get user from auth context
  const { user } = useAuth();

  return {
    canManageUsers: user?.role === 'admin',
    canManageProjects: user?.role === 'admin' || user?.is_project_manager,
    canEditUser: (userId: string) =>
      user?.id === userId || user?.role === 'admin',
    isProjectManager: user?.is_project_manager || false,
  };
}
```

### Rich Text Editor & Markdown Rendering

**Component**: `RichTextEditor` (`/components/task/RichTextEditor.tsx`)

**Features**:
- Markdown-based editing with toolbar
- Toolbar buttons: Bold, Italic, Headings (H1, H2), Lists, Links, Horizontal Rule
- Auto-expanding textarea (resizes based on content)
- Always in edit mode (no preview toggle - markdown renders on cards)
- Keyboard shortcuts displayed in tooltips

**Markdown Renderer** (`/lib/markdown.ts`):
```typescript
export function renderMarkdown(markdown: string): string {
  if (!markdown) return "";

  let html = markdown
    // Escape HTML first
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    // Headers
    .replace(/^### (.*$)/gim, '<h3 class="text-sm font-bold mt-2 mb-1">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-base font-bold mt-2 mb-1">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-lg font-bold mt-2 mb-1">$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener" class="text-lime-600 dark:text-lime-400 hover:underline">$1</a>')
    // Lists
    .replace(/^\- (.*$)/gim, '<li class="ml-4 list-disc">$1</li>')
    // Code (inline)
    .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 bg-muted rounded text-xs font-mono">$1</code>')
    // Horizontal rules
    .replace(/^---$/gim, '<hr class="my-2 border-border" />')
    // Line breaks
    .replace(/\n\n/g, '</p><p class="my-1">')
    .replace(/\n/g, '<br />');

  return `<p class="my-0">${html}</p>`;
}
```

**Task Form Enhancements** (`/components/task/TaskForm.tsx`):

**New Fields**:
- Due Date: Date picker with calendar icon
- Assignee: Dropdown of team members (fetched from `/api/v1/users`)
- Project: Dropdown of projects (fetched from `/api/v1/projects`)
- Description: RichTextEditor component instead of textarea

**Layout**:
- Wider modal: `max-w-3xl` instead of `max-w-md`
- 2-column grid for related fields (Assignee + Project)
- Full-width fields: Title, Description, Priority, Due Date
- Custom scrollbar: `scrollbar-lime` class for overflow

**Task Drawer Enhancements** (`/components/task/TaskDrawer.tsx`):

**Features**:
- Auto-fill form data using `useEffect` when task changes
- Priority full width (removed from 2-column grid)
- Custom scrollbar for content area
- Action buttons: Archive, Delete
- Form fields sync with task data on edit

### Theme-Aware Badge Styling

**Pattern for Dynamic Colors**:
```typescript
// In TaskCard component
const [isDark, setIsDark] = useState(false);

// Detect dark mode
useEffect(() => {
  const checkDark = () => {
    setIsDark(document.documentElement.classList.contains('dark'));
  };
  checkDark();
  const observer = new MutationObserver(checkDark);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  });
  return () => observer.disconnect();
}, []);

// Badge styles with light/dark variants
const getPriorityStyle = (priority: string) => {
  const styles = {
    LOW: {
      light: { backgroundColor: '#dcfce7', color: '#14532d' },
      dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
      dot: '#22c55e',
    },
    MEDIUM: {
      light: { backgroundColor: '#fef9c3', color: '#713f12' },
      dark: { backgroundColor: 'rgba(113, 63, 18, 0.3)', color: '#facc15' },
      dot: '#eab308',
    },
    HIGH: {
      light: { backgroundColor: '#fee2e2', color: '#7f1d1d' },
      dark: { backgroundColor: 'rgba(127, 29, 29, 0.3)', color: '#f87171' },
      dot: '#ef4444',
    },
  };
  return styles[priority as keyof typeof styles] || styles.LOW;
};

const priority = getPriorityStyle(task.priority);
const priorityStyle = isDark ? priority.dark : priority.light;
```

### Task Card Action Menu

**Dropdown Menu Pattern** (`/components/board/TaskCard.tsx`):

```typescript
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";

// Three-dot menu with actions
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <motion.button
      whileHover={{ rotate: 90, scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className="opacity-0 group-hover:opacity-100"
    >
      <MoreHorizontal size={16} strokeWidth={2.5} />
    </motion.button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end" className="w-48">
    <DropdownMenuLabel>Task Actions</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem onClick={handleEdit}>
      <Edit2 className="w-4 h-4 mr-2 text-lime-600" />
      Edit Task
    </DropdownMenuItem>
    <DropdownMenuItem onClick={handleArchive}>
      <Archive className="w-4 h-4 mr-2 text-blue-600" />
      Archive Task
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem
      onClick={handleDelete}
      className="text-rose-600 focus:text-rose-600"
    >
      <Trash2 className="w-4 h-4 mr-2" />
      Delete Task
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

---

## Dashboard Component Enhancements

### UpcomingDeadlines Component

**Component**: `UpcomingDeadlines` (`/components/dashboard/UpcomingDeadlines.tsx`)

**Purpose**: Replace WorkflowProgress with actionable deadline visibility, showing tasks due within 7 days sorted by urgency.

**Features**:
- Filters tasks: excludes DONE/ARCHIVED, must have due_date
- Sorts by urgency: overdue first (most overdue first), then upcoming (by due date)
- Limits to 8 most urgent tasks
- Displays count summary: "X overdue · Y due soon"
- Theme-aware priority badges (HIGH/MEDIUM/LOW) with light/dark variants
- Overdue badges with pulsing animation for critical items
- Links tasks directly to their project pages
- Empty state with calendar icon

**Date Utilities**:
```typescript
const getToday = () => {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return today;
};

const getDaysUntilDue = (dueDate: string): number => {
  const today = getToday();
  const due = new Date(dueDate);
  due.setHours(0, 0, 0, 0);
  return Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
};

const isOverdue = daysUntilDue < 0;
const isDueSoon = daysUntilDue >= 0 && daysUntilDue <= 7;
```

**Usage**:
```tsx
<UpcomingDeadlines tasks={tasks} projects={projects} />
```

### TaskDistributionChart Color Fix

**Issue**: Hex color values (#a3e635) not compatible with chart rendering library
**Solution**: Convert HSL values to RGB for compatibility

**Pattern**:
```typescript
const TASK_COLORS = {
  TODO: 'rgba(163, 230, 53, 0.8)',      // lime-400 to RGB
  DOING: 'rgba(250, 204, 21, 0.8)',     // yellow-400 to RGB
  REVIEW: 'rgba(251, 146, 60, 0.8)',    // orange-400 to RGB
  DONE: 'rgba(74, 222, 128, 0.8)'       // emerald-400 to RGB
};
```

---

## Project Management Enhancements

### ProjectDrawer Component

**Component**: `ProjectDrawer` (`/components/project/ProjectDrawer.tsx`)

**Purpose**: Side panel for editing project details, mirroring TaskDrawer design pattern.

**Features**:
- Slides in from right with spring animation
- Backdrop blur overlay for focus
- Editable fields: name, description (rich text), status
- Rich text editor for project descriptions
- Status dropdown with 4 options: Active, On Hold, Completed, Archived
- Auto-save detection (disabled button when no changes)
- Displays created date (read-only)
- Footer with Cancel/Save buttons

**State Management**:
```typescript
const [editedName, setEditedName] = useState("");
const [editedDescription, setEditedDescription] = useState("");
const [editedStatus, setEditedStatus] = useState<ProjectStatus | null>();

// Sync local state with project data
useEffect(() => {
  if (project) {
    setEditedName(project.name);
    setEditedDescription(project.description || "");
    setEditedStatus(project.status);
  }
}, [project]);

const hasChanges = project && (
  editedName !== project.name ||
  editedDescription !== (project.description || "") ||
  editedStatus !== project.status
);
```

**Usage**:
```tsx
<ProjectDrawer
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  project={selectedProject}
/>
```

### Dynamic Project View Page

**Route**: `/projects/[id]/page.tsx`

**Purpose**: Dynamic route for individual project pages with comprehensive project information.

**Features**:
- Uses Next.js 16 dynamic routes with `use()` hook for params
- Displays project metadata: name, status badge, creation date
- Renders project description with `renderMarkdown()`
- Stats grid: Total Tasks, Completed, Progress percentage
- Animated progress bar (fills from 0% to progress%)
- Lists all project tasks with priority badges and due dates
- Back button navigation with arrow icon
- Loading state with spinner
- Error handling redirects to projects page on 404

**Progress Calculation**:
```typescript
const projectTasks = tasks.filter((task) => task.project_id === id);
const completedTasks = projectTasks.filter((t) => t.status === "DONE").length;
const progress = projectTasks.length > 0
  ? Math.round((completedTasks / projectTasks.length) * 100)
  : 0;
```

**Status Badge Styling**:
```typescript
const getStatusStyle = (status: ProjectStatus) => {
  const styles = {
    active: {
      bg: "bg-emerald-500/10 dark:bg-emerald-500/20",
      text: "text-emerald-700 dark:text-emerald-400",
      border: "border-emerald-200 dark:border-emerald-800",
    },
    on_hold: {
      bg: "bg-amber-500/10 dark:bg-amber-500/20",
      text: "text-amber-700 dark:text-amber-400",
      border: "border-amber-200 dark:border-amber-800",
    },
    completed: {
      bg: "bg-blue-500/10 dark:bg-blue-500/20",
      text: "text-blue-700 dark:text-blue-400",
      border: "border-blue-200 dark:border-blue-800",
    },
    archived: {
      bg: "bg-gray-500/10 dark:bg-gray-500/20",
      text: "text-gray-700 dark:text-gray-400",
      border: "border-gray-200 dark:border-gray-800",
    },
  };
  return styles[status] || styles.active;
};
```

### Project Status Field

**Backend**: Extended Project model with `status` enum field

**Migration**: Add status column to projects table
```python
# Alembic migration
sa.Column('status', sa.String(), nullable=False, server_default='ACTIVE')
```

**Frontend**: Added ProjectStatus enum to types
```typescript
export enum ProjectStatus {
  ACTIVE = 'ACTIVE',
  ON_HOLD = 'ON_HOLD',
  COMPLETED = 'COMPLETED',
  ARCHIVED = 'ARCHIVED'
}
```

---

## Task Management Improvements

### TaskDrawer Time Entries Display

**Enhancement**: Added time entries section to TaskDrawer

**Features**:
- Lists all time entries for the task
- Displays duration, description, date, and user who logged time
- Calculates total time automatically with `useMemo`
- Formats total as "Xh Ym" (e.g., "2h 30m")
- "Add Time Entry" button opens TimeLoggingForm
- Empty state when no time entries exist

**Total Time Calculation**:
```typescript
const totalTime = useMemo(() => {
  if (!task?.time_entries || task.time_entries.length === 0) {
    return "0h 0m";
  }

  const totalMinutes = task.time_entries.reduce((sum, entry) => {
    return sum + entry.duration;
  }, 0);

  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  return `${hours}h ${minutes}m`;
}, [task?.time_entries]);
```

---

## Mobile-Responsive Design Strategy

### Breakpoints

```css
/* Tailwind breakpoints (existing) */
sm: 640px   /* Small phones */
md: 768px   /* Tablets, large phones */
lg: 1024px  /* Desktops */
xl: 1280px  /* Large desktops */
```

### Responsive Patterns

**Grid System**:
```tsx
{/* Dashboard stats - mobile first */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  <StatCard />  {/* 1 col mobile, 2 tablet, 4 desktop */}
</div>
```

**Navigation**:
```tsx
{/* Desktop: permanent sidebar */}
<Sidebar className="hidden md:flex" />

{/* Mobile: hamburger menu */}
<MobileNav className="md:hidden" />
```

**Dialogs**:
```tsx
<DialogContent className="
  fixed inset-0 m-0 h-full w-full rounded-none
  sm:max-w-md sm:h-auto sm:rounded-lg sm:p-6
">
  {/* Full screen on mobile, centered modal on desktop */}
</DialogContent>
```

### Touch Targets

**Minimum**: 44x44px (Apple HIG)
**Recommended**: 48x48px

```tsx
<button className="h-12 w-12 min-w-[48px]">
  <Icon className="h-5 w-5" />
</button>
```

---

## Theme & Visual Identity

### Eco-Modern Theme (DoQuanta Inspired)

**Core Colors**:
```css
:root {
  /* Light Mode */
  --brand-primary: 84 100% 59%;      /* Lime Green #a3e635 */
  --brand-secondary: 240 5.9% 10%;   /* Deep Black Zinc 900 */
  --background: 0 0% 100%;           /* Pure White */
  --foreground: 240 10% 3.9%;        /* Zinc 950 */
  --card: 0 0% 100%;                 /* Pure White */
  --accent: 83, 78%, 56%;             /* Lime 400 */
  --accent-hover: 83, 78%, 45%;       /* Lime 500 - for hover states */
  --radius: 0.5rem;
}

.dark {
  /* Dark Mode */
  --background: 240 10% 3.9%;        /* Zinc 950 */
  --foreground: 0 0% 98%;            /* Zinc 50 */
  --card: 240 10% 3.9%;              /* Zinc 950 */
  --accent: 83, 78%, 56%;             /* Lime 400 */
  --accent-hover: 83, 78%, 45%;       /* Lime 500 */
}

/* Permanent Dark Sidebar Utility */
.sidebar-dark {
  @apply bg-zinc-950 text-zinc-50 border-zinc-800;
}

/* Custom Scrollbar Styling */
.scrollbar-lime {
  scrollbar-width: thin;
  scrollbar-color: hsl(var(--accent)) hsl(var(--muted));
}

.scrollbar-lime::-webkit-scrollbar {
  width: 8px;
}

.scrollbar-lime::-webkit-scrollbar-track {
  background: hsl(var(--muted));
  border-radius: 4px;
}

.scrollbar-lime::-webkit-scrollbar-thumb {
  background: hsl(var(--accent));
  border-radius: 4px;
}

.scrollbar-lime::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--accent-hover));
}
```

**Typography**:
```css
/* Headers - bold, tight tracking */
.font-header {
  @apply font-black tracking-tighter uppercase;
}

/* Body - clean, legible */
.font-body {
  @apply font-normal;
}
```

**Utilities**:
```css
/* Card elevation */
.card-float {
  @apply shadow-lg shadow-slate-200/50 dark:shadow-none;
}

/* Hover feedback */
.hover-lift {
  @apply transition-transform duration-200 hover:-translate-y-0.5;
}
```

---

## Testing Strategy

### Backend Tests

**Contract Tests** (`tests/contract/test_users_contract.py`):
```python
def test_post_users_contracts(openapi_schema):
    """Verify POST /users matches OpenAPI spec."""
    # Validate request/response schemas

def test_patch_users_contracts(openapi_schema):
    """Verify PATCH /users/{id} matches OpenAPI spec."""

def test_delete_users_contracts(openapi_schema):
    """Verify DELETE /users/{id} matches OpenAPI spec."""
```

**Integration Tests** (`tests/integration/test_users_api.py`):
```python
async def test_create_user_as_admin(client, admin_token):
    """Test admin can create user."""

async def test_create_user_as_member_fails(client, member_token):
    """Test member cannot create user."""

async def test_update_project_manager_as_admin(client, admin_token):
    """Test admin can set PM flag."""

async def test_update_project_manager_as_member_fails(client, member_token):
    """Test member cannot set PM flag."""

async def test_delete_last_admin_fails(client, admin_token):
    """Test cannot delete last admin."""

async def test_delete_user_unassigns_tasks(client, admin_token):
    """Test tasks become unassigned."""
```

### Frontend Tests

**Unit Tests** (`components/team/UserForm.test.tsx`):
```typescript
describe('UserForm', () => {
  it('validates name is required');
  it('validates email format');
  it('shows PM checkbox only to admins');
  it('displays temp password after creation');
  it('shows loading state during submission');
});
```

**E2E Tests** (`e2e/user-crud.spec.ts`):
```typescript
test('complete user management workflow', async ({ page }) => {
  // Login as admin
  // Navigate to team page
  // Click Add Team Member
  // Fill form
  // Submit
  // Verify temp password shown
  // Edit user (set PM flag)
  // Delete user
  // Verify tasks unassigned
});
```

**Mobile Tests** (`e2e/mobile-responsiveness.spec.ts`):
```typescript
test('dashboard works on mobile viewport', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/dashboard');

  // Verify hamburger visible
  // Open menu
  // Verify stat cards stacked
});

test('user form full screen on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/team');
  await page.click('text=Add Team Member');

  // Verify dialog is full screen
  const dialog = await page.locator('[role="dialog"]');
  const box = await dialog.boundingBox();
  expect(box?.width).toBe(375);
});
```

---

## Security Considerations

### Authentication & Authorization

**All endpoints require JWT**:
```python
@router.post("/users")
def create_user(
    user_data: UserCreate,
    current_user: CurrentUser,  # From JWT
):
    # current_user.agency_id available for scoping
```

**Permission checks**:
```python
# Admin-only for user CRUD
if current_user.role != UserRole.admin:
    raise HTTPException(403, "Insufficient permissions")

# Admin-only for PM flag modification
if 'is_project_manager' in update_data:
    if current_user.role != UserRole.admin:
        raise HTTPException(403, "Only admins can modify project manager status")
```

### Input Validation

**Email uniqueness**:
```python
existing = session.exec(
    select(User).where(
        User.email == user_data.email,
        User.agency_id == current_user.agency_id
    )
).first()
if existing:
    raise ValueError("Email already exists in agency")
```

**Password requirements**:
```python
password: str = Field(min_length=8, max_length=100)
```

### Rate Limiting

**User management endpoints**:
```python
@router.post("/users")
def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: CurrentUser,
):
    check_rate_limit(request, "user_create")
```

### Audit Logging

**All user CRUD operations logged**:
```python
log_api_call(
    logger,
    "POST /api/v1/users",
    "user_created",
    user_id=str(current_user.id),
    target_user_id=str(new_user.id),
    agency_id=str(current_user.agency_id)
)
```

---

## Performance Optimizations

### Backend

**Database queries**:
```python
# Index on active field for filtering
active: bool = Field(default=True, index=True)

# Index on agency_id for multi-tenant queries (existing)
```

**Response compression**:
```python
# GZip middleware (existing)
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Frontend

**Code splitting**:
```typescript
// Dynamic imports for heavy components
const ProjectForm = dynamic(() => import('@/components/project/ProjectForm'), {
  loading: () => <Skeleton className="h-64 w-full" />,
  ssr: false
});
```

**Optimistic updates**:
```typescript
const mutation = useMutation({
  mutationFn: (data) => api.post('/users', data),
  onMutate: async (newUser) => {
    // Optimistic update
    queryClient.setQueryData(['users'], (old) => [...old, newUser]);
  },
  onError: (err) => {
    // Rollback on error
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});
```

**Drag-and-Drop Synchronous Updates**:
```typescript
// In TaskBoard handleDragEnd
const handleDragEnd = async (event: DragEndEvent) => {
  const { active, over } = event;
  const taskId = active.id as string;
  const overId = over.id as string;

  // Manually update cache FIRST (synchronous optimistic update)
  queryClient.setQueryData<Task[]>(
    ['tasks'],
    (old = []) =>
      old.map((t) =>
        t.id === taskId
          ? { ...t, status: overId as any, updated_at: new Date().toISOString() }
          : t
      )
  );

  // Now clear activeTask - the UI will show the task in the new column
  setActiveTask(null);

  // Then call the mutation in the background
  updateTask.mutate({
    id: taskId,
    data: { status: overId as any },
  });
};
```

---

## Implementation Phases

This section breaks down the implementation into phases based on the user's plan input.

### Phase 1: Backend User Management CRUD

**Priority**: P0 - Blocks all team management features
**Estimated Effort**: 4-6 hours

**Tasks**:
1. Add `UserUpdate` schema to `app/models/user.py`
2. Implement `create_user()` in `app/services/user_service.py`
3. Implement `update_user()` in `app/services/user_service.py`
4. Implement `delete_user()` in `app/services/user_service.py`
5. Add POST endpoint to `app/api/endpoints/users.py`
6. Add PATCH endpoint to `app/api/endpoints/users.py`
7. Add DELETE endpoint to `app/api/endpoints/users.py`
8. Add password expiration fields to User model
9. Add `is_project_manager` field to User model
10. Implement audit logging for user CRUD operations
11. Create and run Alembic migration

**Acceptance Criteria**:
- [ ] POST /api/v1/users creates user with hashed password, sets password_expires_at (now + 7 days), must_change_password=True
- [ ] PATCH /api/v1/users/{id} updates name, email, role, is_project_manager (admin-only for PM flag)
- [ ] DELETE /api/v1/users/{id} soft-deletes (active=False), unassigns all tasks
- [ ] Returns 403 when non-admin tries to modify is_project_manager flag
- [ ] Returns 400 when attempting to delete last admin
- [ ] Audit log entries created for all user CRUD operations

### Phase 2: Mobile-Responsive Dashboard Layout

**Priority**: P0 - Blocks all mobile UX work
**Estimated Effort**: 6-8 hours

**Tasks**:
1. Create MobileNav component with hamburger + drawer
2. Add Archive link to Sidebar
3. Update Sidebar for mobile responsiveness
4. Update dashboard page with responsive grid
5. Add mobile-specific CSS utilities

**Acceptance Criteria**:
- [ ] Sidebar collapses to hamburger on < 768px
- [ ] Hamburger opens slide-in drawer with backdrop
- [ ] Stat cards stack vertically on mobile
- [ ] Touch targets >= 44x44px
- [ ] Archive link visible in mobile drawer

### Phase 3: Frontend Project Management

**Priority**: P1 - Core workflow functionality
**Estimated Effort**: 8-10 hours

**Tasks**:
1. Create ProjectForm component (create/edit modal)
2. Create ProjectCard component with actions
3. Add project mutation hooks to query.ts
4. Update Projects page with CRUD UI
5. Implement project deletion flow

**Acceptance Criteria**:
- [ ] Create/edit/delete workflows working
- [ ] Permission-based UI hiding
- [ ] Loading states on mutations
- [ ] Error toasts on failures
- [ ] Mobile: Full-screen dialog on small screens

### Phase 4: Frontend Team Management

**Priority**: P1 - Core workflow functionality
**Estimated Effort**: 10-12 hours

**Tasks**:
1. Create UserForm component (add/edit modal)
2. Create UserCard component with actions
3. Add user mutation hooks to query.ts
4. Create usePermissions hook
5. Update Team page with CRUD UI
6. Implement user deletion flow

**Acceptance Criteria**:
- [ ] Create/edit/delete workflows working
- [ ] Admin-only access enforced
- [ ] Temporary password displayed after creation
- [ ] "Cannot delete last admin" error handling
- [ ] PM checkbox visible to admins only

### Phase 5: Navigation Enhancement

**Priority**: P2 - UX improvement
**Estimated Effort**: 2-3 hours

**Tasks**:
1. Add Archive navigation item to Sidebar
2. Position between Time Entries and Settings
3. Add active state highlighting
4. Test navigation from all pages

**Acceptance Criteria**:
- [ ] Archive link in sidebar
- [ ] Archive positioned correctly
- [ ] Archive highlights when active

---

## Definition of Done

This feature improvement is complete when:

### Backend
- [ ] POST /api/v1/users creates user with temp password (7-day expiration)
- [ ] PATCH /api/v1/users/{id} updates user with PM permission check
- [ ] DELETE /api/v1/users/{id} soft-deletes and unassigns tasks
- [ ] Last admin cannot be deleted (returns 400)
- [ ] Non-admins cannot modify PM flag (returns 403)
- [ ] Audit logs created for all user CRUD
- [ ] Migration run successfully
- [ ] All contract tests passing
- [ ] All integration tests passing

### Frontend - Projects
- [ ] ProjectForm component created
- [ ] ProjectCard component created
- [ ] Projects page has create/edit/delete UI
- [ ] Permission-based button hiding
- [ ] Loading states on mutations
- [ ] Error toasts display
- [ ] Mobile: Full-screen dialogs
- [ ] Mobile: Touch-friendly buttons

### Frontend - Team
- [ ] UserForm component created
- [ ] UserCard component created
- [ ] Team page has add/edit/delete UI
- [ ] Admin-only access enforced
- [ ] Temp password shown after creation
- [ ] PM checkbox admin-only
- [ ] Mobile: Form fields stack
- [ ] Mobile: Large touch targets

### Navigation
- [ ] Archive link in sidebar
- [ ] Archive positioned correctly
- [ ] Archive highlights when active

### Mobile Responsiveness
- [ ] Sidebar hamburger on < 768px
- [ ] Drawer with backdrop
- [ ] Stat cards stack
- [ ] No horizontal scroll
- [ ] Touch targets >= 44x44px
- [ ] Dialogs full-screen on mobile

### E2E Tests
- [ ] User CRUD workflow test passes
- [ ] Project CRUD workflow test passes
- [ ] Permission denial test passes
- [ ] Mobile viewport tests pass

---

## Quick Start Commands

```bash
# Backend - Run migration
cd teamflow-web/backend
uv run alembic upgrade head

# Backend - Start server
uv run uvicorn app.main:app --reload

# Frontend - Start dev server
cd teamflow-web/frontend
npm run dev

# Run tests
cd teamflow-web/backend && uv run pytest
cd teamflow-web/frontend && npm run test
```

---

## References

- **Spec**: `specs/002-fullstack-web-crm/spec-phase2-complete-workflow.md`
- **Agent Context**: `specs/002-fullstack-web-crm/AGENT_CONTEXT.md`
- **Module Prompt**: `module_prompts/phase-2-complete-workflow-plan.prompt.md`
- **Constitution**: `.specify/memory/constitution.md`
