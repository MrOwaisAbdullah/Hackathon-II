# Phase 2: TeamFlow Full-Stack Web App Architecture Plan Prompt

You are acting as the **Chief Technical Architect** for TeamFlow. Your goal is to generate the **Technical Implementation Plan** (`sp.plan`) for Phase 2 based on the approved specification.

## Context
We are executing **Phase 2: Full-Stack Web App** of the TeamFlow Agency CRM.
The requirements are defined in `@specs/002-fullstack-web-crm/spec.md`.
This project mandates **Spec-Driven Development** and **Animation-First Design**.

## Directive
Run the `sp.plan` process to generate the architecture plan file.
**CRITICAL INSTRUCTION:** You MUST adhere to the **Frontend Designer Skill** workflow (`@.claude/skills/frontend-designer/SKILL.md`) for all UI/UX components in this plan.

---

### 1. Architectural Vision
- **Goal:** Transform the Phase 1 CLI logic into a high-performance, event-driven web application.
- **Frontend:** Next.js 16 (App Router), Tailwind CSS (Variable-First), Shadcn UI, Motion.dev.
- **Backend:** FastAPI (Python), SQLModel, Neon PostgreSQL.
- **Auth:** Better Auth (JWT-based, with middleware for tenant isolation).
- **State:** React Query (Server), Zustand (Client).

### 2. Required Plan Sections

#### A. Data Model & Schema
Define the full database schema for Neon PostgreSQL using SQLModel.
- **Users & Teams:** `User`, `Agency` (Tenant), `Team`.
- **Work:** `Project`, `Task` (with recursive/parent support optional), `TaskStatus` (Enum).
- **Time:** `TimeEntry` (linked to User and Task).
- **Relationships:** Define all foreign keys and cascade rules.

#### B. API Architecture (FastAPI)
Define the REST API structure.
- **Endpoints:** Map all `FR-XXX` requirements to specific endpoints (e.g., `POST /tasks`, `PATCH /tasks/{id}/move`).
- **Middleware:** Auth middleware (verify JWT), Tenant middleware (ensure `agency_id` scope).
- **Error Handling:** Standardized error responses (Problem Details RFC).

#### C. Frontend Architecture (The "Frontend Designer" Mandate)
**Constraint:** This section MUST be detailed and use the `frontend-designer` skill's "Phase 2.5: Design Tokens" approach.
- **Theme System:** Define CSS variables for colors, spacing, and blurs (e.g., `--brand-epicenter`, `--surface-glass`).
- **Component Hierarchy:** Break down the UI into atomic components (e.g., `TaskCard`, `KanbanColumn`, `StatWidget`).
- **Animation Strategy:** Explicitly plan the "Choreography" for key interactions (e.g., `KanbanBoard` uses `layout` prop, `TaskCard` uses `whileHover`).

#### D. Implementation Steps (Phased Rollout)
Break down the implementation into logical steps:
1.  **Foundation:** Repo setup, DB connection, Auth integration.
2.  **Core Domain:** CRUD APIs for Tasks/Projects.
3.  **UI Shell:** Layout, Sidebar, Theme setup.
4.  **Feature: Dashboard:** Stats and visualizations.
5.  **Feature: Kanban:** Drag-and-drop logic (dnd-kit + motion).
6.  **Refinement:** Animation tuning, error states, responsive check.

### 3. Implementation Directives (MCP & Tools)
Explicitly list the tools/skills required for each step:
- **Planning:** "Use `frontend-designer` skill to mock up the Kanban board structure."
- **Docs:** "Use `context7` to fetch `dnd-kit` sorting strategies."
- **Auth:** "Use `better-auth-specialist` agent for JWT setup."

---

## Output Requirement
Generate the `sp.plan` file. It must be a concrete, actionable blueprint that a developer (or agent) can follow to build the system without ambiguity. Ensure strict alignment with `specs/002-fullstack-web-crm/spec.md`.
