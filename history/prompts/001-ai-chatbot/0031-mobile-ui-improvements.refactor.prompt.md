---
id: 0031
title: Mobile UI Improvements
stage: refactor
date: 2026-01-13
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: Owais Abdullah
command: Fix mobile UI issues with sidebar sheet and chat widget
labels: [frontend, mobile, ui, chat-widget, sidebar]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - teamflow-web/frontend/src/components/ui/sheet.tsx
  - teamflow-web/frontend/src/components/chat/ChatWidget.tsx
tests:
  - TypeScript check passed (no errors in modified files)
---

## Prompt

the sidebar sheet in mobile is always dark, the heading of menu, the border colors, etc. all has to be always dark, in mobile, the chatwidget is toucing the sides of page, and the trigger button, add osme spacing, also the icon on the chatwidget should be conditional based on the chat widget is open or closed, also if the widget is full screen hide the toggle button, also if a modal or drawer is opened make sure the chat toggle dont cover them, it should be behind them

## Response snapshot

I've fixed all the mobile UI issues:

**1. Mobile sidebar sheet - Always dark theme (sheet.tsx):**
- Changed sheet background from `bg-card` to `bg-zinc-900` (always dark)
- Changed border from `border-border` to `border-zinc-700` (always dark)
- Changed SheetHeader background to `bg-zinc-900` with `border-zinc-700`
- Changed title color to `text-zinc-50` (always light)
- Changed close button hover to `hover:bg-zinc-800` with `text-zinc-400` → `hover:text-zinc-50`

**2. Chat widget spacing on mobile (ChatWidget.tsx):**
- Changed mobile positioning from `left-2 right-2` to `left-4 right-4` (16px each side → 32px total)
- Updated width calculation from `calc(100vw - 16px)` to `calc(100vw - 32px)`

**3. Toggle button icon conditional (ChatWidget.tsx:201-205):**
- Shows `X` icon when chat is open
- Shows `MessageCircle` icon when chat is closed
- Updated aria-label to reflect current state

**4. Hide toggle in fullscreen (ChatWidget.tsx:188):**
- Added `!isFullscreen` condition to toggle button rendering
- Toggle button now hidden when widget is fullscreen

**5. Z-index management for modals/drawers (ChatWidget.tsx):**
- Toggle button: `z-40` (stays behind modals at z-50)
- Chat widget: `z-50` (same as modals, but modals render later so they appear on top)
- Error banner: `z-40` for consistency with toggle

## Outcome

- ✅ Impact: Fixed mobile sidebar sheet to always use dark theme, improved chat widget spacing and behavior on mobile
- 🧪 Tests: TypeScript check passed
- 📁 Files: 2 files modified (sheet.tsx, ChatWidget.tsx)
- 🔁 Next prompts: Deploy changes to verify fixes in production
- 🧠 Reflection: Z-index layering is important - modals (z-50) should always be above chat toggle (z-40), while chat widget (z-50) appears below modals that render later in DOM

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider testing on actual mobile devices to verify spacing and z-index behavior
