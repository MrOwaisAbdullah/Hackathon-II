# Tasks: TeamFlow Web (Phase 2 - Full-Stack Agency CRM)

**Input**: Design documents from `/specs/002-fullstack-web-crm/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md

**Tests**: Tests are included as this specification requires TDD approach (Constitution Principle IV)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for both backend and frontend

- [X] T001 Create backend directory structure in backend/ with src/api, src/models, src/services, src/schemas, src/core, src/db, tests/unit, tests/integration, tests/contract
- [X] T002 Create frontend directory structure in frontend/ with src/app, src/components, src/lib, src/hooks, src/types, tests/unit, tests/integration, tests/e2e
- [X] T003 [P] Initialize Python project with FastAPI, SQLModel, pytest, Better Auth dependencies in backend/pyproject.toml
- [X] T004 [P] Initialize Next.js 16 project with TypeScript, React Query, Zustand, Motion.dev, @dnd-kit, Tailwind CSS in frontend/package.json
- [X] T005 [P] Configure backend linting with Black, isort, and pylint in backend/pyproject.toml
- [X] T006 [P] Configure frontend linting with ESLint and Prettier in frontend/.eslintrc.js
- [X] T007 [P] Create backend .env.example with DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET, FRONTEND_URL, ENVIRONMENT
- [X] T008 [P] Create frontend .env.local.example with NEXT_PUBLIC_API_URL and NEXT_PUBLIC_BETTER_AUTH_URL
- [X] T009 [P] Setup Alembic for database migrations in backend/alembic.ini and backend/alembic/
- [X] T010 [P] Setup Playwright for E2E testing in frontend/playwright.config.ts
- [X] T011 [P] Create backend pytest fixtures in backend/tests/conftest.py for database session and test client
- [X] T012 [P] Create frontend Vitest config in frontend/vitest.config.ts
- [X] T013 [P] Create backend README.md with setup instructions
- [X] T014 [P] Create frontend README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T015 Setup Neon PostgreSQL database connection in backend/src/db/session.py with SQLAlchemy engine and session factory
- [X] T016 [P] Implement core configuration with environment variables in backend/src/core/config.py
- [X] T017 [P] Implement JWT verification and password hashing utilities in backend/src/core/security.py
- [X] T018 [P] Implement agency scoping middleware in backend/src/core/middleware.py to enforce tenant isolation
- [X] T019 [P] Setup CORS middleware for frontend origin in backend/src/main.py
- [ ] T020 [P] Setup error handling middleware with structured logging in backend/src/main.py
- [X] T021 [P] Create FastAPI application with health check endpoint in backend/src/main.py
- [ ] T022 [P] Create database initialization script in backend/src/db/init_db.py
- [ ] T023 Create Alembic initial schema migration for Agency and User tables in backend/alembic/versions/001_initial_schema.py
- [X] T024 [P] Create Agency SQLModel in backend/src/models/agency.py
- [X] T025 [P] Create User SQLModel in backend/src/models/user.py
- [X] T026 [P] Create base Pydantic schemas in backend/src/schemas/auth.py
- [X] T027 [P] Implement AuthService for agency/user operations in backend/src/services/auth_service.py
- [X] T028 [P] Create frontend root layout with React Query and Zustand providers in frontend/src/app/layout.tsx
- [X] T029 [P] Create API client wrapper with fetch in frontend/src/lib/api.ts
- [X] T030 [P] Create Zustand store for UI state in frontend/src/lib/store.ts
- [X] T031 [P] Create base TypeScript types for User, Agency in frontend/src/types/user.ts
- [X] T032 [P] Setup Tailwind CSS with custom theme in frontend/tailwind.config.ts
- [X] T033 [P] Install and configure Shadcn UI components in frontend/src/components/ui/
- [X] T033a [P] Create basic TaskDrawer shell component with slide-in animation in frontend/src/components/task/TaskDrawer.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

**Note**: TaskDrawer follows incremental enhancement pattern:
- T033a (Foundational): Basic shell with slide-in animation
- T103 (US3): Add assignee dropdown
- T134 (US5): Add time entries section
- T147 (US6): Add archive button

---

## Phase 3: User Story 1 - Agency Authentication & Team Isolation (Priority: P1) 🎯 MVP

**Goal**: Secure agency signup, login, and complete data isolation between agencies

**Independent Test**: Create two agency accounts, verify that Agency A cannot see Agency B's data, and confirm login/logout sessions work correctly

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T034 [P] [US1] Contract test for POST /auth/register in backend/tests/contract/test_register_contract.py
- [ ] T035 [P] [US1] Contract test for POST /auth/login in backend/tests/contract/test_login_contract.py
- [ ] T036 [P] [US1] Contract test for GET /auth/me in backend/tests/contract/test_me_contract.py
- [ ] T037 [P] [US1] Integration test for signup flow in backend/tests/integration/test_auth_api.py
- [ ] T038 [P] [US1] Integration test for multi-tenant isolation in backend/tests/integration/test_agency_isolation.py
- [ ] T039 [P] [US1] E2E test for signup and login in frontend/tests/e2e/auth.spec.ts

### Backend Implementation for User Story 1

- [X] T040 [P] [US1] Implement agency registration endpoint POST /auth/register in backend/src/api/auth.py
- [X] T041 [P] [US1] Implement login endpoint POST /auth/login in backend/src/api/auth.py
- [X] T042 [P] [US1] Implement current user endpoint GET /auth/me in backend/src/api/auth.py
- [X] T043 [P] [US1] Implement logout endpoint POST /auth/logout in backend/src/api/auth.py
- [X] T044 [US1] Implement JWT middleware for token verification in backend/src/core/middleware.py
- [X] T045 [US1] Implement agency_id scoping in all query methods in backend/src/services/auth_service.py
- [X] T046 [US1] Add password validation with bcrypt in backend/src/core/security.py

### Frontend Implementation for User Story 1

- [X] T047 [P] [US1] Create landing page with hero section and CTA in frontend/src/app/page.tsx
- [X] T048 [P] [US1] Create signup page with form in frontend/src/app/signup/page.tsx
- [X] T049 [P] [US1] Create login page with form in frontend/src/app/login/page.tsx
- [X] T050 [P] [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx (embedded in signup page)
- [X] T051 [P] [US1] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx (embedded in login page)
- [X] T052 [US1] Implement authentication hook with JWT storage in frontend/src/hooks/useAuth.tsx
- [X] T053 [US1] Implement protected route wrapper component in frontend/src/components/auth/ProtectedRoute.tsx
- [X] T054 [US1] Add signup/login page transitions with Motion animations in frontend/src/app/signup/page.tsx and login/page.tsx
- [ ] T055 [US1] Create API proxy route for backend requests in frontend/src/app/api/[...]/route.ts

**Checkpoint**: At this point, User Story 1 should be fully functional - users can signup, login, and agencies are isolated

---

## Phase 4: User Story 2 - Project Task Board with Drag-and-Drop (Priority: P1) 🎯 MVP

**Goal**: Visual Kanban-style board with drag-and-drop task management and satisfying visual feedback

**Independent Test**: Create tasks in different columns, drag them between columns, and verify status updates persist with correct animations

### Tests for User Story 2

- [ ] T056 [P] [US2] Contract test for GET /tasks in backend/tests/contract/test_tasks_contract.py
- [ ] T057 [P] [US2] Contract test for POST /tasks in backend/tests/contract/test_tasks_contract.py
- [ ] T058 [P] [US2] Contract test for PATCH /tasks/{id} in backend/tests/contract/test_tasks_contract.py
- [ ] T059 [P] [US2] Contract test for DELETE /tasks/{id} in backend/tests/contract/test_tasks_contract.py
- [ ] T060 [P] [US2] Integration test for task CRUD operations in backend/tests/integration/test_tasks_api.py
- [ ] T061 [P] [US2] Integration test for task status updates in backend/tests/integration/test_tasks_api.py
- [ ] T062 [P] [US2] E2E test for drag-and-drop task board in frontend/tests/e2e/task-board.spec.ts

### Backend Implementation for User Story 2

- [ ] T063 [P] [US2] Create Task SQLModel with status enum in backend/src/models/task.py
- [ ] T064 [P] [US2] Create Project SQLModel in backend/src/models/project.py
- [ ] T065 [P] [US2] Create TaskCreate, TaskUpdate, TaskRead Pydantic schemas in backend/src/schemas/task.py
- [ ] T066 [P] [US2] Create ProjectCreate, ProjectUpdate, ProjectRead Pydantic schemas in backend/src/schemas/project.py
- [ ] T067 [US2] Implement TaskService with CRUD operations in backend/src/services/task_service.py
- [ ] T068 [US2] Implement ProjectService in backend/src/services/project_service.py
- [ ] T069 [P] [US2] Implement GET /tasks endpoint with agency scoping in backend/src/api/tasks.py
- [ ] T070 [P] [US2] Implement POST /tasks endpoint with agency_id auto-assignment in backend/src/api/tasks.py
- [ ] T071 [P] [US2] Implement PATCH /tasks/{id} endpoint in backend/src/api/tasks.py
- [ ] T072 [P] [US2] Implement DELETE /tasks/{id} soft delete endpoint in backend/src/api/tasks.py
- [ ] T073 [P] [US2] Implement GET /projects endpoint in backend/src/api/projects.py
- [ ] T074 [P] [US2] Implement POST /projects endpoint in backend/src/api/projects.py
- [ ] T075 [US2] Add database migration for Task and Project tables in backend/alembic/versions/002_add_tasks_projects.py
- [ ] T076 [US2] Add composite index on (agency_id, status) in backend/alembic/versions/003_add_task_indexes.py

### Frontend Implementation for User Story 2

- [ ] T077 [P] [US2] Create TypeScript types for Task and Project in frontend/src/types/task.ts
- [ ] T078 [P] [US2] Create React Query hooks for tasks in frontend/src/lib/query.ts
- [ ] T079 [P] [US2] Create React Query hooks for projects in frontend/src/lib/query.ts
- [ ] T080 [P] [US2] Create TaskBoard component with dnd-kit in frontend/src/components/board/TaskBoard.tsx
- [ ] T081 [P] [US2] Create TaskColumn droppable component in frontend/src/components/board/TaskColumn.tsx
- [ ] T082 [P] [US2] Create TaskCard draggable component with Motion animations in frontend/src/components/board/TaskCard.tsx
- [ ] T083 [P] [US2] Create DragOverlay for dragged items in frontend/src/components/board/DragOverlay.tsx
- [ ] T084 [P] [US2] Create TaskForm component for quick-add in frontend/src/components/task/TaskForm.tsx
- [ ] T085 [P] [US2] Create useTaskBoard hook with dnd-kit state management in frontend/src/hooks/useTaskBoard.ts
- [ ] T086 [US2] Implement task board page in frontend/src/app/tasks/page.tsx
- [ ] T087 [US2] Add celebration animation (confetti/ripple) when task moves to Done in frontend/src/components/board/TaskBoard.tsx
- [ ] T088 [US2] Add column stagger animations on page load in frontend/src/components/board/TaskBoard.tsx
- [ ] T089 [US2] Add card tilt animation during drag in frontend/src/components/board/TaskCard.tsx
- [ ] T090 [US2] Add drop zone pulse glow effect in frontend/src/components/board/TaskColumn.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full task board with drag-and-drop

---

## Phase 5: User Story 3 - Task Assignment & Team Collaboration (Priority: P2)

**Goal**: Assign tasks to team members, filter by assignee, and see who is working on what

**Independent Test**: Create team members, assign them to tasks, verify assignments persist and display correctly

### Tests for User Story 3

- [ ] T091 [P] [US3] Contract test for POST /tasks/{id}/assign in backend/tests/contract/test_assign_contract.py
- [ ] T092 [P] [US3] Integration test for task assignment in backend/tests/integration/test_tasks_api.py
- [ ] T093 [P] [US3] E2E test for task assignment flow in frontend/tests/e2e/task-assignment.spec.ts

### Backend Implementation for User Story 3

- [ ] T094 [P] [US3] Add assignee_id foreign key to Task model in backend/src/models/task.py
- [ ] T095 [P] [US3] Implement POST /tasks/{id}/assign endpoint in backend/src/api/tasks.py
- [ ] T096 [US3] Add GET /users endpoint for team listing in backend/src/api/users.py
- [ ] T097 [US3] Implement assign task method in TaskService in backend/src/services/task_service.py
- [ ] T098 [US3] Update Task schema to include assignee filtering in backend/src/schemas/task.py

### Frontend Implementation for User Story 3

- [ ] T099 [P] [US3] Create AssigneeAvatar component in frontend/src/components/task/AssigneeAvatar.tsx
- [ ] T100 [P] [US3] Add assignee display to TaskCard in frontend/src/components/board/TaskCard.tsx
- [ ] T101 [P] [US3] Create user filter dropdown component in frontend/src/components/board/UserFilter.tsx
- [ ] T101a [P] [US3] Create TeamMemberList component with draggable avatars in frontend/src/components/board/TeamMemberList.tsx
- [ ] T102 [US3] Add drag-to-assign functionality with avatar drop zone in frontend/src/components/board/TaskCard.tsx
- [ ] T103 [US3] Update TaskDrawer to show assignee dropdown in frontend/src/components/task/TaskDrawer.tsx

**Checkpoint**: All user stories 1-3 should now be independently functional - team assignment complete

---

## Phase 6: User Story 4 - Agency Command Center Dashboard (Priority: P2)

**Goal**: Dashboard with key metrics, animated stat cards, and project overview

**Independent Test**: Create tasks with different statuses, verify dashboard stats accurately reflect data with animations

### Tests for User Story 4

- [ ] T104 [P] [US4] Contract test for GET /analytics/stats in backend/tests/contract/test_analytics_contract.py
- [ ] T105 [P] [US4] Integration test for dashboard statistics in backend/tests/integration/test_analytics_api.py
- [ ] T106 [P] [US4] E2E test for dashboard load with animations in frontend/tests/e2e/dashboard.spec.ts

### Backend Implementation for User Story 4

- [ ] T107 [P] [US4] Implement AnalyticsService with stat calculations in backend/src/services/analytics_service.py
- [ ] T108 [P] [US4] Implement GET /analytics/stats endpoint in backend/src/api/analytics.py
- [ ] T109 [P] [US4] Implement GET /analytics/tasks-by-status endpoint in backend/src/api/analytics.py
- [ ] T110 [US4] Add team utilization calculation in backend/src/services/analytics_service.py

### Frontend Implementation for User Story 4

- [X] T111 [P] [US4] Create dashboard layout with sidebar in frontend/src/app/dashboard/layout.tsx
- [X] T112 [P] [US4] Create dashboard home page in frontend/src/app/dashboard/page.tsx
- [X] T113 [P] [US4] Create StatCard component with hover animation in frontend/src/components/dashboard/StatCard.tsx
- [ ] T114 [P] [US4] Create ProjectList grid component in frontend/src/components/dashboard/ProjectList.tsx
- [ ] T115 [US4] Add React Query hooks for analytics in frontend/src/lib/query.ts
- [X] T116 [US4] Implement stagger animation for stat cards on load in frontend/src/app/dashboard/page.tsx
- [X] T117 [US4] Add hover lift effect on stat cards in frontend/src/components/dashboard/StatCard.tsx
- [X] T111a [US4] Implement collapsible sidebar with smooth transition animation in frontend/src/components/dashboard/Sidebar.tsx
- [X] T111b [US4] Add sidebar collapse state persistence to localStorage in frontend/src/components/dashboard/Sidebar.tsx
- [X] T111c [P] [US4] Create ThemeProvider context with theme toggle in frontend/src/contexts/ThemeContext.tsx
- [X] T111d [P] [US4] Create ThemeToggle component with sun/moon icon animation in frontend/src/components/ui/ThemeToggle.tsx
- [X] T111e [P] [US4] Configure Tailwind with CSS custom properties for primary, secondary, accent colors in frontend/tailwind.config.ts
- [X] T111h [P] [US4] Define CSS custom properties (design tokens) for brand color palette in frontend/src/app/globals.css
- [X] T111f [US4] Create TaskDistributionChart component with animated bars in frontend/src/components/dashboard/TaskDistributionChart.tsx
- [X] T111g [US4] Create WorkflowProgress component with animated step indicators in frontend/src/components/dashboard/WorkflowProgress.tsx

**Checkpoint**: User Stories 1-4 should now be independently functional - dashboard complete

---

## Phase 7: User Story 5 - Time Logging & Profitability Tracking (Priority: P3)

**Goal**: Log time against tasks, calculate profitability, see project financials

**Independent Test**: Create tasks with rates, log time, verify profitability calculations update correctly

### Tests for User Story 5

- [ ] T118 [P] [US5] Contract test for POST /time-entries in backend/tests/contract/test_time_contract.py
- [ ] T119 [P] [US5] Contract test for GET /analytics/profitability in backend/tests/contract/test_profitability_contract.py
- [ ] T120 [P] [US5] Integration test for time logging in backend/tests/integration/test_time_api.py
- [ ] T121 [P] [US5] Integration test for profitability calculations in backend/tests/integration/test_analytics_api.py

### Backend Implementation for User Story 5

- [ ] T122 [P] [US5] Create TimeEntry SQLModel in backend/src/models/time_entry.py
- [ ] T123 [P] [US5] Create TimeEntryCreate, TimeEntryRead Pydantic schemas in backend/src/schemas/time_entry.py
- [ ] T124 [P] [US5] Add hourly_rate field to Project model in backend/src/models/project.py
- [ ] T125 [US5] Implement TimeEntryService in backend/src/services/time_entry_service.py
- [ ] T126 [US5] Implement POST /time-entries endpoint in backend/src/api/time_entries.py
- [ ] T127 [US5] Implement GET /time-entries endpoint with date filtering in backend/src/api/time_entries.py
- [ ] T128 [US5] Implement GET /analytics/profitability endpoint in backend/src/api/analytics.py
- [ ] T129 [US5] Add profitability calculation logic in backend/src/services/analytics_service.py
- [ ] T130 [US5] Add database migration for TimeEntry table and Project.hourly_rate in backend/alembic/versions/004_add_time_entries.py

### Frontend Implementation for User Story 5

- [ ] T131 [P] [US5] Create TimeEntry types in frontend/src/types/task.ts
- [ ] T132 [P] [US5] Create useTimeTracking hook for timer state in frontend/src/hooks/useTimeTracking.ts
- [ ] T133 [P] [US5] Create TimeLoggingForm component in frontend/src/components/task/TimeLoggingForm.tsx
- [ ] T134 [P] [US5] Add time entries section to TaskDrawer in frontend/src/components/task/TaskDrawer.tsx
- [ ] T135 [US5] Create ProfitabilityReport component in frontend/src/components/dashboard/ProfitabilityReport.tsx

**Checkpoint**: User Stories 1-5 should now be independently functional - time tracking complete

---

## Phase 8: User Story 6 - Rich Task Editing & Archive (Priority: P2)

**Goal**: Edit task details in side drawer, archive tasks with restore capability

**Independent Test**: Edit various task fields, archive tasks, verify changes persist and archived tasks can be restored

### Tests for User Story 6

- [ ] T136 [P] [US6] Integration test for task updates in backend/tests/integration/test_tasks_api.py
- [ ] T137 [P] [US6] Integration test for archive/restore in backend/tests/integration/test_tasks_api.py
- [ ] T138 [P] [US6] E2E test for task editing and archiving in frontend/tests/e2e/task-edit.spec.ts

### Backend Implementation for User Story 6

- [ ] T139 [P] [US6] Implement soft delete for tasks (status=archived) in backend/src/api/tasks.py
- [ ] T140 [P] [US6] Implement GET /tasks?include=archived endpoint in backend/src/api/tasks.py
- [ ] T141 [P] [US6] Implement POST /tasks/{id}/restore endpoint in backend/src/api/tasks.py
- [ ] T142 [US6] Add rich text description field to Task model in backend/src/models/task.py

### Frontend Implementation for User Story 6

- [ ] T143 [US6] Enhance TaskDrawer with rich text editor, priority selector, date picker, and archive button in frontend/src/components/task/TaskDrawer.tsx
- [ ] T144 [P] [US6] Create rich text editor component in frontend/src/components/task/RichTextEditor.tsx
- [ ] T145 [P] [US6] Add priority selector component in frontend/src/components/task/PrioritySelector.tsx
- [ ] T146 [P] [US6] Add due date picker component in frontend/src/components/task/DatePicker.tsx
- [ ] T147 [US6] Implement archive button with confirmation modal in frontend/src/components/task/TaskDrawer.tsx
- [ ] T148 [US6] Add archive page with restore functionality in frontend/src/app/archive/page.tsx
- [ ] T149 [US6] Add card scale-out animation for archive in frontend/src/components/board/TaskBoard.tsx

**Checkpoint**: All user stories should now be independently functional - complete task management

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T150 [P] Add 10-second polling for real-time updates in frontend/src/lib/query.ts (refetchInterval: 10000)
- [ ] T151 [P] Add manual refresh button to task board in frontend/src/components/board/TaskBoard.tsx
- [ ] T152 [P] Implement network loss detection and snap-back animation for drag operations in frontend/src/hooks/useTaskBoard.ts
- [ ] T153 [P] Add skeleton screens for loading states in frontend/src/components/ui/Skeleton.tsx
- [ ] T154 [P] Add error boundary for React components in frontend/src/app/error.tsx
- [ ] T155 [P] Add structured logging to all backend endpoints in backend/src/api/
- [ ] T156 [P] Add accessibility labels and ARIA attributes to all interactive components in frontend/src/components/
- [ ] T157 [P] Add keyboard shortcut (CMD+K) for command palette in frontend/src/components/CommandPalette.tsx
- [ ] T158 [P] Optimize images with next/image in frontend/src/app/
- [ ] T159 [P] Add code splitting with dynamic imports in frontend/src/app/
- [ ] T160 [P] Run Lighthouse audit and fix performance issues
- [ ] T161 [P] Verify WCAG AA compliance with axe-core in frontend/tests/
- [ ] T162 [P] Add GZip compression middleware to backend in backend/src/main.py
- [ ] T163 [P] Add rate limiting to auth endpoints in backend/src/api/auth.py
- [ ] T164 Update quickstart.md with any setup changes discovered during implementation
- [ ] T165 Update AGENT_CONTEXT.md with any implementation lessons learned
- [ ] T166 Run all E2E tests and verify critical user journeys pass
- [ ] T167 Run backend test suite and verify 80%+ coverage target met
- [ ] T168 Run frontend test suite and verify critical paths covered
- [ ] T169 Verify OpenAPI spec matches implementation with openapi-spec-validator
- [ ] T170 Verify data isolation between agencies with multi-tenant test suite
- [ ] T171 Update task count in tasks.md (now 172 tasks after remediation)
- [ ] T172 Update analysis report with remediation applied

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User Story 1 (P1) and User Story 2 (P1) can proceed in parallel after Foundational
  - User Stories 3-6 can proceed after Foundational, with optional integration to US1/US2
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Authentication**: No dependencies on other stories - can start after Foundational
- **User Story 2 (P1) - Task Board**: No dependencies on other stories - can start after Foundational
- **User Story 3 (P2) - Assignment**: Integrates with US2 (Task model) but independently testable
- **User Story 4 (P2) - Dashboard**: Integrates with US2 (Task data) but independently testable
- **User Story 5 (P3) - Time Tracking**: Integrates with US2 (Task model) but independently testable
- **User Story 6 (P2) - Editing**: Integrates with US2 (Task model) but independently testable

### Within Each User Story

- Contract tests MUST be written and FAIL before implementation (TDD)
- Integration tests MUST be written before endpoint implementation
- Models before services
- Services before endpoints
- Components before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (T001-T014)**:
- T003, T004, T005, T006, T007, T008, T009, T010, T011, T012, T013, T014 can all run in parallel (different files)

**Foundational Phase (T015-T033)**:
- T016, T017, T018, T019, T020, T021, T022, T024, T025, T026, T027, T028, T029, T030, T031, T032, T033 can all run in parallel

**User Story 1 (US1)**:
- T034-T039 (all tests) can run in parallel
- T040-T043 (endpoints) can run in parallel after T034-T039 fail
- T047-T051 (frontend components) can run in parallel

**User Story 2 (US2)**:
- T056-T062 (all tests) can run in parallel
- T063-T066 (models/schemas) can run in parallel
- T069-T074 (endpoints) can run in parallel after models
- T077-T082 (frontend components) can run in parallel

**After Foundational Phase**:
- US1, US2, US3, US4, US5, US6 can all be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T034: "Contract test for POST /auth/register"
Task T035: "Contract test for POST /auth/login"
Task T036: "Contract test for GET /auth/me"
Task T037: "Integration test for signup flow"
Task T038: "Integration test for multi-tenant isolation"
Task T039: "E2E test for signup and login"

# After tests fail, launch all endpoint implementations together:
Task T040: "Implement POST /auth/register"
Task T041: "Implement POST /auth/login"
Task T042: "Implement GET /auth/me"
Task T043: "Implement POST /auth/logout"

# Launch all frontend components together:
Task T047: "Create landing page"
Task T048: "Create signup page"
Task T049: "Create login page"
Task T050: "Create RegisterForm component"
Task T051: "Create LoginForm component"
```

---

## Parallel Example: User Story 2

```bash
# Launch all models together:
Task T063: "Create Task SQLModel"
Task T064: "Create Project SQLModel"
Task T065: "Create Task schemas"
Task T066: "Create Project schemas"

# Launch all frontend components together:
Task T077: "Create TypeScript types"
Task T078: "Create React Query hooks"
Task T080: "Create TaskBoard component"
Task T081: "Create TaskColumn component"
Task T082: "Create TaskCard component"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T014)
2. Complete Phase 2: Foundational (T015-T033) - CRITICAL
3. Complete Phase 3: User Story 1 - Authentication (T034-T055)
4. Complete Phase 4: User Story 2 - Task Board (T056-T090)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy/demo as MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Authentication) → Test independently → Deploy/Demo
3. Add US2 (Task Board) → Test independently → Deploy/Demo **(MVP Complete)**
4. Add US3 (Assignment) → Test independently → Deploy/Demo
5. Add US4 (Dashboard) → Test independently → Deploy/Demo
6. Add US5 (Time Tracking) → Test independently → Deploy/Demo
7. Add US6 (Editing) → Test independently → Deploy/Demo
8. Polish → Final production release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Task Board)
3. Then:
   - Developer A: User Story 3 (Assignment)
   - Developer B: User Story 4 (Dashboard)
   - Developer C: User Story 6 (Editing)
4. Developer C picks up User Story 5 (Time Tracking) when ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Contract tests MUST fail before implementing (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are mandatory per Constitution Principle IV
- Use `context7` MCP before implementing any library integration
- Use `@.claude/skills/frontend-designer/` before implementing UI components
- Use `@.claude/skills/better-auth-integration/` for authentication patterns
