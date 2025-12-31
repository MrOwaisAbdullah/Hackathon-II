---
id: "0001"
title: "Phase 2 fullstack web CRM specification"
stage: spec
date: 2025-01-29
surface: agent
model: claude-opus-4-5-20251101
feature: "002-fullstack-web-crm"
branch: 002-fullstack-web-crm
user: owais
command: /sp.specify
labels: ["spec","phase2","frontend-design","crm","hackathon"]
links:
  spec: specs/002-fullstack-web-crm/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-fullstack-web-crm/spec.md
  - specs/002-fullstack-web-crm/checklists/requirements.md
tests: []
---

## Prompt

# Phase 2: TeamFlow Full-Stack Web App Specification Prompt

You are acting as the **Chief Product Officer & Lead Frontend Architect** for TeamFlow. Your goal is to generate the **Specify (Requirement Specification)** for Phase 2 of the project.

## Context
We are evolving TeamFlow from a CLI tool into a **Full-Stack Agency CRM**.
**Phase 2** is the "Full CRM" Web Application.
This is NOT a standard "Todo App". It is a high-performance, visually stunning tool for creative agencies to manage complex work.

**Core Functionality (The "Todo" Backbone):**
While this is a CRM, it **MUST** rigorously implement the core Hackathon Phase 2 requirements (Basic Level Features), but flavored for an agency context:
1.  **Add Task** → "Create Agency Deliverable"
2.  **Delete Task** → "Archive Project Task"
3.  **Update Task** → "Refine Scope"
4.  **View Task List** → "Project Backlog View"
5.  **Mark as Complete** → "Deliver & Close"

## Directive
Run the `sp.specify` process to generate the requirements file (`speckit.specify`).
**CRITICAL INSTRUCTION:** For the UI/UX section, you MUST strictly follow the **Frontend Designer Skill** workflow (`@.claude/skills/frontend-designer/SKILL.md`).
- **Plan First:** Use the `frontend-designer` skill to explicitly plan the "Epicenter of Design" and animation choreography before any implementation specs are written.
- **Tools:** Explicitly mandate the use of `context7` (for docs), `shadcn` (for components), and `motion` (for animations) MCP tools.

---

### 1. Project Overview
- **Name:** TeamFlow Web (Phase 2)
- **Type:** Full-Stack Web Application (Next.js 16 + FastAPI)
- **Design Philosophy:** **"Bold & Tactile"** (See Frontend Designer Skill).
    - Avoid "Safe/Corporate" AI cliches (Standard Bootstrap/Material layouts).
    - Aim for: Micro-interactions, fluid layouts, glassmorphism, and deep/rich textures.
- **Persistence:** Neon Serverless PostgreSQL + SQLModel.

### 2. User Stories & Core Features (CRM Extended from Todo)

#### A. Authentication & Access (Better Auth)
*As an Agency Owner, I want...*
- **Secure Sign-up/Login:** Using Better Auth with JWT.
- **Team Isolation:** Data strictly scoped to my agency/team.

#### B. The Agency "Command Center" (Dashboard)
*As a Project Manager, I want a Dashboard that feels like a HUD...*
- **Visuals:** High-contrast stats (Active Projects, Revenue, Team Utilization).
- **Interaction:** Cards that "lift" on hover, charts that animate in.
- **Layout:** Bento-grid style layout for density and clarity.

#### C. Drag-and-Drop Task Board (The Core "Todo" Experience)
*As a Creative Director, I want to distribute work...*
- **Kanban Board:** Drag tasks between columns (Todo, Doing, Review, Done).
- **Physics:** Dragged items should have weight/inertia (using `dnd-kit` + `framer-motion`).
- **Assign:** Drag a user avatar onto a task card to assign them.
- **Core CRUD:**
    - **Add:** Quick-add from any column (CMD+K style or inline).
    - **Edit:** Click card to open a "Sheet" (side drawer) with rich text editor.
    - **Delete:** Drag to a "Trash Can" drop zone or right-click context menu.
    - **Complete:** "Confetti" celebration or satisfaction ripple effect when dragging to "Done".

#### D. Time & Profitability
*As a CFO, I want real-time financials...*
- **Time Logging:** A slick, modal-based timer or manual entry linked to tasks.
- **Profitability:** Live calculation of (Billable Hours * Rate) - (Cost).

### 3. Frontend Architecture & Design (The "Frontend Designer" Mandate)

**Constraint:** You must use the `frontend-designer` skill to define these specs.

#### Aesthetic Direction: "Modern Industrial" or "Glass & Grain"
- **Typography:** Large, editorial headers (e.g., *Clash Display* or *Space Grotesk*) + clean sans-serif body.
- **Motion:**
    - **Page Transitions:** No hard cuts. Content glides in.
    - **Micro-interactions:** Buttons press down, toggles snap, lists stagger in.
    - **Layout Animations:** When a filter is applied, items shuffle positions smoothly (using `framer-motion` layout prop).

#### Tech Stack (Frontend)
- **Framework:** Next.js 16 (App Router)
- **Styling:** Tailwind CSS (extended config for custom fonts/easing)
- **Components:** Shadcn UI (base) + Custom Motion Wrappers
- **State:** React Query (server state) + Zustand (client state)

#### Tech Stack (Backend)
- **Framework:** FastAPI
- **Database:** Neon PostgreSQL (via SQLModel)
- **Auth:** Better Auth (Python integration via JWT verification middleware)

### 4. Implementation Strategy (MCP Usage)
In the spec, explicit instructions must be given to the implementing agent:
1.  **Docs First:** "Use `context7` to fetch latest docs for `dnd-kit` and `better-auth` before coding."
2.  **Visuals:** "Use `frontend-designer` skill to generate the component structure for the Kanban board."
3.  **Animation:** "Use `motion` MCP to verify `AnimatePresence` syntax."

### 5. Acceptance Criteria Examples
- **Scenario: Dragging a Task**
    - **Visual:** Task card tilts slightly when lifted. Drop zones highlight/pulse.
    - **Functional:** Task status updates in DB immediately; optimistic UI update ensures no lag.
- **Scenario: Dashboard Load**
    - **Visual:** Skeleton screens fade out -> Content staggers in (Hero stats first, then lists).
    - **Performance:** LCP < 1.5s.

---

## Output Requirement
Generate the `sp.specify` file. It must be detailed enough that a developer (or agent) can't "boring-ify" the design. It must enforce the **Animation-First** approach while ensuring the **Core Todo Functionality** is rock solid.

## Response snapshot

Generated comprehensive specification for TeamFlow Phase 2 Full-Stack Agency CRM with:
- 6 prioritized user stories (P1-P3) covering authentication, task board, team collaboration, dashboard, time tracking, and editing
- 43 functional requirements across all feature areas
- 5 key entities defined (Agency, User, Task, TimeEntry, Project)
- 10 measurable success criteria
- Animation-first design requirements with choreography script
- Implementation directives mandating MCP tool usage for docs, components, and animation verification

Specification created at: `specs/002-fullstack-web-crm/spec.md`
Quality checklist: `specs/002-fullstack-web-crm/checklists/requirements.md`
All validation checks passed - ready for `/sp.plan` or `/sp.clarify`

## Outcome

- ✅ Impact: Complete specification generated for Phase 2 full-stack web CRM with 6 user stories, 43 functional requirements, and 10 success criteria
- 🧪 Tests: Quality checklist validation passed all items
- 📁 Files: spec.md (384 lines), checklists/requirements.md created
- 🔁 Next prompts: `/sp.plan` to generate architecture plan, `/sp.clarify` if questions arise
- 🧠 Reflection: Spec successfully balances user-facing requirements with animation-first design mandates. Implementation directives section properly separates constraints from implementation details.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All checklist items PASSED
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
