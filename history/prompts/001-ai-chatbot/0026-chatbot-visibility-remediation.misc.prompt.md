---
id: 0026
title: Chatbot Visibility Dashboard-Only Remediation
stage: misc
date: 2026-01-11
surface: agent
model: claude-opus-4-5
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: (unknown)
command: /sp.analyze
labels: ["specification-analysis","remediation","visibility-control","chatbot"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-ai-chatbot/spec.md
 - specs/001-ai-chatbot/tasks.md
 - teamflow-web/frontend/src/components/chat/ChatWidgetWrapper.tsx
tests:
 - Specification analysis completed (no tests run for analysis task)
 - Route visibility verification needed
---

## Prompt

/sp.analyze the chatbot should only visible on /dasboard pages, not on other pages like landing page, contact page, about page, privacy or any other, also not visible on the /chat page

## Response snapshot

### Analysis Completed

Executed specification analysis for 001-ai-chatbot feature with focus on chatbot visibility requirements.

### Findings Summary (5 issues):

**U1 (CRITICAL): Missing FR-030 in spec.md**
- Spec had NO functional requirement defining WHERE the chatbot should appear
- Current global rendering in layout.tsx violated user's dashboard-only requirement
- Added FR-030: "System MUST restrict the floating chat widget visibility to authenticated dashboard routes only"

**I1 (HIGH): ChatWidgetWrapper.tsx contradicts user intent**
- Current code excluded only `/chat` page, but user wanted dashboard-exclusive visibility
- Landing page, login, signup all showed floating widget inappropriately
- Fixed with DASHBOARD_ROUTES whitelist approach

**G1 (HIGH): Task coverage gap**
- No task specified route-based visibility rules
- Added T102 to tasks.md with complete implementation instructions

**A1 (MEDIUM): Ambiguity in FR-028/FR-029**
- Clarified relationship between floating widget and fullscreen page exclusivity

**T1 (LOW): Terminology drift**
- Documented ChatWidget vs fullscreen chat vs AI Assistant terminology

### Remediation Applied:

1. **spec.md** - Added FR-030 after FR-029 (line 113)
2. **tasks.md** - Added T102 after T100a (line 211), marked complete
3. **ChatWidgetWrapper.tsx** - Replaced with whitelist implementation

### Routes Updated:

**DASHBOARD_ROUTES (widget SHOWN):**
- /dashboard, /tasks, /projects, /time-entries, /team, /settings, /archive
- Plus sub-routes (e.g., /projects/123)

**Excluded routes (widget HIDDEN):**
- Public: /, /contact, /about, /privacy
- Auth: /login, /signup
- Fullscreen: /chat

## Outcome

- ✅ Impact: Fixed chatbot visibility to match user requirement (dashboard-only)
- 🧪 Tests: Specification analysis + implementation complete; route verification needed
- 📁 Files: 3 files modified (spec.md, tasks.md, ChatWidgetWrapper.tsx)
- 🔁 Next prompts: Run frontend dev server to verify route visibility
- 🧠 Reflection: Specification analysis identified gap between implementation and intent; remediation completed successfully

## Evaluation notes (flywheel)

- Failure modes observed: None - analysis and remediation completed successfully
- Graders run and results (PASS/FAIL): N/A - analysis task
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify route visibility in browser; add E2E test for T102

## Commit

Commit: e62ff4c - "fix: Restrict chatbot visibility to dashboard routes only"
