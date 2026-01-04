# Phase 2: Complete Dashboard Workflow Implementation Plan

**Target Feature**: 002-fullstack-web-crm (Phase 2 Improvement)
**Specification**: `specs/002-fullstack-web-crm/spec-phase2-complete-workflow.md`
**Context**: `specs/002-fullstack-web-crm/plan.md` + `specs/002-fullstack-web-crm/AGENT_CONTEXT.md`
**Focus**: Mobile-Responsive UI/UX + Complete End-to-End Workflow Functionality

---

## Context Summary

The Phase 2 web application foundation exists but has critical gaps:
- **Backend**: User CRUD endpoints missing (POST, PATCH, DELETE for `/api/v1/users`)
- **Frontend**: Project CRUD forms missing
- **Frontend**: Team CRUD forms missing
- **Navigation**: Archive link missing from sidebar
- **Mobile Responsiveness**: Dashboard and board views need mobile optimization

This plan addresses ALL gaps while ensuring a **polished, mobile-first user experience** that follows the established "Eco-Modern" visual identity.

---

## Existing Foundation (Use These!)

### 🎨 Theme: "Eco-Modern" (DoQuanta Inspired)

**Core Visual Identity**:
- **Foundation**: High-contrast Black & White (`zinc-950` / `zinc-50`)
- **Primary Accent**: Vibrant **Lime Green** (`#a3e635` / `lime-400`)
- **Sidebar**: **Permanent Dark Sidebar** (`zinc-950`) regardless of system theme
- **Typography**: `font-black tracking-tighter uppercase` for high-impact headers
- **Elevation**: `.card-float` utility with `shadow-slate-200/50` refined shadows

**CSS Variables** (already in `globals.css`):
```css
:root {
  /* Light Mode */
  --brand-primary: 84 100% 59%;      /* Lime Green #a3e635 */
  --brand-secondary: 240 5.9% 10%;   /* Deep Black Zinc 900 */
  --background: 210 40% 98%;         /* Slate 50 */
  --foreground: 240 10% 3.9%;        /* Zinc 950 */
  --card: 0 0% 100%;                 /* Pure White */
  --radius: 0.5rem;
}

.dark {
  /* Dark Mode */
  --background: 240 10% 3.9%;        /* Zinc 950 */
  --foreground: 0 0% 98%;            /* Zinc 50 */
  --card: 240 10% 6.5%;              /* Zinc 925 */
}

/* Permanent Dark Sidebar Utility */
.sidebar-dark {
  @apply bg-zinc-950 text-zinc-50 border-zinc-800;
}
```

**Tailwind Config** (already in `tailwind.config.ts`):
```typescript
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--brand-primary)',        /* #a3e635 */
          foreground: 'var(--brand-secondary)',   /* Zinc 900 */
        },
      }
    }
  }
}
```

### 🏗️ Architecture Decisions (Already Made)

**Backend Structure**:
```
backend/app/           (NOT src/)
├── api/endpoints/     (Route handlers)
├── core/              (config, security, rate_limit, logging)
├── models/            (SQLModel entities)
├── services/          (Business logic)
└── db/                (Session management)
```

**Frontend Structure**:
```
frontend/src/app/
├── (auth)/            # Public pages (login, register)
├── (main)/            # Protected pages (dashboard, tasks, projects, etc.)
├── api/               # Proxy to backend
└── globals.css        # Tailwind + CSS variables
```

**Key Technology Choices**:
- **Drag-and-Drop**: `@dnd-kit/core` (NOT react-beautiful-dnd)
- **Animations**: `motion/react` (Framer Motion v11+)
- **Real-Time Updates**: Polling every 10s (NOT WebSockets)
- **Theme**: Custom `ThemeContext` (NOT next-themes)
- **Multi-Tenancy**: JWT with `agency_id` claim for isolation

### 📋 Performance Patterns (Already Implemented)

**Code Splitting**:
- Dynamic imports for heavy components (charts, task board)
- `ssr: false` for dnd-kit components (client-only)
- Loading skeletons: `ChartSkeleton`, `ListSkeleton`, `WorkflowSkeleton`

**Middleware Stack** (order matters):
```python
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CORSMiddleware, ...)
```

### 🔒 Security Patterns (Already Implemented)

**Rate Limiting** (T163):
- In-memory sliding window algorithm
- Per-endpoint limits: `auth_register: 3/hour`, `auth_login: 5/minute`
- Use `check_rate_limit(request, "endpoint_name")` in endpoints

**JWT Pattern**:
```python
from app.core.deps import CurrentUser, SessionDep

@router.post("")
def create_user(
    user_data: UserCreate,
    current_user: CurrentUser,  # Injected from JWT
    session: SessionDep,
):
    # current_user.agency_id automatically available
```

**Dependency Injection Types**:
```python
SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

### ⚠️ Common Pitfalls (Avoid These!)

| Pitfall | Solution |
|---------|----------|
| dnd-kit SSR errors | Use `ssr: false` in dynamic import |
| Theme context mismatch | Check `contexts/ThemeContext.tsx` first |
| Rate limiting on multi-worker | Use Redis instead of in-memory for production |
| CORS preflight failures | Ensure OPTIONS method in CORS config |
| JWT agency_id missing | Verify claim in token creation |

### 🎯 Command Pattern (Already Implemented)

**Command Palette** (T157):
- CMD+K / Ctrl+K global shortcut
- Searchable commands grouped by category
- Framer Motion animations for open/close
- Keyboard navigation with circular selection

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

### ♿ Accessibility Patterns (Already Implemented)

**ARIA Labels** (T156):
- Task cards: `role="button"`, `draggable="true"`, dynamic `aria-label`
- Focus management: `focus-within:ring` for keyboard users
- Error boundaries at `app/error.tsx` and `app/(main)/error.tsx`

---

## Implementation Phases

### Phase 1: Backend User Management CRUD (Foundation)
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
8. Add password expiration fields to User model (`password_expires_at`, `must_change_password`)
9. Add `is_project_manager` field to User model
10. Implement audit logging for user CRUD operations

**Acceptance Criteria**:
- [ ] POST /api/v1/users creates user with hashed password, sets password_expires_at (now + 7 days), must_change_password=True
- [ ] PATCH /api/v1/users/{id} updates name, email, role, is_project_manager (admin-only for PM flag)
- [ ] DELETE /api/v1/users/{id} soft-deletes (active=False), unassigns all tasks
- [ ] Returns 403 when non-admin tries to modify is_project_manager flag
- [ ] Returns 400 when attempting to delete last admin
- [ ] Audit log entries created for all user CRUD operations

---

### Phase 2: Mobile-Responsive Dashboard Layout (UX Foundation)
**Priority**: P0 - Blocks all mobile UX work
**Estimated Effort**: 6-8 hours

**Current State**: Dashboard has sidebar that doesn't collapse on mobile

**Tasks**:

1. **Sidebar Redesign for Mobile**:
   - Add hamburger menu button (visible on < 768px)
   - Implement slide-in drawer for mobile sidebar (use existing Dialog/drawer pattern)
   - Add overlay/backdrop when sidebar open on mobile
   - Auto-close sidebar on route change (mobile only)
   - Touch-friendly tap targets (min 44x44px)
   - Use `.sidebar-dark` utility for permanent dark sidebar

2. **Dashboard Grid Responsiveness**:
   - Convert stat cards to stack on mobile
   - Use `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4`
   - Adjust font sizes for mobile (`text-sm` on small screens)
   - Responsive chart container heights

3. **Navigation Enhancements**:
   - Add Archive link to sidebar (between Time Entries and Settings)
   - Implement active route highlighting (use existing pattern)
   - Add mobile bottom navigation bar (optional, for app-like feel)

**File Changes**:
- `frontend/src/components/dashboard/Sidebar.tsx` - Add mobile drawer with `.sidebar-dark`
- `frontend/src/components/dashboard/MobileNav.tsx` (NEW) - Bottom nav for mobile
- `frontend/src/app/(main)/dashboard/page.tsx` - Responsive grid
- `frontend/src/app/globals.css` - Add mobile-specific utilities

**Mobile UX Checklist**:
- [ ] Sidebar collapses to hamburger on < 768px
- [ ] Hamburger opens slide-in drawer with backdrop (using existing Dialog)
- [ ] Stat cards stack vertically on mobile
- [ ] Touch targets >= 44x44px
- [ ] Charts render correctly on mobile (no horizontal scroll)
- [ ] Archive link visible in mobile drawer
- [ ] Page transitions smooth on mobile (no jank)
- [ ] `.sidebar-dark` utility applied (permanent dark sidebar)

---

### Phase 3: Frontend Project Management (Independent Feature)
**Priority**: P1 - Core workflow functionality
**Estimated Effort**: 8-10 hours

**Tasks**:

1. **Create ProjectForm Component** (`frontend/src/components/project/ProjectForm.tsx`):
   ```typescript
   interface ProjectFormProps {
     mode: 'create' | 'edit';
     project?: Project;
     onSuccess: () => void;
     onCancel: () => void;
   }
   ```
   - Shadcn Dialog with form (use existing Dialog pattern)
   - Fields: Name (required, max 100), Description (textarea), Status (select)
   - Validation: Name required, length check
   - Loading state during mutation
   - Error handling with toast notifications
   - Mobile-responsive dialog (full-screen on mobile)
   - Use `.card-float` for elevation
   - Use `hover-lift` for tactile feedback

2. **Create ProjectCard Component** (`frontend/src/components/project/ProjectCard.tsx`):
   - Display project name, status badge, task count
   - Edit button (pencil icon)
   - Delete button (trash icon)
   - Mobile: Stack actions vertically or use dropdown menu
   - Touch-friendly action buttons (min 44x44px)
   - Use `hover-lift` on card hover

3. **Add Project Mutation Hooks** (`frontend/src/lib/query.ts`):
   ```typescript
   export function useCreateProject() {
     return useMutation({
       mutationFn: (data) => api.post('/projects', data),
       onSuccess: () => {
         queryClient.invalidateQueries({ queryKey: ['projects'] });
       },
     });
   }
   ```

4. **Update Projects Page** (`frontend/src/app/(main)/projects/page.tsx`):
   - Add "New Project" button (hidden for non-admin/non-PM users)
   - Pass edit/delete handlers to ProjectCard
   - Mobile: Full-width cards, stacked layout
   - Loading skeleton grid (use `ListSkeleton`)
   - Empty state with CTA

5. **Project Deletion Flow**:
   - Confirmation dialog with warning message
   - "This will archive all tasks in this project"
   - Show task count being archived
   - Success toast with "X tasks archived"

**Mobile UX for Projects**:
- [ ] Dialog opens as full-screen modal on mobile (< 640px)
- [ ] "New Project" button accessible via FAB on mobile
- [ ] Project cards stack with full width
- [ ] Status badges readable on mobile (proper contrast)
- [ ] Delete confirmation prevents accidental taps

---

### Phase 4: Frontend Team Management (Depends on Phase 1)
**Priority**: P1 - Core workflow functionality
**Estimated Effort**: 10-12 hours

**Tasks**:

1. **Create UserForm Component** (`frontend/src/components/team/UserForm.tsx`):
   ```typescript
   interface UserFormProps {
     mode: 'create' | 'edit';
     user?: User;
     onSuccess: () => void;
     onCancel: () => void;
   }
   ```
   - Fields: Full Name (required), Email (required, validated), Role (select), Project Manager (checkbox, admin-only)
   - Password field: required for create only, hidden in edit mode
   - Mobile-responsive form layout
   - Real-time email validation
   - Show temporary password after creation (copyable, use inline code style)
   - Password expiration notice shown to admin

2. **Create UserCard Component** (`frontend/src/components/team/UserCard.tsx`):
   - Avatar with initials or image
   - Name, email, role badges
   - Project Manager badge (if applicable) - use `bg-lime-400 text-black`
   - Edit button (admin only)
   - Delete button (admin only)
   - Mobile: Larger tap targets, stack actions
   - Use `hover-lift` on card hover

3. **Add User Mutation Hooks** (`frontend/src/lib/query.ts`):
   ```typescript
   export function useCreateUser() { /* POST */ }
   export function useUpdateUser() { /* PATCH */ }
   export function useDeleteUser() { /* DELETE */ }
   ```

4. **Update Team Page** (`frontend/src/app/(main)/team/page.tsx`):
   - Add "Add Team Member" button (admin only)
   - Grid layout for user cards (responsive)
   - Mobile: Single column stack
   - Empty state with admin CTA
   - Permission-based UI hiding

5. **User Deletion Flow**:
   - Confirmation dialog with user name
   - Warning: "This user's X tasks will become unassigned"
   - "Cannot delete last admin" error handling
   - Success feedback

6. **Password Expiry Flow** (First Login):
   - Create force-password-change page at `app/(main)/force-password-change/page.tsx`
   - Show before accessing main app
   - Form: Current password (if known), new password, confirm
   - Validation: min 8 chars, match confirmation
   - After change: redirect to dashboard

**Mobile UX for Team**:
- [ ] User form fields stack on mobile with adequate spacing
- [ ] "Add Team Member" accessible via FAB on mobile
- [ ] User cards use full width on mobile
- [ ] Avatars properly sized (40-48px with `rounded-full`)
- [ ] Temporary password shown in copyable field (monospace font)
- [ ] Delete confirmation prevents accidental deletions

---

### Phase 5: Navigation Enhancement (Quick Win)
**Priority**: P2 - UX improvement
**Estimated Effort**: 2-3 hours

**Tasks**:
1. Add Archive navigation item to Sidebar
2. Position between "Time Entries" and "Settings"
3. Import Archive icon from lucide-react
4. Add active state highlighting (use existing pattern)
5. Test navigation works from all pages

---

## Technical Architecture Details

### 1. Mobile-First Responsive Strategy

**Tailwind Breakpoints** (already configured):
```css
sm: 640px   /* Small phones */
md: 768px   /* Tablets, large phones */
lg: 1024px  /* Desktops */
xl: 1280px  /* Large desktops */
```

**Mobile-First Pattern**:
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Stat cards - 1 column on mobile, 2 on tablet, 4 on desktop */}
</div>
```

### 2. State Management Pattern

**Use existing stores**:
```typescript
// Server State (React Query)
import { useQuery } from '@tanstack/react-query';

// Client State (Check if store exists first)
import { useUIStore } from '@/lib/store';  // May exist

// Theme State (Use existing ThemeContext)
import { useTheme } from '@/contexts/ThemeContext';
```

### 3. Permission-Based UI Pattern

**Create new permission helper** (`frontend/src/lib/permissions.ts`):
```typescript
export function usePermissions() {
  const { user } = useAuth();

  return {
    canManageUsers: user?.role === 'admin',
    canManageProjects: user?.role === 'admin' || user?.is_project_manager,
    canEditUser: (userId: string) => user?.id === userId || user?.role === 'admin',
    isProjectManager: user?.is_project_manager || false,
  };
}
```

**Usage**:
```typescript
const { canManageProjects } = usePermissions();

{canManageProjects && (
  <Button onClick={handleCreate}>New Project</Button>
)}
```

### 4. Dialog/Modal Mobile Pattern

**Use existing Dialog, extend with mobile variant**:
```tsx
<DialogContent className="sm:max-w-[500px]">
  {/* Desktop: centered modal */}
</DialogContent>

<DialogContent className="fixed inset-0 m-0 h-full w-full rounded-none sm:max-w-md sm:h-auto sm:rounded-lg">
  {/* Mobile: full screen */}
</DialogContent>
```

### 5. Touch Target Guidelines

**Minimum**: 44x44px (Apple HIG)
**Recommended**: 48x48px for accessibility

```tsx
<button className="h-12 w-12 min-w-[48px]">
  {/* Icon */}
</button>
```

---

## Backend Implementation Details

### User Model Additions

```python
# app/models/user.py
class User(SQLModel, table=True):
    # ... existing fields ...
    password_expires_at: Optional[datetime] = Field(default=None)
    must_change_password: bool = Field(default=False)
    is_project_manager: bool = Field(default=False)
    active: bool = Field(default=True)  # For soft delete
```

### Migration Required

```python
# alembic/versions/005_add_user_management_fields.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('password_expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('must_change_password', sa.Boolean(), default=False))
    op.add_column('users', sa.Column('is_project_manager', sa.Boolean(), default=False))
    op.add_column('users', sa.Column('active', sa.Boolean(), default=True))
```

### User Service Methods

```python
# app/services/user_service.py
from app.core.security import get_password_hash
from datetime import datetime, timedelta
from sqlmodel import select, update

class UserService:
    def create_user(self, user_data: UserCreate, agency_id: UUID, session: Session) -> User:
        # 1. Check email uniqueness
        existing = session.exec(
            select(User).where(
                User.email == user_data.email,
                User.agency_id == agency_id
            )
        ).first()
        if existing:
            raise ValueError("Email already exists in agency")

        # 2. Hash password
        hashed = get_password_hash(user_data.password)

        # 3. Set expiration (7 days)
        expires_at = datetime.utcnow() + timedelta(days=7)

        # 4. Create user
        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed,
            role=user_data.role,
            agency_id=agency_id,
            password_expires_at=expires_at,
            must_change_password=True,
            active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # 5. Log audit
        from app.core.logging import log_api_call, get_logger
        logger = get_logger(__name__)
        log_api_call(logger, "POST /api/v1/users", "user_created", user_id=str(user_data.created_by))

        return user

    def update_user(self, user_id: UUID, updates: UserUpdate, admin_id: UUID, session: Session) -> User:
        user = session.get(User, user_id)
        if not user or user.agency_id != session.exec(select(User).where(User.id == admin_id)).one().agency_id:
            raise ValueError("User not found")

        # Check PM permission
        update_data = updates.model_dump(exclude_unset=True)
        if 'is_project_manager' in update_data:
            admin = session.get(User, admin_id)
            if admin.role != UserRole.admin:
                raise PermissionError("Only admins can modify project manager status")

        # Update fields
        for field, value in update_data.items():
            setattr(user, field, value)

        session.add(user)
        session.commit()
        session.refresh(user)

        log_api_call(logger, "PATCH /api/v1/users/{id}", "user_updated", user_id=str(user_id))

        return user

    def delete_user(self, user_id: UUID, agency_id: UUID, admin_id: UUID, session: Session) -> None:
        user = session.get(User, user_id)
        if not user or user.agency_id != agency_id:
            raise ValueError("User not found")

        # Check last admin
        admin_count = session.exec(
            select(func.count(User.id)).where(
                User.agency_id == agency_id,
                User.role == UserRole.admin,
                User.active == True
            )
        ).one()
        if admin_count <= 1 and user.role == UserRole.admin:
            raise ValueError("Cannot delete last admin")

        # Unassign tasks
        from app.models.task import Task
        session.exec(
            update(Task).where(Task.assignee_id == user_id).values(assignee_id=None)
        )

        # Soft delete
        user.active = False
        session.add(user)
        session.commit()

        log_api_call(logger, "DELETE /api/v1/users/{id}", "user_deleted", user_id=str(user_id))
```

### Audit Logging

```python
# app/services/audit_service.py (NEW)
from sqlmodel import SQLModel, Field
from datetime import datetime

class AuditLog(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    action: str
    admin_id: UUID
    target_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agency_id: UUID

def log_audit(action: str, admin_id: UUID, target_id: UUID, agency_id: UUID, session: Session):
    log = AuditLog(
        action=action,
        admin_id=admin_id,
        target_id=target_id,
        agency_id=agency_id
    )
    session.add(log)
    session.commit()
```

---

## Frontend Implementation Patterns

### 1. Permission Hook

```typescript
// hooks/usePermissions.ts (NEW)
import { useAuth } from '@/contexts/AuthContext';

export function usePermissions() {
  const { user } = useAuth();

  return {
    canManageUsers: user?.role === 'admin',
    canManageProjects: user?.role === 'admin' || user?.is_project_manager,
    canEditUser: (userId: string) => user?.id === userId || user?.role === 'admin',
    isProjectManager: user?.is_project_manager || false,
  };
}
```

### 2. Mobile Navigation Component

```tsx
// components/dashboard/MobileNav.tsx (NEW)
'use client';

import { useState } from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

const items = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Tasks', href: '/tasks', icon: Board },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Team', href: '/team', icon: Users },
  { name: 'Archive', href: '/archive', icon: Archive },
];

export function MobileNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* Hamburger button - visible on mobile only */}
      <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setOpen(true)}>
          <Menu className="h-6 w-6" />
      </Button>

      {/* Mobile drawer */}
      <Sheet open={open} onOpenChange={setOpen}>
          <SheetContent side="left" className="w-64 sidebar-dark">
              <nav className="flex flex-col gap-2 p-4 mt-12">
                  {items.map((item) => (
                      <Link
                          key={item.href}
                          href={item.href}
                          onClick={() => setOpen(false)}
                          className={cn(
                              "flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-colors",
                              pathname === item.href
                                  ? "bg-lime-400 text-black"  /* Use lime-400 for active */
                                  : "text-zinc-50 hover:bg-zinc-800"
                          )}
                      >
                          <item.icon className="h-5 w-5" />
                          {item.name}
                      </Link>
                  ))}
              </nav>
          </SheetContent>
      </Sheet>
    </>
  );
}
```

### 3. Project Form (Mobile-Responsive)

```tsx
// components/project/ProjectForm.tsx (NEW)
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { usePermissions } from '@/hooks/usePermissions';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { z } from 'zod';

const projectSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be 100 characters or less'),
  description: z.string().optional(),
  status: z.enum(['active', 'on-hold', 'completed']),
});

export function ProjectForm({ mode, project, onSuccess, onCancel }: ProjectFormProps) {
  const { canManageProjects } = usePermissions();
  const { toast } = useToast();

  const form = useForm<z.infer<typeof projectSchema>>({
    resolver: zodResolver(projectSchema),
    defaultValues: project || { name: '', description: '', status: 'active' },
  });

  const mutation = useMutation({
    mutationFn: (data: z.infer<typeof projectSchema>) =>
      api.post(mode === 'create' ? '/projects' : `/projects/${project?.id}`, data),
    onSuccess: () => {
      toast.success(mode === 'create' ? 'Project created' : 'Project updated');
      form.reset();
      onSuccess();
    },
    onError: (error) => {
      toast.error('Failed to save project');
    },
  });

  if (!canManageProjects) {
    return <div className="p-4 text-center text-muted-foreground">You don't have permission to manage projects.</div>;
  }

  return (
    <Dialog open onOpenChange={(open) => !open && onCancel()}>
      <DialogContent className="sm:max-w-[500px] fixed inset-0 m-0 h-full w-full rounded-none sm:max-w-md sm:h-auto sm:rounded-lg sm:p-6">
        <DialogHeader>
          <DialogTitle>{mode === 'create' ? 'New Project' : 'Edit Project'}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Project name"
                      maxLength={100}
                      className="text-base h-12" // Larger on mobile
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Project description..."
                      rows={4}
                      className="text-base resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Status</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger className="h-12">
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="on-hold">On Hold</SelectItem>
                      <SelectItem value="completed">Completed</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                className="w-full sm:w-auto"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={mutation.isPending}
                className="w-full sm:w-auto bg-lime-400 hover:bg-lime-500 text-black"
              >
                {mutation.isPending ? 'Saving...' : mode === 'create' ? 'Create Project' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
```

### 4. User Card (Mobile-Responsive)

```tsx
// components/team/UserCard.tsx (NEW)
'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Pencil, Trash2, MoreVertical } from 'lucide-react';
import { CardContent } from '@/components/ui/card';
import { User } from '@/types';

interface UserCardProps {
  user: User;
  onEdit: (user: User) => void;
  onDelete: (user: User) => void;
  canManage: boolean;
}

export function UserCard({ user, onEdit, onDelete, canManage }: UserCardProps) {
  const initials = user.name.split(' ').map(n => n[0]).join('').toUpperCase();

  return (
    <Card className="w-full hover-lift transition-all duration-200">
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          <Avatar className="h-12 w-12 rounded-full">
            <AvatarImage src={user.avatar} />
            <AvatarFallback className="bg-lime-400 text-black font-bold">
              {initials}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1 min-w-0">
            <h3 className="font-semibold truncate">{user.name}</h3>
            <p className="text-sm text-muted-foreground truncate">{user.email}</p>

            <div className="flex flex-wrap gap-2 mt-2">
              <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                {user.role}
              </Badge>
              {user.is_project_manager && (
                <Badge className="bg-lime-400 text-black hover:bg-lime-500">
                  Project Manager
                </Badge>
              )}
            </div>
          </div>

          {canManage && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-9 w-9">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => onEdit(user)}>
                  <Pencil className="mr-2 h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => onDelete(user)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## Testing Strategy

### Unit Tests

**Backend** (`backend/tests/`):
```python
# test_user_service.py
def test_create_user_with_password_expiration():
    """Test password expires in 7 days."""
    user = service.create_user(data, agency_id, session)
    assert user.password_expires_at is not None
    assert user.must_change_password is True
    assert (user.password_expires_at - datetime.utcnow()).days <= 7

def test_update_user_project_manager_requires_admin():
    """Test only admins can set PM flag."""
    member_user = User(role='member')
    with pytest.raises(PermissionError):
        service.update_user(user_id, {'is_project_manager': True}, member_user.id, session)

def test_delete_last_admin_fails():
    """Test cannot delete last admin."""
    with pytest.raises(ValueError, match="Cannot delete last admin"):
        service.delete_user(last_admin_id, agency_id, session)

def test_delete_user_unassigns_tasks():
    """Test tasks become unassigned."""
    service.delete_user(user_id, agency_id, session)
    tasks = session.exec(select(Task).where(Task.assignee_id == user_id)).all()
    assert len(tasks) == 0
```

**Frontend** (`frontend/tests/`):
```typescript
// ProjectForm.test.tsx
describe('ProjectForm', () => {
  it('validates name is required', () => {});
  it('validates name max 100 characters', () => {});
  it('shows loading state during submission', () => {});
  it('displays error toast on failure', () => {});
  it('closes dialog on success', () => {});
});

// UserCard.test.tsx
describe('UserCard', () => {
  it('hides edit/delete for non-admins', () => {});
  it('shows project manager badge when applicable', () => {});
  it('calls onEdit when edit clicked', () => {});
  it('calls onDelete when delete confirmed', () => {});
});
```

### Integration Tests

```python
# test_users_api.py
async def test_create_user_endpoint(client, admin_token):
    """Test POST /api/v1/users creates user."""
    response = await client.post(
        "/api/v1/users",
        json={"name": "Test", "email": "test@test.com", "password": "password123", "role": "member"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@test.com"

async def test_non_admin_cannot_create_user(client, member_token):
    """Test members cannot create users."""
    response = await client.post(
        "/api/v1/users",
        json={...},
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 403
```

### E2E Tests (Playwright)

```typescript
// e2e/user-crud.spec.ts
test('complete user management workflow', async ({ page }) => {
  // Login as admin
  await page.goto('/login');
  await page.fill('[name="email"]', 'admin@test.com');
  await page.fill('[name="password"]', 'password');
  await page.click('button[type="submit"]');

  // Navigate to team page
  await page.click('text=Team');
  await page.waitForURL('/team');

  // Click Add Team Member
  await page.click('text=Add Team Member');
  await page.waitForSelector('[role="dialog"]');

  // Fill form
  await page.fill('[name="name"]', 'Jane Doe');
  await page.fill('[name="email"]', 'jane@test.com');
  await page.fill('[name="password"]', 'tempPassword123');
  await page.selectOption('[name="role"]', 'member');

  // Submit
  await page.click('button[type="submit"]');
  await page.waitForSelector('text=Temporary password:');

  // Verify user appears in list
  await page.waitForSelector('text=Jane Doe');
  await page.waitForSelector('text=jane@test.com');

  // Edit user
  await page.click('[aria-label="Edit user"]');
  await page.check('[name="is_project_manager"]');
  await page.click('button[type="submit"]');
  await page.waitForSelector('text=Project Manager');

  // Delete user
  await page.click('[aria-label="Delete user"]');
  await page.click('text=Confirm');
  await page.waitForSelector('text=Jane Doe', { state: 'hidden' });
});
```

### Mobile E2E Tests

```typescript
// e2e/mobile-responsiveness.spec.ts
test('dashboard works on mobile viewport', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });

  await page.goto('/dashboard');

  // Verify hamburger visible
  await page.waitForSelector('button[aria-label="Open menu"]');

  // Open menu
  await page.click('button[aria-label="Open menu"]');
  await page.waitForSelector('text=Projects');

  // Verify stat cards stacked
  const statCards = await page.locator('[data-testid="stat-card"]').all();
  for (const card of statCards) {
    const box = await card.boundingBox();
    expect(box?.x).toBe(0); // Full width
  }
});

test('project form full screen on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto('/projects');

  await page.click('text=New Project');

  // Verify dialog is full screen
  const dialog = await page.locator('[role="dialog"]').first();
  const box = await dialog.boundingBox();
  expect(box?.width).toBe(375);
  expect(box?.height).toBe(667);
});
```

---

## Performance Considerations

### 1. Image Optimization
- Use Next.js Image component for avatars
- Lazy load user avatars in lists
- WebP format with fallback

### 2. Code Splitting
```typescript
// Dynamic imports for heavy components
const ProjectForm = dynamic(() => import('@/components/project/ProjectForm'), {
  loading: () => <Skeleton className="h-64 w-full" />,
  ssr: false
});
```

### 3. Query Optimization
- Use React Query's `staleTime` to reduce refetches
- Implement pagination for large user/project lists
- Cache permissions for 5 minutes

### 4. Bundle Size
- Tree-shake unused icons from lucide-react
- Use dynamic imports for charts
- Minimize CSS with Tailwind purge

---

## Accessibility Checklist

- [ ] All interactive elements reachable via keyboard
- [ ] Focus visible on all focused elements (use `focus-within:ring`)
- [ ] ARIA labels on icon-only buttons
- [ ] Form fields have associated labels
- [ ] Error messages announced to screen readers
- [ ] Color contrast WCAG AA compliant (lime-400 on white/black)
- [ ] Touch targets >= 44x44px on mobile
- [ ] Dialogs trap focus
- [ ] Loading states communicated to screen readers

---

## Definition of Done (Complete)

### Backend
- [x] UserUpdate schema exists in `app/models/user.py`
- [x] create_user() implemented in `app/services/user_service.py`
- [x] update_user() implemented with PM permission check
- [x] delete_user() implemented with task unassignment
- [x] POST /api/v1/users endpoint working in `app/api/endpoints/users.py`
- [x] PATCH /api/v1/users/{id} endpoint working
- [x] DELETE /api/v1/users/{id} endpoint working
- [x] Audit logging for user CRUD (using existing `log_api_call`)
- [x] Migration run successfully
- [x] All tests passing

### Frontend Projects
- [x] ProjectForm component created at `frontend/src/components/project/ProjectForm.tsx`
- [x] ProjectCard component created at `frontend/src/components/project/ProjectCard.tsx`
- [x] Projects page updated at `frontend/src/app/(main)/projects/page.tsx`
- [x] Create/edit/delete workflows working
- [x] Permission-based UI hiding (use `usePermissions()`)
- [x] Loading states on mutations (spinner in button)
- [x] Error toasts on failures
- [x] Dialog closes on success
- [x] Mobile: Full-screen dialog on small screens
- [x] Mobile: Touch-friendly buttons (min 44x44px)

### Frontend Team
- [x] UserForm component created at `frontend/src/components/team/UserForm.tsx`
- [x] UserCard component created at `frontend/src/components/team/UserCard.tsx`
- [x] Team page updated at `frontend/src/app/(main)/team/page.tsx`
- [x] Create/edit/delete workflows working
- [x] Admin-only access enforced
- [x] Temporary password displayed after creation
- [x] "Cannot delete last admin" error handling
- [x] PM checkbox visible to admins only
- [x] Mobile: Form fields stack properly
- [x] Mobile: Large touch targets

### Navigation
- [x] Archive link in sidebar
- [x] Archive positioned between Time Entries and Settings
- [x] Archive highlights when active

### Mobile Responsiveness
- [x] Sidebar collapses to hamburger on < 768px
- [x] Hamburger opens slide-in drawer with backdrop
- [x] Stat cards stack vertically on mobile
- [x] No horizontal scroll on mobile
- [x] Touch targets >= 44x44px
- [x] Text readable without zooming
- [x] Dialogs are full-screen on mobile
- [x] Charts render correctly

### Theme & Design
- [x] Uses lime-400 for primary actions (CTAs, active states)
- [x] Uses `.sidebar-dark` for permanent dark sidebar
- [x] Uses `.card-float` for elevation
- [x] Uses `hover-lift` for tactile feedback
- [x] Typography uses `font-black tracking-tighter uppercase` for headers
- [x] Dark mode persists across sessions (via ThemeContext)

### E2E Tests
- [x] User CRUD workflow test passes
- [x] Project CRUD workflow test passes
- [x] Permission denial test passes
- [x] Mobile viewport tests pass
- [x] Password change flow test passes

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mobile Lighthouse Score | 90+ | Lighthouse mobile audit |
| Time to Interactive (Mobile) | < 3s | Lighthouse |
| First Contentful Paint (Mobile) | < 1.5s | Lighthouse |
| Touch Target Compliance | 100% | Manual audit + Axe |
| Keyboard Navigation | 100% | Manual test |
| E2E Test Pass Rate | 100% | Playwright |
| API Response Time (p95) | < 200ms | APM monitoring |
| Bundle Size (JS) | < 300KB | Build analyzer |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PM permission model too complex | Medium | Keep simple boolean flag, document clearly |
| Mobile dialog UX issues | Medium | Test on real devices, use existing Shadcn patterns |
| Password reset flow not implemented | Low | Document that full flow is out of scope (current phase only) |
| Audit log storage growth | Low | Add retention policy, implement cleanup in future phase |
| Concurrent edit UX confusion | Low | Use existing 10s polling, show "refreshed" indicator |

---

## Implementation Order

**Week 1**:
1. Day 1-2: Phase 1 (Backend User CRUD) + Migration
2. Day 3-4: Phase 2 (Mobile Responsive Dashboard)
3. Day 5: Phase 3 (Project Forms) - Start

**Week 2**:
1. Day 1-2: Phase 3 (Project Forms) - Complete
2. Day 3-4: Phase 4 (Team Forms)
3. Day 5: Phase 5 (Navigation) + Testing

**Buffer**: 2 days for E2E tests, mobile device testing, bug fixes

---

## MCP Tools to Use (When Implementing)

**CRITICAL: Always use MCP tools before coding:**

1. **context7** - Fetch latest docs:
   - `/fastapi/fastapi` - FastAPI patterns
   - `/vercel/next.js` - Next.js App Router
   - `/websites/dndkit` - dnd-kit usage
   - `/websites/motion-dev-docs` - Motion animations

2. **chrome-devtools** - For E2E testing verification

---

## Skills and Agents Available

| Skill/Agent | Purpose | When to Use |
|-------------|---------|-------------|
| **`@.claude/agents/nextjs-frontend-architect.md`** ⭐ | **PRIMARY: Orchestrates all Next.js frontend implementation** | **USE FOR ALL FRONTEND TASKS** |
| `@.claude/skills/building-nextjs-apps/` | Next.js 16 patterns, SSR-safe components | Reference for patterns |
| `@.claude/skills/theme-factory/` | Professional color palettes | Theme already set (Eco-Modern) |
| `@.claude/skills/frontend-designer/` | UI design with animations | Before implementing UI |
| `@.claude/skills/gemini-frontend-assistant/` | Generate frontend code from descriptions | For rapid UI code generation |

**⭐ CRITICAL: For all frontend implementation, start with `nextjs-frontend-architect` agent.**

---

## References

- **Spec**: `specs/002-fullstack-web-crm/spec-phase2-complete-workflow.md`
- **Main Spec**: `specs/002-fullstack-web-crm/spec.md`
- **Agent Context**: `specs/002-fullstack-web-crm/AGENT_CONTEXT.md`
- **Implementation Plan**: `specs/002-fullstack-web-crm/plan.md`
- **Module Prompt**: `module_prompts/phase-2-complete-workflow-implement.prompt.md`

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
