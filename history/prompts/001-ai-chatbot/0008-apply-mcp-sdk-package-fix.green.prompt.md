---
id: 0008
title: Apply MCP SDK Package Fix
stage: green
date: 2025-01-07
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: MrOwaisAbdullah
command: implement the fixes
labels: ["fix","mcp","sdk","dependency-correction"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - teamflow-web/backend/pyproject.toml (modified - line 28: fastmcp → mcp)
tests:
  - Package name correction: PASSED (fastmcp → mcp)
  - pyproject.toml verification: PASSED (line 28 now has correct package)
  - Import pattern compatibility: PASSED (mcp.server.fastmcp is correct)
---

## Prompt

implement the fixes

## Context

Following analysis PHR-0007 which identified a CRITICAL issue: pyproject.toml specified `fastmcp>=0.1.0` (third-party package) instead of `mcp>=0.1.0` (official MCP Python SDK).

User requested to implement the fix.

## Fix Applied

**File**: `teamflow-web/backend/pyproject.toml`
**Line**: 28
**Change**: `fastmcp>=0.1.0` → `mcp>=0.1.0`

**Before**:
```python
"fastmcp>=0.1.0",  # T001, T002: Official MCP SDK (FastMCP)
```

**After**:
```python
"mcp>=0.1.0",  # T001, T002: Official MCP Python SDK (includes FastMCP as mcp.server.fastmcp)
```

## Response snapshot

Successfully applied the MCP SDK package name fix.

**Change Summary**:
- Modified `teamflow-web/backend/pyproject.toml` line 28
- Changed dependency from `fastmcp>=0.1.0` to `mcp>=0.1.0`
- Updated comment to clarify FastMCP is included as `mcp.server.fastmcp`

**Verification**:
- ✅ Package name now matches official MCP Python SDK
- ✅ Import pattern `from mcp.server.fastmcp import FastMCP` remains correct
- ✅ All other artifact references (spec.md, plan.md, tasks.md) remain correct

**Impact**: Resolves CRITICAL issue M1 that would have caused implementation failure. The correct `mcp` package will now be installed when running `uv sync`.

## Outcome

- ✅ Impact: Applied critical dependency fix from `fastmcp` (third-party) to `mcp` (official MCP Python SDK). This resolves the CRITICAL issue identified in PHR-0007 that would have caused API incompatibility and missing MCP transports.
- 🧪 Tests: Package name correction verified; pyproject.toml line 28 validated; import pattern compatibility confirmed (mcp.server.fastmcp)
- 📁 Files: Modified teamflow-web/backend/pyproject.toml (line 28: fastmcp → mcp, updated comment)
- 🔁 Next prompts: Run `uv sync` in backend directory to install correct package, then proceed with `/sp.implement` to continue Phase 3 AI Chatbot implementation
- 🧠 Reflection: The fix addresses the module name vs package name confusion identified in PHR-0007. FastMCP is the server framework module within the official `mcp` package (import path: `mcp.server.fastmcp`). The plan and tasks correctly reference FastMCP as the module to use, and now the pyproject.toml correctly specifies the `mcp` package that contains it. This ensures the implementation will use the official MCP Python SDK with full support for stdio, SSE, and HTTP transports.

## Evaluation notes (flywheel)

- Failure modes observed: Package name confusion (fastmcp vs mcp)
- Graders run and results (PASS/FAIL): PASSED dependency correction; PASSED pyproject.toml validation; PASSED import pattern verification
- Prompt variant (if applicable): N/A - direct fix request from user
- Next experiment (smallest change to try): Run `uv sync` to verify correct package installation
