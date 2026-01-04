# Feature Specification: TeamFlow Complete Dashboard Workflow (Phase 2 Improvement)

**Feature Branch**: `002-fullstack-web-crm` (improvement)
**Created**: 2025-01-03
**Status**: Draft
**Input**: User description: "Complete the full workflow of the dashboard from start to end - add projects, teams, settings, adding, editing, assigning, deleting tasks, log time. All CRUD functionality for Projects and Team management must work end-to-end."

---

## Executive Summary

This specification defines the **complete CRUD functionality** for TeamFlow's Phase 2 web application. While the foundation has been built (authentication, task board, dashboard analytics), critical user-facing workflows remain incomplete. This improvement adds full Create, Read, Update, Delete operations for **Team Management** and **Project Management**, enabling the complete agency workflow from onboarding team members to organizing projects and tracking deliverables.

**Scope**: This improvement completes the missing CRUD operations identified in the current implementation:
- Backend: User management endpoints (POST, PATCH, DELETE)
- Frontend: Project creation, editing, and deletion
- Frontend: Team member addition, editing, and removal
- Navigation: Archive page access from sidebar

---

## Clarifications

### Session 2025-01-03

- **Q: How should temporary passwords be handled regarding expiration and reusability?**
  - **A: Temporary password expires in 7 days and user must change on first login**
- **Q: How should the system handle concurrent edits to the same user record?**
  - **A: Last-write-wins — most recent edit overwrites previous changes**
- **Q: Who should be able to create, edit, and delete projects?**
  - **A: Mixed - admins and users with "project manager" designation can manage projects; regular members have read-only access**
- **Q: What level of audit logging should be implemented for user and project management operations?**
  - **A: Basic audit - log user CRUD actions (who, what, when) for admin operations**
- **Q: Who should be able to designate a user as a project manager?**
  - **A: Admin only - only admins can set/clear is_project_manager flag**

---

## User Scenarios & Testing

### User Story 3-A - Team Management CRUD (Priority: P1)

**Journey**: As an Agency Admin, I want to manage team members (add, edit, remove) so that I can control who has access to my agency and assign work appropriately.

**Why this priority**: Team management is foundational for any agency workflow. Without the ability to add or remove team members, the application cannot support real agency growth or personnel changes.

**Independent Test**: Can be fully tested by creating a new team member, editing their role, and deleting them - all actions persist and reflect correctly in the team list.

**Acceptance Scenarios**:

1. **Given** I am logged in as an admin, **When** I click "Add Team Member" and fill in the form (name, email, role), **Then** a new user is created with a temporary password displayed to me
2. **Given** I am viewing the team list, **When** I click edit on a team member and change their role, **Then** the role updates immediately and persists across page refresh
3. **Given** I am viewing the team list, **When** I click delete on a team member and confirm, **Then** the member is removed from the list and their assigned tasks become unassigned
4. **Given** I attempt to delete the last admin in the agency, **When** I confirm the deletion, **Then** the system shows an error message "Cannot delete the last admin" and the user is not deleted
5. **Given** I attempt to create a user with an email that already exists in my agency, **When** I submit the form, **Then** the system shows an error "Email already exists in this agency"
6. **Given** I create a new team member, **When** the creation completes, **Then** a temporary password is generated and displayed in a success message for me to share with the new user
7. **Given** a new user logs in with a temporary password for the first time, **When** authentication succeeds, **Then** they are prompted to change their password before accessing the application
8. **Given** a temporary password has expired (older than 7 days), **When** the user attempts to log in, **Then** the system shows an error "Password has expired. Please contact your admin to generate a new temporary password."
9. **Given** I am editing a team member as an admin, **When** I check the "Project Manager" checkbox and save, **Then** the user gains project management permissions
10. **Given** I am a non-admin attempting to set a user as project manager, **When** I submit the edit, **Then** the system returns 403 Forbidden with "Only admins can modify project manager designation"

---

### User Story 2-B - Project Management CRUD (Priority: P1)

**Journey**: As a Project Manager, I want to manage projects (create, edit, delete) so that I can organize my team's work and track deliverables for different clients or initiatives.

**Why this priority**: Projects are the organizing unit for agency work. Without project CRUD, teams cannot organize work beyond a flat list, making scalability impossible.

**Independent Test**: Can be fully tested by creating a new project, editing its name and status, and deleting it - all actions persist and the project list updates correctly.

**Acceptance Scenarios**:

1. **Given** I am on the Projects page, **When** I click "New Project" and fill in the name (required) and description (optional), **Then** a new project is created and appears in the project list
2. **Given** I am viewing the project list, **When** I click edit on a project and change the status from "active" to "on-hold", **Then** the status badge updates immediately
3. **Given** I am viewing the project list, **When** I click delete on a project, **Then** a confirmation dialog appears with warning "This will archive all tasks in this project (restorable from Archive page)"
4. **Given** I confirm the project deletion, **When** the deletion completes, **Then** the project is removed from the list and all its tasks are moved to the Archive page
5. **Given** I attempt to create a project without a name, **When** I submit the form, **Then** the system shows "Project name is required" and does not create the project
6. **Given** I create a project with a name over 100 characters, **When** I submit the form, **Then** the system shows validation error "Name must be 100 characters or less"
7. **Given** I am logged in as a regular member (not admin or project manager), **When** I view the Projects page, **Then** I do not see "New Project", "Edit", or "Delete" buttons
8. **Given** I am a regular member attempting to create a project via API, **When** the request is processed, **Then** the system returns 403 Forbidden with "Insufficient permissions"

---

### User Story 4-C - Navigation Enhancement (Priority: P3)

**Journey**: As a User, I want to access the Archive page from the sidebar so that I can restore deleted items without navigating manually.

**Why this priority**: Low priority - this is a convenience improvement. The Archive page exists but is not discoverable. Adding the link improves UX but does not block core workflows.

**Independent Test**: Can be fully tested by clicking the Archive link in the sidebar and verifying navigation to the Archive page.

**Acceptance Scenarios**:

1. **Given** I am viewing any page in the application, **When** I look at the sidebar navigation, **Then** I see an "Archive" link between "Time Entries" and "Settings"
2. **Given** I click the "Archive" link in the sidebar, **When** the navigation completes, **Then** I am taken to the /archive page showing all archived items
3. **Given** I am on the Archive page, **When** I look at the sidebar, **Then** the "Archive" link is highlighted as the active navigation item

---

### Edge Cases

- What happens when a team member is deleted while they have assigned tasks? → Tasks become unassigned (assignee_id set to null), displaying an empty avatar placeholder
- What happens when two admins try to delete the last admin simultaneously? → First request succeeds, second request fails with "Cannot delete last admin" error
- What happens when a project is deleted that has 100+ tasks? → All tasks are archived in a batch operation, confirmation warns about the volume
- What happens when a user tries to edit a project that was just deleted by another user? → Edit fails with "Project not found" error, list refreshes automatically
- What happens when network connection is lost during user creation? → Form shows loading spinner until timeout, then displays error with "Retry" option
- What happens when email validation fails on user creation? → Inline error shows "Invalid email format" and highlights the email field
- How does the system handle duplicate project names within an agency? → Project names are not required to be unique (different projects can have the same name), but a warning may be shown
- What happens when a user tries to log in with an expired temporary password? → Login fails with "Password has expired. Please contact your admin to generate a new temporary password."
- What happens when two admins edit the same team member simultaneously? → Last-write-wins — most recent edit overwrites previous changes; polling (10s) updates other admins' views

---

## Requirements

### Functional Requirements

#### Team Management

- **FR-001**: System MUST allow admins to create new team members with name, email, role, and auto-generated temporary password
- **FR-002**: System MUST validate that email addresses are unique within an agency before creating a user
- **FR-003**: System MUST allow admins to edit team member name, email, role, and project manager designation via a modal form
- **FR-003-A**: System MUST enforce admin-only access for modifying is_project_manager flag; non-admins cannot grant or revoke project manager status
- **FR-004**: System MUST prevent deletion of the last admin in an agency (minimum one admin required)
- **FR-005**: System MUST soft-delete team members (set active=False) instead of hard deletion
- **FR-006**: When a team member is deleted, all tasks assigned to that member MUST become unassigned (assignee_id set to null)
- **FR-007**: System MUST display the temporary password to the admin after user creation for sharing with the new user
- **FR-008**: System MUST enforce minimum password length of 8 characters for new users
- **FR-008-A**: Temporary passwords MUST expire after 7 days and users MUST be required to change their password on first login

#### Project Management

- **FR-009**: System MUST allow users to create projects with name (required), description (optional), and status (active/on-hold/completed)
- **FR-010**: System MUST validate that project name is provided and does not exceed 100 characters
- **FR-011**: System MUST allow users to edit project name, description, and status via a modal form
- **FR-012**: System MUST preserve the creation date and creator when editing a project
- **FR-013**: System MUST show a confirmation dialog when deleting a project with the message "This will archive all tasks in this project (restorable from Archive page)"
- **FR-014**: When a project is deleted, all tasks in that project MUST be moved to Archive (status set to ARCHIVED)
- **FR-015**: System MUST allow restoration of archived projects and their tasks from the Archive page

#### Navigation

- **FR-016**: System MUST display an "Archive" link in the sidebar navigation between "Time Entries" and "Settings"
- **FR-017**: The Archive link MUST navigate to the /archive page when clicked
- **FR-018**: The Archive link MUST be highlighted as active when the user is on the Archive page

#### User Interface

- **FR-019**: All forms MUST show loading states during API mutations (spinner on submit button)
- **FR-020**: All forms MUST display error messages inline when validation or API errors occur
- **FR-021**: All successful mutations MUST refresh the relevant data lists automatically
- **FR-022**: Delete actions MUST require explicit user confirmation before proceeding
- **FR-023**: Forms MUST use Shadcn UI Dialog/Modal components for consistency
- **FR-024**: All forms MUST close automatically on successful submission

#### API Endpoints

- **FR-025**: Backend MUST provide POST /api/v1/users endpoint for creating team members
- **FR-026**: Backend MUST provide PATCH /api/v1/users/{id} endpoint for updating team members
- **FR-027**: Backend MUST provide DELETE /api/v1/users/{id} endpoint for soft-deleting team members
- **FR-028**: Backend MUST enforce admin-only access for user creation, update, and deletion operations
- **FR-029**: Backend MUST return 403 Forbidden when non-admins attempt to modify team members
- **FR-030**: Backend MUST return 404 Not Found when attempting to edit/delete non-existent users
- **FR-031**: Backend MUST enforce project management access control: only admins and users with is_project_manager=True can create, edit, or delete projects
- **FR-032**: Backend MUST return 403 Forbidden when non-admin/non-project-manager users attempt to modify projects
- **FR-033**: Frontend MUST hide "New Project", "Edit", and "Delete" buttons from users without project management permissions

#### Observability & Audit Logging

- **FR-034**: Backend MUST log all user CRUD operations (create, update, delete) with admin user ID, target user ID, action, and timestamp
- **FR-035**: Backend MUST log all project deletion operations with user ID, project ID, and timestamp
- **FR-036**: Audit logs MUST be queryable for security review and compliance purposes

---

### Key Entities

- **User**: Represents a team member in the agency. Key attributes: id, name, email, hashed_password, role (admin/member), agency_id, active (boolean for soft delete), password_expires_at (datetime for temporary password expiration), must_change_password (boolean flag for first login), is_project_manager (boolean flag granting project CRUD permissions). Has relationships to assigned tasks and time entries.

- **UserCreate**: Schema for creating new users. Required fields: name, email, password, role. Password will be auto-generated by backend if not provided.

- **UserUpdate**: Schema for updating existing users. All fields optional: name, email, role, is_project_manager. Password changes handled separately (not in this workflow).

- **Project**: Represents a collection of tasks for a client or initiative. Key attributes: id, name, description, status (active/on-hold/completed), agency_id, created_at. Has many Tasks.

- **ProjectCreate**: Schema for creating projects. Required: name. Optional: description, status (defaults to "active").

- **ProjectUpdate**: Schema for updating projects. All fields optional: name, description, status.

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Admins can add a new team member and see them appear in the team list within 2 seconds
- **SC-002**: Users can create a new project and see it appear in the project list within 1 second
- **SC-003**: Deleting a team member successfully unassigns all their tasks (verified by checking task count changes)
- **SC-004**: Deleting a project successfully moves all its tasks to Archive (verified by Archive page task count)
- **SC-005**: System prevents deletion of the last admin with appropriate error message
- **SC-006**: All forms provide visual feedback (loading state) within 100ms of submission
- **SC-007**: All form errors display inline with clear, actionable messages
- **SC-008**: Archive link is visible in sidebar and navigates correctly on first click
- **SC-009**: 95% of users can complete the full "add team member → assign tasks → delete team member" workflow without assistance
- **SC-010**: Email uniqueness validation prevents duplicate emails within the same agency 100% of the time

---

## Constraints & Assumptions

### Constraints

- **Authentication Required**: All team and project management operations require authenticated admin users
- **Multi-Tenancy**: All data is scoped to the current agency_id from the authenticated user's session
- **Backend Framework**: FastAPI with SQLModel and PostgreSQL
- **Frontend Framework**: Next.js 16 with React Query and Shadcn UI
- **Admin-Only Operations**: User CRUD operations are restricted to admin role only
- **Soft Delete Pattern**: User and project deletion uses soft delete (active=False) for data recovery

### Assumptions

- Agencies have 2-50 team members (small to medium-sized agencies)
- Admins are trusted to manage team members appropriately
- Temporary passwords for new users will be shared securely outside the application (email not sent in this phase)
- Projects can have the same name within an agency (no uniqueness constraint)
- Task reassignment on user deletion is acceptable (no automatic reassignment logic)
- Archive page already exists and can display archived items
- Backend authentication middleware (JWT) is already functional and validates admin role

---

## Dependencies

### External Dependencies

- **Existing Feature 002**: This improvement builds upon the foundation laid in 002-fullstack-web-crm (authentication, task board, dashboard)
- **Shadcn UI Components**: Dialog, Form, Button, Select, Textarea components for forms
- **React Query**: For optimistic updates and cache invalidation
- **Backend Models**: User, Project models already exist in the database

### Internal Dependencies

- **User Model**: `app/models/user.py` must include UserUpdate schema (to be added)
- **User Service**: `app/services/user_service.py` must include create, update, delete methods (to be added)
- **User Endpoints**: `app/api/endpoints/users.py` must include POST, PATCH, DELETE routes (to be added)
- **Project Service**: `app/services/project_service.py` already has CRUD methods (verify before use)
- **Project Endpoints**: `app/api/endpoints/projects.py` already has CRUD routes (verify before use)
- **Frontend Query Hooks**: `frontend/src/lib/query.ts` must include user and project mutation hooks (to be added)
- **Frontend Forms**: New components to be created:
  - `frontend/src/components/team/UserForm.tsx` (NEW)
  - `frontend/src/components/project/ProjectForm.tsx` (NEW)

---

## Definition of Done

This feature improvement is complete when:

- [ ] Backend POST /api/v1/users endpoint creates users with hashed passwords and returns UserRead
- [ ] Backend PATCH /api/v1/users/{id} endpoint updates user name, email, or role
- [ ] Backend DELETE /api/v1/users/{id} endpoint soft-deletes users and unassigns tasks
- [ ] Backend prevents deletion of the last admin (returns 400 or 403)
- [ ] Backend enforces email uniqueness within agency on user creation
- [ ] Frontend "Add Team Member" button opens modal form
- [ ] Frontend user creation form validates email format and password length
- [ ] Frontend displays temporary password after successful user creation
- [ ] Frontend "New Project" button opens modal form
- [ ] Frontend project creation form validates name required and max length
- [ ] Frontend edit buttons on UserCard and ProjectCard open pre-filled modals
- [ ] Frontend delete actions show confirmation dialogs with appropriate warnings
- [ ] Frontend forms show loading states during API mutations
- [ ] Frontend forms show error messages on validation or API failure
- [ ] Frontend lists refresh automatically after successful mutations
- [ ] Sidebar includes Archive link between Time Entries and Settings
- [ ] Archive link navigates to /archive page and highlights as active
- [ ] All mutations invalidate relevant React Query caches
- [ ] E2E tests cover: create user → edit user → delete user workflow
- [ ] E2E tests cover: create project → edit project → delete project workflow
- [ ] Manual testing confirms no console errors during any CRUD operation
- [ ] All forms close automatically on successful submission
