---
id: 0016
title: dashboard-404-analytics-api-path-fix
stage: red
date: 2026-01-02
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-crm
branch: 002-fullstack-web-crm
user: owais_abdullah
command: /sp.implement
labels: ["bug-fix","api","dashboard","analytics"]
links:
  spec: specs/002-fullstack-web-crm/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - teamflow-web/frontend/src/lib/query.ts (fixed analytics API paths)
tests:
  - Dashboard should now load with stats cards and charts
---

## Prompt

User reported: "still no dashboard page"

Previous fixes had already:
1. Fixed tasks API response format to return `{ tasks: [...] }` instead of raw array
2. Added stub analytics endpoints to backend (`/api/v1/analytics/stats`, `/api/v1/analytics/tasks-by-status`)

Despite these fixes, dashboard continued to return 404.

## Response snapshot

**ROOT CAUSE**: Analytics API calls in frontend used incorrect paths.

**Investigation Findings:**

The `api` client in `lib/api.ts` has baseURL `http://localhost:8000` (no `/api/v1` prefix).

But analytics hooks in `lib/query.ts` were calling:
- Line 23: `api.get('/analytics/stats')` → hits `http://localhost:8000/analytics/stats` (404)
- Line 35: `api.get('/analytics/tasks-by-status')` → hits `http://localhost:8000/analytics/tasks-by-status` (404)

Backend serves analytics at:
- `/api/v1/analytics/stats`
- `/api/v1/analytics/tasks-by-status`

**Fix Applied:** Updated `lib/query.ts` to use correct paths:

```typescript
// Before:
const { data } = await api.get('/analytics/stats');

// After:
const { data } = await api.get('/api/v1/analytics/stats');
```

Fixed all three analytics hooks:
- `useDashboardStats`: `/analytics/stats` → `/api/v1/analytics/stats`
- `useTasksByStatus`: `/analytics/tasks-by-status` → `/api/v1/analytics/tasks-by-status`
- `useProjectProfitability`: `/analytics/profitability` → `/api/v1/analytics/profitability`

## Outcome

- ✅ Impact: Dashboard should now load successfully. Analytics API calls will hit correct endpoints and return data. Turbopack will hot-reload changes.
- 🧪 Tests: User needs to refresh browser at /dashboard to verify fix. Should see stat cards (Active Projects, Tasks Completed, Team Utilization, Revenue) and charts.
- 📁 Files: 1 file modified (lib/query.ts - 3 API paths fixed)
- 🔁 Next prompts: Refresh /dashboard, verify stats display correctly, test drag-and-drop on /tasks page
- 🧠 Reflection: API path inconsistency between base URL and endpoint paths. The analytics endpoints were registered at `/api/v1/analytics/*` on backend but frontend was calling `/analytics/*`. Combined with missing `/api/v1` prefix in baseURL, this caused API 404s that broke dashboard rendering.

## Evaluation notes (flywheel)

- Failure modes observed: API path mismatch between frontend and backend
- Graders run and results (PASS/FAIL): Fix applied, awaiting user verification on frontend
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): User refreshes dashboard, verifies stats cards and charts load correctly, then tests task creation and drag-and-drop functionality
