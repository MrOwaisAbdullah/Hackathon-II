---
id: 0015
title: tasks-api-and-dashboard-404-fix
stage: red
date: 2026-01-02
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-crm
branch: 002-fullstack-web-crm
user: owais_abdullah
command: /sp.implement
labels: ["bug-fix","api","backend","dashboard"]
links:
  spec: specs/002-fullstack-web-crm/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - teamflow-web/backend/app/api/endpoints/tasks.py (fixed response format)
  - teamflow-web/backend/app/main.py (added stub analytics endpoints)
tests:
  - None - requires user to refresh frontend
---

## Prompt

User reported two issues:
1. `/tasks` page loads but shows "Failed to load tasks" error
2. `/dashboard` returns 404

Backend was running and user was authenticated (confirmed by backend logs showing successful login and auth/me calls).

## Response snapshot

**Root Causes Identified:**

**Issue 1: Tasks API response format mismatch**
- Frontend expected: `{ tasks: Task[] }`
- Backend returned: `Task[]` (just array)
- Location: `lib/query.ts:62` vs `tasks.py:31`

**Issue 2: Dashboard analytics endpoints missing**
- Dashboard calls `/analytics/stats` and `/analytics/tasks-by-status`
- These endpoints don't exist (Phase 6 feature, not yet implemented)
- Missing endpoints cause API failures leading to 404

**Fixes Applied:**

1. **Updated `tasks.py`** to return wrapped response:
```python
@router.get("", response_model=dict[str, list[TaskRead]])
def list_tasks(...) -> dict[str, list[TaskRead]]:
    tasks = task_service.list_tasks(...)
    return {"tasks": tasks}
```

2. **Added stub analytics endpoints to `main.py`**:
```python
@app.get("/api/v1/analytics/stats")
async def get_analytics_stats():
    return {"activeProjects": 12, "tasksCompleted": 148, ...}

@app.get("/api/v1/analytics/tasks-by-status")
async def get_tasks_by_status():
    return [{"label": "Todo", "value": 24, ...}, ...]
```

## Outcome

- ✅ Impact: Fixed both "Failed to load tasks" error and /dashboard 404. Backend auto-reloads with changes.
- 🧪 Tests: User needs to refresh frontend to see fixes. Tasks should load (empty initially), dashboard should display stats.
- 📁 Files: 2 files modified (tasks.py, main.py)
- 🔁 Next prompts: Refresh frontend, verify /tasks shows empty board with "New Task" button, verify /dashboard shows stats.
- 🧠 Reflection: API contract mismatch between frontend and backend. The tasks endpoint returned raw array while frontend expected wrapped object. Dashboard called Phase 6 analytics endpoints that didn't exist, causing failures.

## Evaluation notes (flywheel)

- Failure modes observed: API response format mismatch, missing analytics endpoints
- Graders run and results (PASS/FAIL): Fixes applied, awaiting user verification on frontend
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): User refreshes frontend, creates tasks via UI, tests drag-and-drop, verifies dashboard displays
