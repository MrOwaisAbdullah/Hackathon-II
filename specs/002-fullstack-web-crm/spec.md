# Feature Specification: TeamFlow Web (Phase 2 - Full-Stack Agency CRM)

**Feature Branch**: `002-fullstack-web-crm`
**Created**: 2025-01-29
**Status**: Draft
**Input**: User description: "Phase 2: TeamFlow Full-Stack Web App Specification. Evolving TeamFlow from a CLI tool into a Full-Stack Agency CRM. This is NOT a standard Todo App. It is a high-performance, visually stunning tool for creative agencies to manage complex work."

---

## Executive Summary

TeamFlow Phase 2 transforms the CLI-based task management tool into a **full-stack web application** designed specifically for creative agencies. While this application builds on the core "todo" functionality required by the hackathon (add, delete, update, view, mark complete), it reimagines these features through the lens of agency workflows: project deliverables, team collaboration, visual task boards, and profitability tracking.

The application distinguishes itself through **animation-first design**, creating a tactile, responsive interface that feels alive. Every interaction—from dragging tasks to completing work—provides visual feedback that reinforces user actions and creates delight.

**Design Philosophy**: "Bold & Tactile"—avoiding safe, corporate AI aesthetics in favor of micro-interactions, fluid layouts, glassmorphism, and rich textures.

---

## Clarifications

### Session 2025-01-29

- **Q: When two users edit the same task simultaneously, how should the system resolve conflicts?**
  - **A: Last write wins — most recent edit overwrites previous changes**
- **Q: When a user loses connection while dragging a task, what should happen?**
  - **A: Cancel the drag immediately and return task to original column**
- **Q: Should users see changes from other team members in real-time or require manual refresh?**
  - **A: Polling every 10 seconds + manual refresh button**
- **Q: When a team member is deleted from the agency, what happens to their assigned tasks?**
  - **A: Tasks become unassigned (assignee_id set to null)**

---

## User Flows

This section documents the complete user journey from first visit to active usage. Each flow represents a critical path through the application.

### Flow 1: First-Time User (Landing → Signup → Dashboard)

**Entry Point**: User visits `https://teamflow.app` (or deployed URL)

**Steps**:

1. **Landing Page**
   - Hero section with bold typography.
   - Animated background (subtle particle or gradient movement)
   - CTA buttons: "Get Started Free" (primary), "Watch Demo" (secondary)
   - Feature preview cards that animate on scroll
   - Social proof: "Trusted by 50+ creative agencies"

2. **Click "Get Started Free"** → Navigate to Signup Page
   - Page transition: Smooth slide-in from right
   - Form fields: Email, Password (with visibility toggle), Agency Name, Full Name
   - Real-time validation with inline feedback
   - Terms checkbox with styled custom control
   - Submit button with hover glow effect

3. **Submit Signup Form** → Account Creation + Auto-Login
   - Loading state: Skeleton or spinner with agency name ("Setting up [Agency Name]...")
   - Success feedback: Brief celebration animation
   - Session created automatically
   - Redirect to Dashboard

4. **Dashboard First Load**
   - Skeleton screens fade out (500ms)
   - Hero stats stagger in (0ms, 100ms, 200ms delays)
   - Empty state message: "Create your first project to get started"
   - Onboarding tooltip: "Press Ctrl/CMD+K anytime for quick actions"

---

### Flow 2: Returning User (Login → Dashboard)

**Entry Point**: User visits app while logged out

**Steps**:

1. **Login Page**
   - Clean, centered form with agency branding
   - Email field (auto-focus on load)
   - Password field with "Forgot password?" link
   - "Remember me" toggle
   - "Don't have an account? Sign up" link
   - Submit button with loading state

2. **Submit Login** → Authentication
   - Validation: Check credentials via API
   - Error state: Shake animation on invalid credentials
   - Success: Session created, store JWT

3. **Navigate to Dashboard**
   - Page transition: Fade-in from bottom
   - Load user's agency data
   - Display stats, projects, tasks

---

### Flow 3: Task Creation Flow (Dashboard → Task Board → Create)

**Entry Point**: User is on Dashboard

**Steps**:

1. **From Dashboard**
   - Click "View Task Board" button or nav item
   - Page transition: Slide-in from right

2. **Task Board Loads**
   - Columns animate in from bottom (staggered: Todo → Doing → Review → Done)
   - Existing task cards stagger in per column
   - Empty columns show "Drop tasks here" ghost state

3. **Create New Task**
   - Option A: Click "+" button in column header → Modal form
   - Option B: Press CMD+K → Command palette → Type "Create task"
   - Option C: Double-click empty space in column → Inline form

4. **Task Creation Form**
   - Title (required, auto-focus)
   - Description (rich text toolbar: bold, italic, list, link)
   - Assignee dropdown (search team members)
   - Priority selector (Low/Medium/High with color coding)
   - Due date picker
   - Submit button with "Create & Add Another" option

5. **Submit Form**
   - Optimistic UI: Card appears immediately with scale-in animation
   - API call in background
   - Error handling: Card shows error state, allows retry
   - Success: Card settles in column

---

### Flow 4: Drag Task to Complete (Task Board → Celebration)

**Entry Point**: User views task board with tasks in progress

**Steps**:

1. **Start Drag**
   - User clicks and holds task card
   - Card scales to 105%, tilts 3 degrees
   - Shadow increases (elevation)
   - Other cards fade slightly (focus on dragged item)

2. **Drag Over Columns**
   - Drop zones highlight with pulse glow
   - Column background subtly brightens
   - Other items make room (layout animation)

3. **Drop on "Done"**
   - Card scales down to 100%
   - Snaps to grid position with spring physics
   - Status updates immediately (optimistic UI)
   - API call syncs in background

4. **Celebration Animation**
   - Confetti explosion from card center
   - OR: Ripple effect radiates outward
   - Sound effect (optional, can be disabled)
   - "Great work!" toast notification

---

### Flow 5: View Task Details (Task Board → Detail Drawer)

**Entry Point**: User is on Task Board

**Steps**:

1. **Click Task Card**
   - Drawer slides in from right (300ms ease-out)
   - Background overlay fades in (backdrop-blur)
   - Task board dims slightly

2. **Detail Drawer Content**
   - Title (editable, large typography)
   - Status badge (click to cycle through statuses)
   - Assignee section (avatar + name, click to reassign)
   - Description (rich text, editable)
   - Due date (click to edit via date picker)
   - Time entries section (list of logged hours)
   - "Add Time Entry" button
   - Activity history (who changed what, when)
   - Action buttons: "Archive", "Duplicate"

3. **Close Drawer**
   - Click overlay → Drawer slides out
   - Press ESC → Drawer slides out
   - Click "X" button → Drawer slides out
   - Changes auto-save or show "Save" button

---

### Flow 6: Assign Task to Team Member (Task Board → Assign)

**Entry Point**: User views unassigned task card

**Steps**:

1. **View Unassigned Task**
   - Card shows empty avatar placeholder
   - "Unassigned" text or icon

2. **Open Assignment Options**
   - Option A: Click card → Detail drawer → Click assignee dropdown
   - Option B: Drag team member avatar from sidebar onto card
   - Option C: Right-click card → Context menu → "Assign to..."

3. **Select Team Member**
   - Dropdown shows list with avatars
   - Search/filter by name
   - Click member name → Assignment saved

4. **Visual Confirmation**
   - Card updates with new avatar (scale animation)
   - Assignee sees task in their "My Tasks" filter
   - Optional: Notification sent to assignee

---

### Flow 7: Archive Task (Task Board → Archive)

**Entry Point**: User wants to remove a task

**Steps**:

1. **Initiate Archive**
   - Option A: Drag task card to "Trash" drop zone (bottom-right)
   - Option B: Right-click card → "Archive"
   - Option C: Open detail drawer → Click "Archive" button

2. **Confirm Archive**
   - Confirmation modal: "Archive this task?"
   - Shows task title and warning
   - "Cancel" (secondary) and "Archive" (destructive)

3. **Archive Animation**
   - Card scales down to 0%
   - Fades out (300ms)
   - Other cards shuffle to fill space (layout animation)

4. **Access Archive**
   - Navigate to "Archive" via sidebar
   - Archived tasks listed with restore option
   - Click "Restore" → Task returns to previous column

---

### Page Structure Summary

```
┌─────────────────────────────────────────────────────────────┐
│                        LANDING PAGE                          │
│  Hero + Features + CTA → Sign Up                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                         AUTH PAGES                           │
│  /signup  |  /login  |  /forgot-password                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      AUTHENTICATED APP                       │
│  ┌──────────┬───────────────────────────────────────────┐   │
│  │          │  HEADER: Logo | Search | Notifications | 👤 │   │
│  │  SIDEBAR  ├───────────────────────────────────────────┤   │
│  │          │                                           │   │
│  │ • Dashboard│                                           │   │
│  │ • Projects │           MAIN CONTENT AREA              │   │
│  │ • Tasks    │                                           │   │
│  │ • Team     │           (Dashboard / Board / Detail)   │   │
│  │ • Time     │                                           │   │
│  │ • Settings │                                           │   │
│  │          │                                           │   │
│  └──────────┴───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## User Scenarios & Testing

### User Story 1 - Agency Authentication & Team Isolation (Priority: P1)

**Journey**: As an agency owner, I want to sign up securely and know that all my team's work, tasks, and data are completely isolated from other agencies. When I log in, I should see only my agency's projects and team members.

**Why this priority**: Without secure authentication and data isolation, nothing else matters. This is the foundation upon which all trust and multi-tenancy is built.

**Independent Test**: Can be fully tested by creating two agency accounts, verifying that data from one agency is never visible to the other, and confirming that login/logout sessions work correctly.

**Acceptance Scenarios**:

1. **Given** I am a new user, **When** I visit the application for the first time, **Then** I see a signup page requesting my email, password, and agency name
2. **Given** I have completed signup, **When** I submit the form with valid data, **Then** my account is created and I am logged in automatically
3. **Given** I am logged out, **When** I enter my credentials and submit, **Then** I am authenticated and redirected to my dashboard
4. **Given** I am logged in as Agency A, **When** I access any page, **Then** I only see Agency A's data (projects, tasks, team members)
5. **Given** Agency A and Agency B both exist, **When** Agency A logs in, **Then** they cannot see or access any of Agency B's data
6. **Given** my session has been inactive for extended time, **When** I return to the app, **Then** I am prompted to re-authenticate

---

### User Story 2 - Project Task Board with Drag-and-Drop (Priority: P1)

**Journey**: As a creative director or project manager, I want a visual Kanban-style board where I can see all project tasks arranged by status (Todo, Doing, Review, Done). I should be able to drag tasks between columns to update their status, with satisfying visual feedback that confirms the action.

**Why this priority**: This is the core "todo" functionality reimagined for agencies. It directly addresses the hackathon requirements (add, view, update, complete) while providing the primary interface for daily work.

**Independent Test**: Can be fully tested by creating tasks in different columns, dragging them between columns, and verifying that status updates persist and animations play correctly.

**Acceptance Scenarios**:

1. **Given** I am viewing the project board, **When** the page loads, **Then** I see tasks organized into columns (Todo, Doing, Review, Done)
2. **Given** I am viewing the Todo column, **When** I click a "Quick Add" button, **Then** a new task form appears inline or in a modal
3. **Given** I am creating a new task, **When** I enter a title and submit, **Then** the task appears in the Todo column with a stagger animation
4. **Given** I am dragging a task card, **When** I lift the card, **Then** the card tilts slightly and drop zones highlight
5. **Given** I am dragging a task to a new column, **When** I drop it, **Then** the task animates into its new position and the status updates immediately
6. **Given** I have dragged a task to "Done", **When** the drop completes, **Then** a celebration animation plays (confetti or ripple effect)
7. **Given** I am viewing a task card, **When** I click it, **Then** a side drawer (sheet) opens with full task details and edit controls

---

### User Story 3 - Task Assignment & Team Collaboration (Priority: P2)

**Journey**: As a project manager, I want to assign tasks to specific team members and see who is working on what at a glance. I should be able to reassign tasks by dragging team member avatars onto task cards.

**Why this priority**: Team collaboration is essential for agency work. This extends basic task management into a team coordination tool.

**Independent Test**: Can be fully tested by creating team members, assigning them to tasks, and verifying that assignments persist and display correctly on the board.

**Acceptance Scenarios**:

1. **Given** I am viewing the task board, **When** I look at any task card, **Then** I see the assignee's avatar or an unassigned indicator
2. **Given** I am viewing a task, **When** I open the task detail drawer, **Then** I can assign or reassign the task to a team member
3. **Given** I am viewing the board, **When** I drag a team member's avatar onto a task card, **Then** the task becomes assigned to that team member
4. **Given** I am filtering by team member, **When** I select a person from a filter dropdown, **Then** only tasks assigned to that person are displayed
5. **Given** I am assigned to a task, **When** I view the board, **Then** I can quickly see all tasks assigned to me

---

### User Story 4 - Agency Command Center Dashboard (Priority: P2)

**Journey**: As a project manager or agency owner, I want a dashboard that shows me key metrics at a glance: active projects, total tasks, team utilization, and revenue profitability. The dashboard should feel like a HUD (heads-up display) with cards that animate in and respond to hover.

**Why this priority**: Provides executive-level visibility into agency health. Extends basic "view task list" into analytics and insights.

**Independent Test**: Can be fully tested by creating tasks with different statuses and assignees, then verifying that dashboard stats accurately reflect the data and animations play on load.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I navigate to the dashboard, **Then** I see stat cards (Active Projects, Tasks Completed, Team Utilization, Revenue)
2. **Given** the dashboard is loading, **When** skeleton screens fade out, **Then** content staggers in (hero stats first, then lists)
3. **Given** I am viewing the dashboard, **When** I hover over a stat card, **Then** the card lifts slightly and shows a subtle glow
4. **Given** tasks have been created and completed, **When** I view the dashboard, **Then** all statistics accurately reflect the current state
5. **Given** I want to see more detail, **When** I click on a stat card, **Then** I am navigated to a detailed view or filtered list
6. **Given** I am on desktop viewing the dashboard, **When** I click the sidebar collapse button, **Then** the sidebar smoothly collapses to icons-only and the content area expands to fill the space
7. **Given** the sidebar is collapsed, **When** I click the expand button, **Then** the sidebar smoothly expands to show full labels
8. **Given** I am viewing any page, **When** I click the theme toggle button, **Then** the color scheme smoothly animates between light and dark modes
9. **Given** I have selected a theme, **When** I refresh the page or return later, **Then** my theme preference persists
10. **Given** I am viewing the dashboard, **When** the page loads, **Then** I see animated visualizations including bar charts for task distribution and workflow progress indicators with smooth animations

---

### User Story 5 - Time Logging & Profitability Tracking (Priority: P3)

**Journey**: As a CFO or account manager, I want to log time spent on tasks and see profitability calculations. I need to know which projects are profitable (billable hours × rate) and which are over-budget.

**Why this priority**: Business intelligence is valuable but not required for basic task management. This extends the tool into agency operations.

**Independent Test**: Can be fully tested by creating tasks with hourly rates, logging time, and verifying that profitability calculations update correctly.

**Acceptance Scenarios**:

1. **Given** I am viewing a task, **When** I open the detail drawer, **Then** I see a time logging interface (timer or manual entry)
2. **Given** I am logging time, **When** I start a timer, **Then** the timer counts up in real-time and I can stop it to log hours
3. **Given** a task has billable hours logged, **When** I view the dashboard or project view, **Then** I see profitability calculated as (Billable Hours × Rate) - Cost
4. **Given** I am viewing a project, **When** I look at profitability metrics, **Then** I can see which projects are over or under budget
5. **Given** I have logged time incorrectly, **When** I edit or delete a time entry, **Then** profitability recalculates

---

### User Story 6 - Rich Task Editing & Archive (Priority: P2)

**Journey**: As a creative professional, I want to edit task details (title, description, priority, due date) in a rich interface. When a task is no longer needed, I want to archive it (not permanently delete immediately) with the option to restore.

**Why this priority**: Completes the CRUD requirements (create, read, update, delete) with a professional interface. Archive provides safety vs. permanent deletion.

**Independent Test**: Can be fully tested by editing various task fields, archiving tasks, and verifying that changes persist and archived tasks can be restored.

**Acceptance Scenarios**:

1. **Given** I am viewing a task card, **When** I click to open it, **Then** I see a side drawer with rich text editor for description
2. **Given** I am editing a task, **When** I change the title, description, priority, or due date, **Then** changes save automatically or when I click save
3. **Given** I want to remove a task, **When** I drag it to a "Trash" drop zone or use a context menu, **Then** the task is archived (moved to archive, not deleted)
4. **Given** I am viewing the task board, **When** I archive a task, **Then** the card animates out smoothly
5. **Given** I have archived tasks, **When** I view an "Archive" section, **Then** I can see all archived tasks and restore them
6. **Given** I have restored an archived task, **When** I return to the board, **Then** the task appears in its previous column with an animation

---

### Edge Cases

- What happens when a user tries to drag a task while a network request is in progress?
- **Concurrent edits**: When two users edit the same task simultaneously, the last write wins (most recent edit overwrites previous changes)
- **Deleted team member**: When a team member is deleted from the agency, their assigned tasks become unassigned (assignee_id set to null), showing empty avatar placeholder
- How does the board behave when there are 100+ tasks in a single column (performance)?
- **Network loss during drag**: Cancel the drag immediately and return task to original column with visual feedback (snap-back animation)
- How does the system handle session timeouts during long inactivity periods?
- What happens when the user tries to create a task without a title?
- How does the application behave on mobile devices with smaller screens?
- What happens when a task's due date is in the past (visual indication)?
- How does the system handle time zone differences for distributed teams?

---

## Requirements

### Functional Requirements

#### Authentication & Access
- **FR-001**: System MUST allow new users to sign up with email, password, and agency name
- **FR-002**: System MUST authenticate existing users via email and password login
- **FR-003**: System MUST maintain secure sessions and handle session expiration
- **FR-004**: System MUST ensure complete data isolation between agencies (multi-tenancy)
- **FR-005**: System MUST allow users to log out and terminate their session

#### Task Management (Core Hackathon Requirements)
- **FR-006**: Users MUST be able to create new tasks with at least a title, description (rich text with markdown support), priority, due date, assignee, and project association
- **FR-007**: Users MUST be able to view all tasks organized by status (Todo, Doing, Review, Done)
- **FR-008**: Users MUST be able to update task details (title, description with rich text editor, priority, due date, assignee, project)
- **FR-009**: Users MUST be able to delete/archive tasks via dropdown menu or detail drawer
- **FR-010**: Users MUST be able to mark tasks as complete (move to Done status) with celebration animation
- **FR-060**: Task cards MUST display action menu (three-dot menu) with Edit, Archive, and Delete options
- **FR-061**: Task creation and editing forms MUST include rich text markdown editor with toolbar (bold, italic, headings, lists, links)

#### Task Board & Drag-and-Drop
- **FR-011**: System MUST display tasks in a Kanban-style board with columns
- **FR-012**: Users MUST be able to drag task cards between columns
- **FR-013**: System MUST provide visual feedback during drag operations (card tilt, drop zone highlighting)
- **FR-014**: System MUST update task status immediately when dropped in a new column
- **FR-015**: System MUST play a celebration animation when tasks are moved to "Done"
- **FR-016**: System MUST support quick-add task creation from any column

#### Team & Assignment
- **FR-017**: Users MUST be able to create and manage team members within their agency
- **FR-018**: Users MUST be able to assign tasks to team members
- **FR-019**: System MUST display assignee avatars on task cards
- **FR-020**: Users MUST be able to filter tasks by assignee
- **FR-021**: System MUST support reassigning tasks via drag-and-drop (avatar to card)
- **FR-047**: When a team member is deleted from the agency, all tasks assigned to that member MUST become unassigned (assignee_id set to null) and display an empty avatar placeholder

#### Dashboard & Analytics
- **FR-022**: System MUST display a dashboard with key metrics (active projects, tasks, team utilization) AND animated visualizations (bar charts, upcoming deadline indicators)
- **FR-023**: System MUST show profitability calculations when time and rate data are available
- **FR-024**: Dashboard cards MUST animate in on page load with stagger effect
- **FR-025**: Dashboard MUST provide statistics updated via polling every 10 seconds and a manual refresh button for immediate sync
- **FR-048**: Dashboard sidebar MUST support collapse/expand on desktop with smooth transition animation
- **FR-049**: When sidebar is collapsed, it MUST show icons-only and content area MUST expand to fill available space
- **FR-066**: Dashboard MUST display Upcoming Deadlines component showing tasks due within 7 days, sorted by urgency (overdue first, then by due date)
- **FR-067**: Upcoming Deadlines MUST display overdue badges with pulsing animation for tasks past their due date
- **FR-068**: Upcoming Deadlines MUST link tasks to their respective project detail pages for quick navigation

#### Time & Profitability
- **FR-026**: Users MUST be able to log time against tasks (via timer or manual entry)
- **FR-027**: System MUST calculate profitability as (Billable Hours × Rate) - Cost
- **FR-028**: System MUST display profitability metrics at project and dashboard levels
- **FR-029**: Users MUST be able to edit or delete time entries

#### User Interface & Animation
- **FR-030**: System MUST provide smooth page transitions (no hard cuts)
- **FR-031**: All interactive elements MUST provide visual feedback on hover, tap, and active states
- **FR-032**: System MUST use skeleton screens during loading states
- **FR-033**: Task cards MUST stagger in when displayed in a list
- **FR-034**: Layout changes MUST animate smoothly (using layout-aware transitions)
- **FR-035**: System MUST support keyboard shortcuts (CMD+K for quick actions)
- **FR-062**: All buttons MUST use standardized CSS variables for consistent theming (--accent, --accent-hover for primary actions)
- **FR-063**: Dropdown menus and drawer panels MUST display custom lime-themed scrollbars when content overflows
- **FR-064**: Priority and status badges MUST use theme-aware colors (light/dark mode compatible) with proper contrast
- **FR-065**: Drag-and-drop operations MUST use synchronous cache updates for immediate visual feedback before API completion

#### Theme Support
- **FR-050**: System MUST support light and dark color themes
- **FR-051**: Theme preference MUST persist across sessions (localStorage)
- **FR-052**: Theme transition MUST animate smoothly between modes
- **FR-053**: System MUST provide a theme toggle button accessible from all pages

#### Brand Identity & Design Tokens
- **FR-054**: System MUST use a unique brand color palette that avoids AI-cliché purple (#8b5cf6, #7c3aed, #a78bfa)
- **FR-055**: Primary brand color MUST be defined in CSS custom properties for theme consistency
- **FR-056**: Color palette MUST follow "Modern Industrial / Glass & Grain" aesthetic with deep orange primary
- **FR-057**: All color values MUST use CSS custom properties (design tokens) for maintainability

#### Task Editing & Archive
- **FR-036**: Users MUST be able to edit task details in a side drawer (sheet)
- **FR-037**: System MUST provide a rich text editor for task descriptions
- **FR-038**: Users MUST be able to archive tasks (soft delete) with restore capability
- **FR-039**: System MUST support drag-to-archive or context menu for deletion
- **FR-040**: Archived tasks MUST be viewable in a separate archive section
- **FR-069**: TaskDrawer MUST display all time entries logged against the task with duration, description, date, and user
- **FR-070**: TaskDrawer MUST calculate and display total time automatically from all time entries
- **FR-071**: TaskDrawer MUST provide "Add Time Entry" button to open TimeLoggingForm

#### Project Management & Navigation
- **FR-072**: Projects MUST have a status field with four states: Active, On Hold, Completed, Archived
- **FR-073**: Project status MUST be visually indicated with color-coded badges (emerald/amber/blue/gray)
- **FR-074**: System MUST provide a ProjectDrawer component for editing project details (mirrors TaskDrawer design)
- **FR-075**: ProjectDrawer MUST include rich text editor for project descriptions
- **FR-076**: System MUST provide dynamic routes for individual project pages at `/projects/[id]`
- **FR-077**: Project detail pages MUST display project metadata, description (rendered markdown), and task statistics
- **FR-078**: Project detail pages MUST show progress bar with completion percentage
- **FR-079**: Project detail pages MUST list all project tasks with priority and due date information

#### Data Persistence
- **FR-041**: System MUST persist all data (tasks, users, time entries) to a database
- **FR-042**: System MUST handle optimistic UI updates with server synchronization
- **FR-043**: System MUST handle network errors gracefully with retry or user notification
- **FR-044**: When multiple users edit the same task concurrently, system MUST use last-write-wins conflict resolution (most recent edit overwrites previous changes)
- **FR-045**: When network connection is lost during a drag operation, system MUST cancel the drag and return the task card to its original column with a snap-back animation
- **FR-046**: System MUST poll for updates from other team members every 10 seconds and provide a manual refresh button for immediate sync

---

### Key Entities

- **Agency**: Represents a company/team using the system. Key attributes: name, created date, subscription tier. All data is scoped to an agency.

- **User**: Represents an individual person with login credentials. Key attributes: email, password (hashed), name, role (admin, member), agency_id.

- **Task**: Represents a unit of work or deliverable. Key attributes: title, description (rich text with markdown support), status (Todo, Doing, Review, Done), priority (Low, Medium, High), due_date (optional), created_at, updated_at, agency_id, assignee_id (references User, optional), project_id (references Project, optional). Task descriptions support markdown rendering on cards with rich text editing in forms.

- **TimeEntry**: Represents time logged against a task. Key attributes: duration (hours), description, date, task_id, user_id, billable (boolean), hourly_rate. Time entries are displayed in TaskDrawer with total time calculation.

- **Project**: Represents a collection of tasks for a client or initiative. Key attributes: name, description (rich text with markdown support), status (Active, On Hold, Completed, Archived), agency_id, budget, hourly_rate. Has many Tasks. Projects have dedicated detail pages with dynamic routes.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can complete the signup flow and create their first task within 3 minutes
- **SC-002**: Users can drag a task between columns and see the status update within 500ms (including network round-trip)
- **SC-003**: The dashboard loads and displays all statistics within 2 seconds on a standard connection
- **SC-004**: 95% of users successfully complete the core task workflow (create, assign, move to done) on their first session without assistance
- **SC-005**: The application supports at least 50 concurrent users without performance degradation
- **SC-006**: Task board renders smoothly with up to 100 tasks per column (60fps animations)
- **SC-007**: All animations complete within 400ms (responsive feel, no sluggishness)
- **SC-008**: Time logging and profitability calculations update in real-time within 1 second
- **SC-009**: The application is fully functional on mobile devices (320px width minimum)
- **SC-010**: Data isolation between agencies is 100%—no cross-agency data leakage possible

---

## Constraints & Assumptions

### Constraints

- **Hackathon Requirements**: Must implement core todo functionality (add, delete, update, view, mark complete) as the foundation
- **Design Requirement**: Must use "Bold & Tactile" aesthetic—no safe, bootstrap-like designs
- **Animation Requirement**: Must use animation-first approach with Motion.dev (Framer Motion)
- **Performance Requirement**: Largest Contentful Paint (LCP) must be under 1.5 seconds
- **Browser Support**: Must work on modern browsers (Chrome, Firefox, Safari, Edge) within last 2 versions

### Assumptions

- Users have modern browsers with JavaScript enabled
- Users have basic familiarity with Kanban-style boards (Trello, Linear, etc.)
- Agencies have 2-50 team members (small to medium-sized agencies)
- Most users interact with the application on desktop/laptop screens
- Time zone handling will default to UTC with display in user's local time
- Rich text editor requirements are basic (bold, italic, lists, links)—not full word processing
- Profitability calculation assumes simple hourly rate model (no complex tiered billing)

---

## Design & Animation Requirements

This specification mandates **Animation-First Design**. Implementers MUST follow the Frontend Designer Skill workflow:

### Phase 1: Design Planning (Before Implementation)

**CRITICAL**: Before writing any implementation code, the implementing agent MUST:

1. **Define the "Epicenter of Design"**: Identify the ONE core interaction that makes this unforgettable. For TeamFlow, this is the **drag-and-drop task completion with celebration animation**.

2. **Use MCP Tools for Documentation**:
   - Use `context7` MCP to fetch latest docs for `dnd-kit`, `@better-auth`, `@tanstack/react-query`
   - Use `shadcn` MCP to fetch latest component templates (Card, Button, Sheet, Avatar)
   - Use `motion` MCP to verify Motion.dev syntax for `AnimatePresence`, `layout` prop, `drag` controls

3. **Draft the Choreography Script**:
   - **Page Load**: Skeleton fades out → Stats stagger in (0ms, 100ms, 200ms delays) → Board columns slide up
   - **Task Creation**: New card scales in from 80% to 100% with spring physics
   - **Drag Start**: Card scales to 105%, tilts 3 degrees, shadow increases
   - **Drag Over Column**: Drop zone pulses with glow effect
   - **Drop**: Card scales down to 100%, snaps to grid position
   - **Complete Task**: Confetti explosion or ripple effect radiates from card center

### Phase 2: Aesthetic Direction

**Tone**: Modern Industrial / Glass & Grain
- Think: Durable, professional, with premium touches
- Not: Playful, cartoonish, or overly minimal

**Typography** (BANNED: Inter, Roboto, Arial):
- Display Headers: *Clash Display* or *Space Grotesk* (bold, editorial)
- Body: *Geist* or custom sans-serif (clean, legible)

**Texture & Depth**:
- Glassmorphism on cards and overlays (backdrop-blur, subtle borders)
- Noise texture overlay on backgrounds for depth
- Gradient glows on active states
- Box-shadows that lift cards on hover (elevation hierarchy)

**Layout**:
- Bento-grid style dashboard (asymmetric rectangles)
- Generous padding and spacing
- High contrast for readability (WCAG AA compliant)

**Color Palette** (BANNED: Generic Purple #8b5cf6, #7c3aed, #a78bfa):
- **Primary (Brand)**: Lime Green (`#a3e635` - Lime 400) - Eco-modern theme, vibrant energy, distinctive from AI tools
- **Secondary**: Deep Black (`#18181b` - Zinc 900) - High contrast, professional
- **Accent**: Lime Green (`#a3e635` - Lime 400) with hover variant (`#84cc16` - Lime 500)
- **Backgrounds**: Pure White (light), Zinc 950 (dark)
- **Success**: Emerald (`#10b981`)
- **Warning**: Amber (`#f59e0b`)
- **Error**: Rose (`#f43f5e`)
- **Neutral Scale**: Zinc 50-900 (light mode), Zinc 950-50 (dark mode)

**CSS Custom Properties**:
```css
:root {
  --brand-primary: 84 100% 59%;      /* Lime Green #a3e635 */
  --brand-secondary: 240 5.9% 10%;   /* Deep Black #18181b */
  --accent: 83, 78%, 56%;             /* Lime 400 */
  --accent-hover: 83, 78%, 45%;       /* Lime 500 - for hover states */
  --background: 0 0% 100%;           /* White */
  --foreground: 240 10% 3.9%;        /* Zinc 950 */
}
```

**Rationale**: Lime green provides an eco-modern aesthetic that stands out from traditional corporate tools while maintaining professionalism. The high-contrast black & white foundation ensures excellent readability and WCAG AA compliance. The lime accent color is used sparingly for CTAs and interactive elements to create visual hierarchy.

### Phase 3: Implementation Rules

- **Motion.dev**: Use `layout` prop for all reordering animations; use `AnimatePresence` for items leaving DOM; use `whileHover` and `whileTap` for tactile feedback
- **Performance**: Use `will-change` on animating properties; avoid animating layout-triggering properties (top, left, width, height)
- **Shadcn Integration**: Wrap all shadcn components in `motion.div` for animation
- **Drag-and-Drop**: Use `@dnd-kit/core` combined with Motion.dev for physics-based dragging

---

## Implementation Directives for Agents

When implementing this specification, the following workflow is REQUIRED:

### Available Skills & Agents

This project has specialized skills and agents available. Use them where appropriate:

| Skill/Agent | Purpose | When to Use |
|-------------|---------|-------------|
| **`@.claude/agents/nextjs-frontend-architect.md`** ⭐ | **PRIMARY: Orchestrates all Next.js frontend implementation** | **USE FOR ALL FRONTEND TASKS** - This agent coordinates building-nextjs-apps, frontend-designer, theme-factory, and gemini-frontend-assistant skills |
| `@.claude/skills/building-nextjs-apps/` | Next.js 16 patterns, SSR-safe components, async params | When needing Next.js-specific patterns reference |
| `@.claude/skills/frontend-designer/` | Animation choreography, visual direction | For planning motion and aesthetics |
| `@.claude/skills/theme-factory/` | Professional color palettes and theming | When establishing visual identity |
| `@.claude/skills/gemini-frontend-assistant/` | Generate frontend code from descriptions | For rapid UI code generation |
| `@.claude/skills/better-auth-integration/` | Production-ready authentication patterns | When implementing auth flows |
| `.agent-better-auth-specialist` | Better Auth implementation expert | For complex auth scenarios |
| `@.claude/skills/ux-evaluator/` | Evaluate UX quality, identify issues | **AFTER** designing any flow/feature |
| `@.claude/skills/cli-deployment/` | Deployment patterns and scripts | When preparing for production |
| `@.claude/skills/deployment-engineer/` | CI/CD, Docker, K8s deployment | For infrastructure setup |
| `@.claude/skills/chatbot-widget-creator/` | ChatKit UI integration | If adding chat support |
| `@.claude/skills/rag-pipeline-builder/` | RAG implementation with FastAPI | If adding AI search |

**⭐ CRITICAL: All frontend implementation MUST use the `nextjs-frontend-architect` agent as the primary orchestrator.** This agent ensures SSR-safe patterns, proper Next.js 16 architecture, and coordinates all other frontend skills.

### Mandatory Implementation Workflow

**⭐ FOR ALL FRONTEND TASKS: Start with `@.claude/agents/nextjs-frontend-architect.md`**

The `nextjs-frontend-architect` agent orchestrates all frontend implementation by:
1. Reading specs/plans to understand requirements
2. Using `building-nextjs-apps` skill for Next.js 16 patterns (async params, SSR-safe components, etc.)
3. Using `theme-factory` skill for professional color palettes
4. Using `frontend-designer` skill for animation choreography
5. Using `gemini-frontend-assistant` skill for code generation

**General Implementation Workflow:**

1. **Documentation First**: Before writing any code, use `context7` MCP to fetch latest documentation for:
   - `dnd-kit` (drag and drop library)
   - `@better-auth` (authentication)
   - `@tanstack/react-query` (server state)
   - `motion` (animation library)

2. **Frontend Implementation** (via `nextjs-frontend-architect`):
   - Establish visual identity with `theme-factory`
   - Plan animation choreography with `frontend-designer`
   - Generate SSR-safe components with `gemini-frontend-assistant`
   - Ensure all patterns follow Next.js 16 best practices

3. **Authentication Implementation**: Use `@.claude/skills/better-auth-integration/` or invoke `.agent-better-auth-specialist` for:
   - JWT-based authentication setup
   - Agency/team data isolation
   - Session management
   - Protected routes

4. **Animation Verification**: Use `motion` MCP to verify correct syntax for:
   - `AnimatePresence` for exit animations
   - `layout` prop for smooth reordering
   - `drag` controls and constraints
   - `useMotionTemplate` for shared values

5. **Component Sourcing**: Use `shadcn` MCP to fetch:
   - Base components: Button, Card, Sheet, Avatar, Input
   - Form components: Form, Label, Select, Textarea
   - Do NOT manually write these components from memory

6. **UX Evaluation**: **MANDATORY after designing each major flow** — Use `@.claude/skills/ux-evaluator/` to evaluate:
   - Landing page conversion flow
   - Signup/login user experience
   - Task board usability
   - Dashboard information architecture
   - Any new feature or flow before implementation

### UX Evaluation Gates

After completing design for each of the following, **MUST** run `@.claude/skills/ux-evaluator/`:

- [ ] Landing page + signup flow
- [ ] Login page
- [ ] Dashboard layout
- [ ] Task board (drag-and-drop)
- [ ] Task detail drawer
- [ ] Archive/restore flow
- [ ] Team assignment flow

---

## Open Questions / Clarifications Needed

None at this time. All requirements have been specified with reasonable defaults documented in Assumptions.

---

## Dependencies

### External Dependencies
- **Phase 1 CLI**: The existing TeamFlow CLI (feature 001) provides the data model inspiration and user workflows
- **Authentication Provider**: Better Auth for JWT-based authentication
- **Database**: PostgreSQL-hosted service (Neon Serverless)
- **Component Library**: Shadcn UI for base components
- **Animation Library**: Motion.dev (Framer Motion) for all animations
- **Drag and Drop**: @dnd-kit for physics-based drag operations
- **State Management**: React Query for server state, Zustand for client state

### Internal Skills & Agents
- **`@.claude/agents/nextjs-frontend-architect.md`** ⭐ — **PRIMARY for all frontend implementation** - Orchestrates building-nextjs-apps, frontend-designer, theme-factory, and gemini-frontend-assistant
- `@.claude/skills/building-nextjs-apps/` — Next.js 16 patterns, SSR-safe components, breaking changes
- `@.claude/skills/theme-factory/` — Professional color palettes and theming
- `@.claude/skills/frontend-designer/` — Animation-first UI component generation
- `@.claude/skills/gemini-frontend-assistant/` — Frontend code generation
- `@.claude/skills/better-auth-integration/` — Authentication patterns and setup
- `.agent-better-auth-specialist` — Better Auth expert for complex scenarios
- `@.claude/skills/ux-evaluator/` — UX quality evaluation (run after each design)
- `@.claude/skills/deployment-engineer/` — CI/CD and deployment automation

---

## Definition of Done

This feature is complete when:

- [ ] All P1 and P2 user stories are implemented and passing
- [ ] All functional requirements (FR-001 through FR-047) are met
- [ ] All success criteria (SC-001 through SC-010) are verified
- [ ] Dashboard loads with stagger animations within 2 seconds
- [ ] Task drag-and-drop works with visual feedback (tilt, glow, snap)
- [ ] Completion celebration animation plays when tasks move to "Done"
- [ ] Authentication and multi-tenancy data isolation is verified
- [ ] Time logging and profitability calculations are accurate
- [ ] Application is responsive and functional on mobile devices (320px+)
- [ ] Lighthouse performance score is 90+ (Performance, Accessibility, Best Practices)
- [ ] No console errors or warnings in production build
- [ ] All animations run at 60fps on target hardware
