# Technology Research: TeamFlow Web (Phase 2)

**Branch**: `002-fullstack-web-crm` | **Date**: 2025-01-29 | **Plan**: [plan.md](./plan.md)

## Summary

This document captures the technology research and decision-making process for TeamFlow Phase 2. All decisions are backed by official documentation retrieved via `context7` MCP tool.

---

## Backend Research

### FastAPI + SQLModel Stack

**Decision**: FastAPI 0.115+ with SQLModel for backend API

**Rationale**:
- FastAPI provides automatic OpenAPI documentation, async support, and dependency injection
- SQLModel combines Pydantic validation with SQLAlchemy ORM, reducing boilerplate
- Python 3.13+ for latest type hinting and performance improvements

**Key Patterns from Documentation**:

1. **Session Dependency Pattern** (from `/fastapi/fastapi`):
```python
from typing import Annotated, Generator
from fastapi import Depends
from sqlmodel import Session, create_engine

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
```

2. **Annotated Dependency Injection** (from `/fastapi/fastapi`):
```python
# Reusable type alias for current user
CurrentUser = Annotated[User, Depends(get_current_user)]

# Use in endpoints
@router.get("/users/me")
def read_users_me(user: CurrentUser):
    return user
```

3. **JWT Authentication with OAuth2PasswordBearer** (from `/fastapi/fastapi`):
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Use as dependency
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # Verify JWT and return user
    pass
```

**Implementation Notes**:
- Use `Annotated` for cleaner dependency injection
- Session dependency with `yield` ensures transactional integrity
- OAuth2PasswordBearer for JWT token handling
- Automatic request validation via Pydantic schemas

---

## Frontend Research

### Next.js 16 App Router

**Decision**: Next.js 16 with App Router for frontend

**Rationale**:
- App Router provides React Server Components, streaming, and improved performance
- Built-in layouts for shared UI (dashboard shell, auth gates)
- Server Actions for mutations without API routes
- File-system based routing simplifies navigation

**Key Patterns from Documentation** (`/vercel/next.js`):

1. **Root Layout Pattern**:
```tsx
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

2. **Server Actions for Mutations**:
```ts
'use server'

export async function createTask(data: TaskCreate) {
  // Server-side logic, DB access
  // No API route needed
}
```

3. **Cookie Management** (for JWT storage):
```ts
'use server'

import { cookies } from 'next/headers'

export async function setToken(token: string) {
  const cookieStore = await cookies()
  cookieStore.set('auth_token', token, { httpOnly: true, path: '/' })
}
```

**Implementation Notes**:
- Use Server Components by default, Client Components only for interactivity
- Server Actions for form submissions (task create, login)
- httpOnly cookies for JWT security
- Route Groups for organization `(dashboard)`, `(auth)`

---

### dnd-kit for Drag-and-Drop

**Decision**: @dnd-kit/core for Kanban board drag functionality

**Rationale**:
- Lightweight, performant, and accessible
- Modular with hooks-based API
- Better TypeScript support than react-beautiful-dnd
- Active maintenance and good documentation

**Key Patterns from Documentation** (`/websites/dndkit`):

1. **DndContext Setup**:
```jsx
import {DndContext} from '@dnd-kit/core';

function TaskBoard() {
  return (
    <DndContext>
      <TaskColumn />
      <TaskCard />
    </DndContext>
  )
}
```

2. **Draggable Task Card**:
```tsx
import {useDraggable} from '@dnd-kit/core';

function TaskCard({ id, children }) {
  const {attributes, listeners, setNodeRef, transform} = useDraggable({
    id: id,
  });
  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
  } : undefined;

  return (
    <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
      {children}
    </div>
  );
}
```

3. **Droppable Column**:
```tsx
import {useDroppable} from '@dnd-kit/core';

function TaskColumn({ id, children }) {
  const {isOver, setNodeRef} = useDroppable({ id });
  const style = {
    backgroundColor: isOver ? '#e0f2fe' : undefined,
  };

  return (
    <div ref={setNodeRef} style={style}>
      {children}
    </div>
  );
}
```

**Implementation Notes**:
- Use `useDraggable` on TaskCard components
- Use `useDroppable` on TaskColumn components
- Handle `onDragEnd` event to update task status
- Use `transform` for performant visual feedback
- Combine with Motion for smooth animations

---

### Motion.dev (Framer Motion) for Animations

**Decision**: Motion (Framer Motion) for animations and micro-interactions

**Rationale**:
- Declarative API with Spring physics
- AnimatePresence for exit animations
- Layout animations for reordering
- Drag gesture animations
- Best-in-class TypeScript support

**Key Patterns from Documentation** (`/websites/motion-dev-docs`):

1. **AnimatePresence for Exits**:
```tsx
import {AnimatePresence, motion} from 'motion/react'

function TaskBoard() {
  return (
    <AnimatePresence>
      {tasks.map(task => (
        <motion.div
          key={task.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9 }}
        />
      ))}
    </AnimatePresence>
  )
}
```

2. **Layout Animations for Reordering**:
```tsx
<motion.div
  layout
  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
>
  {task.title}
</motion.div>
```

3. **Drag Animations**:
```tsx
<motion.div
  drag
  dragConstraints={{ left: 0, right: 0 }}
  whileDrag={{ scale: 1.05, rotate: 2 }}
  whileHover={{ scale: 1.02 }}
>
  {task.title}
</motion.div>
```

**Implementation Notes**:
- Use `AnimatePresence` for column transitions
- Add `layout` prop to task cards for smooth reordering
- Use `whileDrag` for visual feedback during drag
- Spring physics for natural feel (stiffness: 300, damping: 30)
- `initial` → `animate` → `exit` pattern for entrance/exit

---

## Database Research

### Neon Serverless PostgreSQL

**Decision**: Neon PostgreSQL with SQLModel

**Rationale**:
- Serverless: scales to zero when idle, cost-effective
- Native PostgreSQL: full feature support, migrations
- Connection pooling included
- Branching for development/testing

**Schema Design Principles**:
- Multi-tenant via `agency_id` foreign key on all tables
- Cascade deletes for data consistency
- Indexes on foreign keys and frequently queried columns
- Timestamps for auditing (`created_at`, `updated_at`)

---

## State Management Research

### React Query + Zustand

**Decision**: React Query for server state, Zustand for client state

**Rationale**:
- React Query: caching, refetching, optimistic updates
- Zustand: minimal boilerplate for UI state (drawers, modals)
- Separation of concerns prevents complexity

**Patterns**:

1. **React Query Hooks**:
```tsx
// lib/query.ts
import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query'

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => fetch('/api/tasks').then(r => r.json()),
    refetchInterval: 10000, // Poll every 10s
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (task: Task) =>
      fetch(`/api/tasks/${task.id}`, {
        method: 'PATCH',
        body: JSON.stringify(task)
      }),
    onMutate: async (task) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['tasks'] })
      const previous = queryClient.getQueryData(['tasks'])
      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map(t => t.id === task.id ? task : t)
      )
      return {previous}
    },
    onError: (err, task, context) => {
      queryClient.setQueryData(['tasks'], context.previous)
    }
  })
}
```

2. **Zustand Store**:
```tsx
// lib/store.ts
import {create} from 'zustand'

interface UIState {
  selectedTask: Task | null
  drawerOpen: boolean
  setSelectedTask: (task: Task | null) => void
  toggleDrawer: () => void
}

export const useUIStore = create<UIState>((set) => ({
  selectedTask: null,
  drawerOpen: false,
  setSelectedTask: (task) => set({ selectedTask: task }),
  toggleDrawer: () => set((state) => ({ drawerOpen: !state.drawerOpen }))
}))
```

---

## Authentication Research

### Better Auth + JWT

**Decision**: Better Auth with JWT tokens for agency-based authentication

**Approach**:
- Better Auth Python library for JWT generation/verification
- Agency scoping via JWT claims (`agency_id`)
- httpOnly cookies for token storage (XSS protection)
- FastAPI middleware for token verification

**Flow**:
1. User registers → New Agency created, JWT with `agency_id`
2. Login → JWT issued, stored in httpOnly cookie
3. API requests → JWT verified via middleware, `agency_id` extracted
4. All queries scoped to `agency_id` (tenant isolation)

---

## Testing Strategy Research

### Backend Testing

**Tools**: pytest, pytest-cov, httpx

**Approach**:
- Unit tests for services (business logic)
- Integration tests for API endpoints
- Contract tests for OpenAPI spec compliance
- 80%+ coverage target

**Example**:
```python
# tests/unit/test_task_service.py
def test_create_task(db_session, test_agency):
    service = TaskService(db_session)
    task = service.create_task(
        title="Test Task",
        agency_id=test_agency.id,
        status="todo"
    )
    assert task.id is not None
    assert task.status == "todo"
```

### Frontend Testing

**Tools**: Vitest, @testing-library/react, Playwright

**Approach**:
- Unit tests for hooks and utilities
- Integration tests for components
- E2E tests for critical journeys (login, drag task)
- Accessibility testing with axe-core

**Example**:
```tsx
// tests/unit/TaskCard.test.tsx
import {render, screen} from '@testing-library/react'
import {TaskCard} from '@/components/board/TaskCard'

test('renders task title', () => {
  render(<TaskCard task={{id: 1, title: 'Test Task'}} />)
  expect(screen.getByText('Test Task')).toBeInTheDocument()
})
```

---

## Performance Optimizations

### Backend
- Connection pooling via Neon
- Indexed foreign keys (`agency_id`, `project_id`)
- Response compression (gzip)
- Optimistic updates for perceived performance

### Frontend
- Code splitting with Next.js dynamic imports
- Image optimization with next/image
- Streaming with Server Components
- 10s polling with React Query refetchInterval
- Motion animations with GPU acceleration

---

## Security Considerations

1. **JWT Security**:
   - Short expiration (1 hour)
   - Refresh token rotation
   - httpOnly cookies (XSS protection)
   - CSRF tokens

2. **Multi-Tenant Isolation**:
   - All queries scoped to `agency_id`
   - Middleware enforces tenant scoping
   - Row-level security in PostgreSQL

3. **Input Validation**:
   - Pydantic schemas on all endpoints
   - SQLModel prevents SQL injection
   - Rate limiting on auth endpoints

---

## Technology Versions

| Technology | Version | Rationale |
|------------|---------|-----------|
| Python | 3.13+ | Latest type hints, performance |
| FastAPI | 0.115+ | Stable, async support |
| SQLModel | 0.0.22+ | Pydantic v2 compatibility |
| Node.js | 20+ | LTS, stable |
| Next.js | 16.0+ | App Router, Server Components |
| React | 19+ | Latest features, concurrent |
| TypeScript | 5.8+ | Strict mode, better inference |
| @dnd-kit/core | 6.x | Latest stable |
| motion (framer-motion) | 11.x | React 19 compatible |

---

## Alternative Technologies Considered

| Technology | Rejected Because |
|------------|------------------|
| tRPC | Adds complexity, FastAPI already provides type safety |
| Prisma | Less control than SQLModel, SQLModel integrates better with FastAPI |
| Supabase | Overkill for this use case, Neon simpler for serverless |
| React Beautiful DND | No longer maintained, dnd-kit has better TypeScript |
| Zustand for server state | React Query provides caching, refetching, optimistic updates |
| WebSockets for real-time | Polling every 10s sufficient for this scope, simpler |
| MongoDB | Relational model better for multi-tenant CRM |

---

## Documentation Sources

All research verified via `context7` MCP tool:
- `/fastapi/fastapi` - FastAPI official docs
- `/vercel/next.js` - Next.js official docs
- `/websites/dndkit` - dnd-kit official docs
- `/websites/motion-dev-docs` - Motion (Framer Motion) docs

---

## Next Steps

1. ✅ Research complete - proceed to Phase 1
2. Generate data model with entities and relationships
3. Define API contracts (OpenAPI spec)
4. Create quickstart guide for developers
