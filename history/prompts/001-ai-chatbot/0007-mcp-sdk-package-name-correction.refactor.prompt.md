---
id: 0007
title: MCP SDK Package Name Correction
stage: refactor
date: 2025-01-07
surface: agent
model: glm-4.7
feature: 001-ai-chatbot
branch: 001-ai-chatbot
user: MrOwaisAbdullah
command: /sp.analyze
labels: ["mcp","sdk","package-correction","dependency","critical"]
links:
  spec: specs/001-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - teamflow-web/backend/pyproject.toml (identified - incorrect package `fastmcp`)
  - specs/001-ai-chatbot/spec.md (verified - correct references to Official MCP SDK)
  - specs/001-ai-chatbot/plan.md (verified - correct architecture)
  - specs/001-ai-chatbot/tasks.md (verified - FastMCP module references correct)
tests:
  - Package name verification: PASSED (official `mcp` package confirmed)
  - Documentation verification: PASSED (https://modelcontextprotocol.github.io/python-sdk/ confirms `pip install mcp`)
  - Import pattern verification: PASSED (`from mcp.server.fastmcp import FastMCP` is correct)
  - Artifact consistency check: FAILED (pyproject.toml has wrong package `fastmcp`)
---

## Prompt

/sp.analyze we have to use official python mcp sdk https://modelcontextprotocol.github.io/python-sdk/, not fastmcp, we know that official mcp sdk is also use fastmcp

## Context

User identified a critical inconsistency: The implementation specifies `fastmcp` as a dependency, but the correct package is the official Python MCP SDK (`mcp`). The user notes that FastMCP is part of the official SDK (via `mcp.server.fastmcp`).

## Your Task

Perform a focused cross-artifact analysis to verify:
1. The correct package name for the official MCP Python SDK
2. All references to MCP SDK/FastMCP across artifacts
3. Any inconsistencies between specification and implementation

## Expected Output

Generate a structured analysis report identifying:
- Whether `fastmcp` or `mcp` is the correct PyPI package
- All locations where this package is referenced
- The severity of any inconsistencies found
- Remediation steps if needed

## Constraint

**STRICTLY READ-ONLY**: Do not modify files. Output analysis report only.

## Response snapshot

Successfully identified and analyzed the MCP SDK package name inconsistency.

**Critical Finding**: Wrong package specified in pyproject.toml

**Correct Package**: `mcp` (Official MCP Python SDK from https://pypi.org/project/mcp/)
**Incorrect Package**: `fastmcp` (Third-party package by jlowin)

**Key Findings**:
1. Official documentation confirms: `pip install mcp`
2. Import pattern: `from mcp.server.fastmcp import FastMCP` (FastMCP is a module within official SDK)
3. pyproject.toml line 28 has: `fastmcp>=0.1.0` ❌ WRONG
4. Should be: `mcp>=0.1.0` ✅ CORRECT

**Verification from Official Docs** (https://modelcontextprotocol.github.io/python-sdk/):
- "The Python SDK is available on PyPI as `mcp`"
- Installation: `pip install mcp`
- Usage: `from mcp.server.fastmcp import FastMCP`

**Artifacts Checked**:
- ✅ spec.md: Correctly references "Official MCP SDK"
- ✅ plan.md: Correctly references "Official MCP SDK (FastMCP)"
- ✅ tasks.md: Correctly references FastMCP module usage
- ❌ pyproject.toml: Incorrectly specifies `fastmcp` package

**Clarification on FastMCP**:
- FastMCP is NOT a separate package
- FastMCP is the server framework **within** the official `mcp` package
- Module path: `mcp.server.fastmcp`
- Therefore, references to "FastMCP" in plan/tasks are correct
- Only the package dependency needs fixing

**Severity**: CRITICAL - Wrong dependency would cause:
- Incompatible API surface
- Missing standard MCP transports (stdio, SSE, HTTP)
- Security/compatibility issues
- Architecture violation

**Required Fix**:
```python
# In teamflow-web/backend/pyproject.toml, line 28:
- "fastmcp>=0.1.0"  # WRONG
+ "mcp>=0.1.0"      # CORRECT - Official MCP Python SDK
```

**Status**: ⚠️ CRITICAL ISSUE FOUND - Remediation required before proceeding with implementation.

## Outcome

- ✅ Impact: Identified critical package name inconsistency that would cause implementation failure. Confirmed correct package is `mcp` (official MCP Python SDK), not `fastmcp` (third-party). Clarified that FastMCP is a module within the official SDK (`mcp.server.fastmcp`), so references to "FastMCP" in plan/tasks are correct.
- 🧪 Tests: Package name verification from official docs (PASSED - `pip install mcp`); import pattern verification (PASSED - `from mcp.server.fastmcp`); artifact consistency scan (FAILED - pyproject.toml has wrong package)
- 📁 Files: Identified pyproject.toml:28 as requiring fix; verified spec.md, plan.md, tasks.md have correct references; confirmed official documentation at https://modelcontextprotocol.github.io/python-sdk/
- 🔁 Next prompts: Fix pyproject.toml then proceed with `/sp.implement` - change line 28 from `fastmcp>=0.1.0` to `mcp>=0.1.0`, then run `uv sync` to install correct package
- 🧠 Reflection: User correctly identified a critical error that would have caused implementation failure. The confusion stems from FastMCP being both (1) a module name within the official SDK and (2) a third-party package name. The official MCP Python SDK is the package `mcp` on PyPI, which includes FastMCP as `mcp.server.fastmcp`. This is a classic case where module name ≠ package name. All references to "FastMCP" in the plan/tasks are technically correct since they refer to the module within the SDK. Only the pyproject.toml dependency needs correction from `fastmcp` to `mcp`.

## Evaluation notes (flywheel)

- Failure modes observed: Package name confusion (fastmcp third-party vs mcp official)
- Graders run and results (PASS/FAIL): PASSED official documentation verification; PASSED import pattern verification; FAILED pyproject.toml dependency check
- Prompt variant (if applicable): N/A - user-provided correction with specific issue
- Next experiment (smallest change to try): Apply fix to pyproject.toml line 28, verify `uv sync` installs correct package
