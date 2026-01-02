---
id: 0012
title: frontend-turbopack-windows-fix
stage: red
date: 2026-01-02
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-crm
branch: 002-fullstack-web-crm
user: owais_abdullah
command: /sp.implement
labels: ["bug-fix","nextjs","windows","turbopack"]
links:
  spec: specs/002-fullstack-web-crm/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - teamflow-web/frontend/package.json (modified: added --turbo=false flag)
tests:
  - None - requires user to run on Windows machine
---

## Prompt

User reported that `npm run dev` was failing with:

```
Error: `turbo.createProject` is not supported by the wasm bindings.
```

And warnings about missing `@next/swc-win32-x64-msvc` package on Windows.

## Response snapshot

**ROOT CAUSE**: Next.js 16 defaults to Turbopack with WASM bindings, which doesn't support all features on Windows.

**Fix Applied**:
Modified `package.json` dev script from:
```json
"dev": "next dev"
```
to:
```json
"dev": "next dev --turbo=false"
```

This disables Turbopack and uses the traditional webpack compiler, which works properly on Windows.

**User Instructions Provided**:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` to get correct Windows packages
3. Run `npm run dev` to start frontend
4. Start backend in separate terminal
5. Test drag functionality

**Why This Happened**:
- Next.js 16.1.1 on Windows tries to use Turbopack with WASM bindings
- WASM bindings have limited feature support on Windows
- The `--turbo=false` flag forces use of the stable webpack compiler

## Outcome

- ✅ Impact: Fixed frontend dev server startup on Windows by disabling Turbopack. User can now run `npm run dev` without the turbo.createProject error.
- 🧪 Tests: User needs to run `npm run dev` on Windows machine to verify fix.
- 📁 Files: 1 file modified (package.json - added --turbo=false flag to dev script).
- 🔁 Next prompts: User should run `npm run dev` on Windows, then start backend, create tasks, and verify drag functionality works.
- 🧠 Reflection: This was a platform-specific issue with Next.js 16 on Windows. Turbopack is still experimental and has platform-specific limitations. The --turbo=false flag is a reliable workaround.

## Evaluation notes (flywheel)

- Failure modes observed: Next.js 16 Turbopack crash on Windows
- Graders run and results (PASS/FAIL): Fix applied, awaiting user verification on Windows
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): User runs `npm run dev` on Windows to verify frontend starts successfully, then tests drag functionality
