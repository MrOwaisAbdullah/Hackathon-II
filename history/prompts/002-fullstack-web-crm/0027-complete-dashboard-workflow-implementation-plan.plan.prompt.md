---
id: 0027
title: Complete Dashboard Workflow Implementation Plan
stage: plan
date: 2026-01-03
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-crm
branch: 002-fullstack-web-crm
user: User
command: /sp.plan
labels: [phase2, complete-workflow, user-crud, project-crud, mobile-responsive, navigation, planning]
links:
  spec: specs/002-fullstack-web-crm/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fullstack-web-crm/plan.md (updated)
  - specs/002-fullstack-web-crm/research.md (updated with Phase 2 improvement research)
  - specs/002-fullstack-web-crm/data-model.md (updated User entity with new fields)
  - specs/002-fullstack-web-crm/contracts/openapi.yaml (updated user endpoints and schemas)
  - specs/002-fullstack-web-crm/AGENT_CONTEXT.md (updated with Phase 10 section)
tests:
  - None (planning phase, no code changes)
---

## Prompt

User invoked `/sp.plan` with comprehensive input for implementing the "Complete Dashboard Workflow" improvement. Key requirements included:

### Target Feature
- Feature: 002-fullstack-web-crm (Phase 2 Complete Workflow Improvement)
- Focus: Mobile-Responsive UI/UX + Complete End-to-End Workflow Functionality

### Implementation Phases Provided
1. **Phase 1: Backend User Management CRUD** (HIGH PRIORITY)
   - POST /api/v1/users - Create new team member with auto-generated temp password
   - PATCH /api/v1/users/{id} - Update user (name, email, role)
   - DELETE /api/v1/users/{id} - Delete/deactivate user (soft delete)

2. **Phase 2: Mobile-Responsive Dashboard Layout** (HIGH PRIORITY)
   - Mobile navigation (hamburger menu + Sheet component)
   - Responsive patterns (full-screen dialogs on mobile)

3. **Phase 3: Frontend Project Management** (HIGH PRIORITY)
   - ProjectForm.tsx - Create/edit project modal
   - ProjectCard.tsx - Enhanced project card with actions

4. **Phase 4: Frontend Team Management** (HIGH PRIORITY)
   - UserForm.tsx - Create/edit user modal
   - UserCard.tsx - Enhanced user card with actions

5. **Phase 5: Navigation Enhancement** (LOW PRIORITY)
   - Add Archive link to sidebar

### User Model Extensions (Phase 2)
- `active: bool` (default=True) - Soft delete
- `is_project_manager: bool` (default=False) - PM permissions
- `password_expires_at: Optional[datetime]` - Temp password expiration
- `must_change_password: bool` (default=False) - Force password change on first login

### Theme Specifications ("Eco-Modern" - DoQuanta Inspired)
- Foundation: High-contrast Black & White (zinc-950/zinc-50)
- Primary Accent: Vibrant Lime Green (lime-400/#a3e635)
- Sidebar: Permanent dark sidebar (zinc-950) regardless of theme
- Typography: High-impact headers with font-black tracking-tighter uppercase
- Elevation: .card-float with refined shadows

### Key Directives
- Use existing AGENT_CONTEXT.md and plan.md for theme, colors, learnings
- Follow existing infrastructure (logging, rate limiting, security patterns)
- Mobile-first with Tailwind responsive classes (sm:, md:, lg:)
- Use Shadcn Sheet for mobile navigation, Dialog for forms

## Response snapshot

Successfully completed `/sp.plan` workflow and generated comprehensive implementation plan:

### Phase 0: Research Complete
- Updated `research.md` with Phase 2 improvement research findings
- Documented User model extensions, permission model, mobile patterns
- Added audit logging and rate limiting patterns

### Phase 1: Data Model & API Contracts Complete
- Updated `data-model.md` with new User fields and Pydantic schemas
- Updated `contracts/openapi.yaml` with:
  - New endpoints: POST, PATCH, DELETE /users
  - Updated User schema with Phase 2 fields
  - New schemas: UserCreate, UserUpdate, UserReadWithTempPassword

### Plan Generation Complete
- Filled `plan.md` with 5 implementation phases
- Included technical context, constitution check, project structure
- All 12 constitution principles passed

### Agent Context Updated
- Added Phase 10 section to AGENT_CONTEXT.md
- Documented new User model fields, API endpoints, mobile patterns
- Listed frontend components to create and implementation order

## Outcome

- ✅ Impact: High - Completes missing CRUD functionality for User and Project management, enables mobile-responsive workflows
- 🧪 Tests: None (planning phase only)
- 📁 Files: 5 files updated (plan.md, research.md, data-model.md, openapi.yaml, AGENT_CONTEXT.md)
- 🔁 Next prompts: `/sp.tasks` to generate testable implementation tasks, then `/sp.implement` to execute
- 🧠 Reflection: Planning phase completed successfully. All architecture decisions documented. Ready for task generation and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - workflow proceeded smoothly
- Graders run and results (PASS/FAIL): N/A - planning phase
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): None - proceed to task generation with `/sp.tasks`
