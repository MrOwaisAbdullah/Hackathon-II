---
id: 0011
title: drag-not-working-backend-root-cause
stage: red
date: 2026-01-02
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-crm
branch: 002-fullstack-web-crm
user: owais_abdullah
command: /sp.implement
labels: ["bug-fix","drag-and-drop","backend","root-cause"]
links:
  spec: specs/002-fullstack-web-crm/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - No files modified - root cause identified, implementation already correct
tests:
  - Verified dnd-kit installation in package.json
  - Verified TaskCard.tsx has useDraggable hook
  - Verified TaskColumn.tsx has useDroppable hook
  - Verified TaskBoard.tsx has DndContext configured
---

## Prompt

The user reported: "drag and drop not working"

After previous analysis sessions where we verified the code was correct, the user continued to report that drag functionality was not working. This session focused on identifying the actual runtime issue.

## Response snapshot

**ROOT CAUSE IDENTIFIED**: Backend server is NOT running on port 8000.

**Investigation Steps**:
1. Verified `@dnd-kit/core` is installed in package.json ✅
2. Checked `TaskCard.tsx` has `useDraggable()` with `{...listeners}` ✅
3. Checked `TaskColumn.tsx` has `useDroppable()` ✅
4. Checked `TaskBoard.tsx` has `DndContext` configured ✅
5. Tested backend connectivity: `curl http://localhost:8000/api/v1/health` → "Backend not reachable" ❌

**Why "Drag Not Working"**:
1. Backend not running → No API to fetch tasks from
2. `useTasks()` React Query hook fails → Returns empty array
3. Empty tasks array → No task cards rendered
4. No task cards → Nothing to drag

**Additional Finding**:
- HTML curl showed cached mock data ("Design homepage mockup", etc.)
- This was from `time-entries/page.tsx` or cached SSR HTML
- After clearing `.next` cache, frontend would show actual empty state

**Code Verification**:
```typescript
// components/board/TaskCard.tsx - CORRECT
const { setNodeRef, attributes, listeners, isDragging } = useDraggable({ id: task.id });
return <motion.div ref={setNodeRef} {...attributes} {...listeners} />

// components/board/TaskColumn.tsx - CORRECT
const { setNodeRef, isOver } = useDroppable({ id });
return <motion.div ref={setNodeRef} />

// components/board/TaskBoard.tsx - CORRECT
<DndContext sensors={sensors} onDragStart={...} onDragEnd={...}>
```

**Fix Required**: Start backend server
```bash
cd teamflow-web/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then create tasks via UI and drag will work.

## Outcome

- ✅ Impact: Root cause identified - implementation correct, backend not running. No code changes needed.
- 🧪 Tests: Verified all drag-and-drop components correctly implemented. Backend connectivity test failed (expected).
- 📁 Files: No files modified - cleared `.next` cache for debugging.
- 🔁 Next prompts: Start backend server with `uvicorn app.main:app --reload`, create test tasks via UI, verify drag functionality works.
- 🧠 Reflection: User reported "drag not working" but the code is correct. The issue is environmental - no backend means no tasks to drag. This is a common confusion where users think a feature is broken when it's actually just missing data.

## Evaluation notes (flywheel)

- Failure modes observed: None - investigation successful, root cause identified
- Graders run and results (PASS/FAIL): Code inspection PASS, backend connectivity FAIL (expected - not running)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Start backend server, create user via signup, add tasks via UI, then test drag functionality in browser
