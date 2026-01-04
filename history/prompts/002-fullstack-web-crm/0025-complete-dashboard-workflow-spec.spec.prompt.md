---
id: "0025"
title: "Complete Dashboard Workflow Spec"
stage: spec
date: "2025-01-03"
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-crm
branch: 002-fullstack-web-crm
user: owais_abdullah
command: /sp.specify
labels: ["spec","crud","team-management","project-management","phase-2"]
links:
  spec: specs/002-fullstack-web-crm/spec-phase2-complete-workflow.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fullstack-web-crm/spec-phase2-complete-workflow.md
  - specs/002-fullstack-web-crm/checklists/requirements-phase2-complete-workflow.md
tests:
  - No tests created (spec phase only)
---

## Prompt

Complete the full workflow of the dashboard from start to end - add projects, teams, settings, adding, editing, assigning, deleting tasks, log time. All CRUD functionality for Projects and Team management must work end-to-end.

This is Phase 2 improvement work (not Phase 3). The backend and frontend foundation is already built (see specs/002-fullstack-web-crm/spec.md). This improvement focuses on completing missing CRUD operations for Projects and Team management.

## Current State Analysis

### Backend Status (Partial Implementation)
| Endpoint | GET | POST | PATCH | DELETE |
|----------|-----|------|-------|--------|
| `/api/v1/auth` | ✅ | ✅ | ✅ | ✅ |
| `/api/v1/tasks` | ✅ | ✅ | ✅ | ✅ |
| `/api/v1/projects` | ✅ | ✅ | ✅ | ✅ |
| `/api/v1/time-entries` | ✅ | ✅ | ✅ | ✅ |
| `/api/v1/analytics` | ✅ | N/A | N/A | N/A |
| `/api/v1/users` | ✅ | ❌ | ❌ | ❌ |

### Frontend Status (Partial Implementation)
| Page | View | Create | Edit | Delete |
|------|------|--------|------|--------|
| `/dashboard` | ✅ | N/A | N/A | N/A |
| `/tasks` | ✅ | ✅ | ✅ | ✅ |
| `/projects` | ⚠️ | ❌ | ❌ | ❌ |
| `/team` | ⚠️ | ❌ | ❌ | ❌ |
| `/time-entries` | ✅ | ✅ | ✅ | ✅ |
| `/settings` | ✅ | N/A | ✅ | N/A |
| `/archive` | ✅ | N/A | N/A | ✅ (restore) |

### Navigation Status
- Sidebar: Missing **Archive** link
- All other pages: Linked correctly

## User Stories & Requirements

### US3-A: Team Management CRUD
*As an Agency Admin, I want to manage team members so that I can control who has access to my agency.*

**Required Operations:**
1. **Create Team Member**
   - Fields: Full Name, Email, Password (temporary), Role (Admin/Member)
   - Validation: Email must be unique within agency
   - Security: At least one admin must remain

2. **Edit Team Member**
   - Fields: Full Name, Email, Role
   - Password change: Separate flow (not in edit form)

3. **Delete Team Member**
   - Behavior: Soft delete (set `active=False`)
   - Side effect: Assigned tasks become unassigned
   - Validation: Cannot delete last admin

### US2-B: Project Management CRUD
*As a Project Manager, I want to manage projects so that I can organize my team's work.*

**Required Operations:**
1. **Create Project**
   - Fields: Name (required), Description (optional), Status (active/on-hold/completed)

2. **Edit Project**
   - Fields: Same as create
   - Preserve: Creation date, creator

3. **Delete Project**
   - Behavior: Soft delete with confirmation
   - Warning: "This will archive all tasks in this project"
   - Restore: Available via Archive page

### US4-C: Navigation Enhancement
*As a User, I want to access the Archive page from the sidebar so that I can restore deleted items.*

**Required Changes:**
- Add "Archive" link to Sidebar navigation
- Use `Archive` icon from lucide-react
- Position: Between "Time Entries" and "Settings"

## Technical Implementation Requirements

### Part 1: Backend User Management (Python/FastAPI)

**File: `teamflow-web/backend/app/services/user_service.py`**

Add these methods to `UserService` class:

```python
def create_user(self, user_data: UserCreate, agency_id: str, session: Session) -> User:
    """Create a new user in the agency.

    Requirements:
    - Hash password with bcrypt
    - Verify email uniqueness within agency
    - Set default role if not provided
    - Validate: at least one admin exists after creation
    """

def update_user(self, user_id: UUID, agency_id: UUID, updates: UserUpdate, session: Session) -> User:
    """Update user information.

    Requirements:
    - Allow updating: name, email, role
    - Validate email uniqueness (excluding current user)
    - Prevent removing last admin
    """

def delete_user(self, user_id: UUID, agency_id: UUID, session: Session) -> None:
    """Soft delete a user.

    Requirements:
    - Set active=False instead of hard delete
    - Unassign all tasks (set assignee_id to NULL)
    - Prevent deleting last admin
    """
```

**File: `teamflow-web/backend/app/api/endpoints/users.py`**

Add these endpoints:

```python
@router.post("", response_model=UserRead, status_code=201)
def create_user(
    user_data: UserCreate,
    current_user: CurrentUser,
    session: SessionDep,
) -> User:
    """Create a new team member.

    Requirements:
    - Only admins can create users
    - Validate email uniqueness
    - Generate temporary password or use provided one
    """

@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: UUID,
    updates: UserUpdate,
    current_user: CurrentUser,
    session: SessionDep,
) -> User:
    """Update user information.

    Requirements:
    - Only admins can update users
    - Prevent removing last admin
    """

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> None:
    """Delete/deactivate a user.

    Requirements:
    - Only admins can delete users
    - Soft delete (active=False)
    - Prevent deleting last admin
    """
```

**Schemas Required:**
- `UserCreate`: name, email, password, role
- `UserUpdate`: name (optional), email (optional), role (optional)

### Part 2: Frontend Project Management (Next.js/React)

**File: `teamflow-web/frontend/src/components/project/ProjectForm.tsx`** (NEW)

```typescript
interface ProjectFormProps {
  mode: 'create' | 'edit';
  project?: Project;
  onSuccess: () => void;
  onCancel: () => void;
}

Required features:
- Modal/Dialog using Shadcn UI
- Form fields: Name (required), Description (textarea), Status (select)
- Validation: Name required, max 100 chars
- Loading state during mutation
- Error handling with user-friendly messages
```

**File: `teamflow-web/frontend/src/components/project/ProjectCard.tsx`** (ENHANCE)

```typescript
Add these action buttons:
- Edit button (pencil icon)
- Delete button (trash icon)
- Dropdown menu for actions on mobile
```

**File: `teamflow-web/frontend/src/app/(main)/projects/page.tsx`** (MODIFY)

```typescript
Add to page header:
- "New Project" button (opens create modal)
- Pass edit/delete handlers to ProjectCard components
```

**File: `teamflow-web/frontend/src/lib/query.ts`** (ADD)

```typescript
export function useCreateProject() {
  // POST /api/v1/projects
}

export function useUpdateProject() {
  // PATCH /api/v1/projects/{id}
}

export function useDeleteProject() {
  // DELETE /api/v1/projects/{id}
}
```

### Part 3: Frontend Team Management (Next.js/React)

**File: `teamflow-web/frontend/src/components/team/UserForm.tsx`** (NEW)

```typescript
interface UserFormProps {
  mode: 'create' | 'edit';
  user?: User;
  onSuccess: () => void;
  onCancel: () => void;
}

Required features:
- Modal/Dialog using Shadcn UI
- Form fields:
  - Full Name (required)
  - Email (required, email validation)
  - Role (select: Admin/Member)
  - Password (required for create only)
- Validation: Email format, password min 8 chars
- Loading state during mutation
- Error handling with user-friendly messages
```

**File: `teamflow-web/frontend/src/components/team/UserCard.tsx`** (ENHANCE)

```typescript
Add these action buttons:
- Edit button (pencil icon)
- Delete button (trash icon)
- Dropdown menu for actions on mobile
```

**File: `teamflow-web/frontend/src/app/(main)/team/page.tsx`** (MODIFY)

```typescript
Add to page header:
- "Add Team Member" button (opens create modal)
- Pass edit/delete handlers to UserCard components
```

**File: `teamflow-web/frontend/src/lib/query.ts`** (ADD)

```typescript
export function useCreateUser() {
  // POST /api/v1/users
}

export function useUpdateUser() {
  // PATCH /api/v1/users/{id}
}

export function useDeleteUser() {
  // DELETE /api/v1/users/{id}
}
```

### Part 4: Navigation Enhancement

**File: `teamflow-web/frontend/src/components/dashboard/Sidebar.tsx`** (MODIFY)

Add to navigation items array:

```typescript
{
  name: "Archive",
  href: "/archive",
  icon: Archive,
  current: pathname === "/archive",
}
```

Position: Between "Time Entries" and "Settings"

## Implementation Directives

### Order of Implementation
1. **Backend User CRUD** (enables team management)
2. **Frontend Project Forms** (independent feature)
3. **Frontend Team Forms** (depends on backend user CRUD)
4. **Navigation Enhancement** (quick win, independent)

### Code Patterns to Follow

**For Backend:**
- Follow existing patterns in `task_service.py` and `project_service.py`
- Use Pydantic models for validation
- Return 404 for non-existent resources
- Return 403 for permission errors
- Return 422 for validation errors

**For Frontend:**
- Follow existing patterns in `TaskForm.tsx` and `TaskDrawer.tsx`
- Use TanStack Query mutations with optimistic updates
- Use Shadcn UI components (Dialog, Form, Button)
- Show loading spinners during mutations
- Show error toasts on failure
- Invalidate queries on success

### Testing Requirements

**Backend Tests:**
- Unit tests for `create_user`, `update_user`, `delete_user`
- Integration tests for new endpoints
- Test email uniqueness validation
- Test last-admin protection

**Frontend Tests:**
- Component tests for forms (validation, loading, error states)
- E2E tests for complete CRUD workflows

## Success Criteria

### Backend
- [ ] POST /api/v1/users creates new user
- [ ] PATCH /api/v1/users/{id} updates user
- [ ] DELETE /api/v1/users/{id} soft-deletes user
- [ ] Cannot delete last admin (400 or 403 error)
- [ ] Email uniqueness enforced within agency

### Frontend Projects
- [ ] "New Project" button opens modal
- [ ] Create form validates name required
- [ ] Edit button opens pre-filled modal
- [ ] Delete shows confirmation dialog
- [ ] All mutations show loading states
- [ ] Projects list refreshes after mutations

### Frontend Team
- [ ] "Add Team Member" button opens modal
- [ ] Create form validates email format
- [ ] Edit button opens pre-filled modal
- [ ] Delete shows confirmation with warning
- [ ] Cannot delete last admin (error message)
- [ ] Team list refreshes after mutations

### Navigation
- [ ] Archive link visible in sidebar
- [ ] Archive link navigates to /archive

## Output Requirement

Implement all missing CRUD functionality following the specifications above.
Ensure consistent patterns with existing code.
Test all workflows end-to-end before completion.

## Response snapshot

Created comprehensive specification for TeamFlow Complete Dashboard Workflow (Phase 2 Improvement).

**Specification File**: `specs/002-fullstack-web-crm/spec-phase2-complete-workflow.md`

**User Stories Defined**:
1. **US3-A: Team Management CRUD (P1)** - Add, edit, delete team members with validation
2. **US2-B: Project Management CRUD (P1)** - Create, edit, delete projects with task archival
3. **US4-C: Navigation Enhancement (P3)** - Add Archive link to sidebar

**Requirements Specified**:
- 30 Functional Requirements (FR-001 through FR-030)
- 10 Success Criteria (SC-001 through SC-010)
- 7 Edge Cases identified
- Key Entities: User, UserCreate, UserUpdate, Project, ProjectCreate, ProjectUpdate

**Implementation Phases**:
1. Backend User CRUD (POST, PATCH, DELETE endpoints)
2. Frontend Project Forms (Create, Edit, Delete modals)
3. Frontend Team Forms (Add, Edit, Delete modals)
4. Navigation Enhancement (Archive link)

**Validation Result**: ✅ PASSED
- All content quality checks passed
- All requirement completeness checks passed
- No [NEEDS CLARIFICATION] markers
- Specification is ready for `/sp.plan` or implementation

## Outcome

- ✅ Impact: High - Completes critical CRUD functionality for team and project management, enabling full agency workflow
- 🧪 Tests: Spec phase only - no tests created yet
- 📁 Files: 2 files created
  - `specs/002-fullstack-web-crm/spec-phase2-complete-workflow.md` (specification)
  - `specs/002-fullstack-web-crm/checklists/requirements-phase2-complete-workflow.md` (validation checklist)
- 🔁 Next prompts: `/sp.plan` to create implementation plan, or proceed directly with implementation using the module prompt at `module_prompts/phase-2-complete-workflow-implement.prompt.md`
- 🧠 Reflection: Specification built upon existing 002-fullstack-web-crm foundation. User provided comprehensive context about current state analysis and technical requirements. All acceptance criteria are testable and measurable.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASSED - All checklist items validated successfully
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - Specification complete and ready for implementation
