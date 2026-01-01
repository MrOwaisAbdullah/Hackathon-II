---
name: building-nextjs-apps
description: Build Next.js 16 applications with correct patterns and distinctive design. Use when creating pages, layouts, dynamic routes, upgrading from Next.js 15, or implementing proxy.ts. Covers breaking changes (async params/searchParams, Turbopack, cacheComponents) and frontend aesthetics. NOT when building non-React or backend-only applications.
---

# Next.js 16 Applications

Build Next.js 16 applications correctly with distinctive design.

## Required Clarifications

Before generating code, ask:
1.  **Routing**: "Using App Router (default) or Pages Router?" (Assume App Router if unspecified)
2.  **Styling**: "Tailwind CSS + shadcn/ui?" (Assume yes if unspecified)
3.  **Database**: "Which database/ORM?" (e.g., PostgreSQL + Drizzle/Prisma/SQLModel)

## Quick Reference

| Pattern | Reference |
|---------|-----------|
| **Breaking Changes** | [nextjs-16-patterns.md](references/nextjs-16-patterns.md) |
| **Core Patterns** | [nextjs-16-patterns.md](references/nextjs-16-patterns.md) (Layouts, Actions, APIs) |
| **Data Fetching** | [nextjs-16-patterns.md](references/nextjs-16-patterns.md) (Server/Client) |
| **Design & UI** | [frontend-design.md](references/frontend-design.md) (Shadcn, Theming) |
| **Dates & UTC** | [datetime-patterns.md](references/datetime-patterns.md) |

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Next.js Docs | https://nextjs.org/docs | Routing, Rendering, Caching |
| React Docs | https://react.dev | Server Components, Hooks |
| Shadcn/ui | https://ui.shadcn.com | Component references |

## Critical Breaking Changes (Summary)

**1. Async Params**: `params` and `searchParams` are now Promises.
   - **WRONG**: `const { id } = params`
   - **RIGHT**: `const { id } = await params`

**2. Client Components**: Use `use()` hook for promises.
   - **RIGHT**: `const { id } = use(params)`

See [references/nextjs-16-patterns.md](references/nextjs-16-patterns.md) for full examples.

---

## ⚠️ CRITICAL SSR Pitfalls (Read Before Coding!)

**If you're using Zustand with persist middleware, localStorage, or any browser APIs, you WILL encounter these errors:**

- ❌ "Maximum update depth exceeded"
- ❌ "The result of getServerSnapshot should be cached to avoid an infinite loop"
- ❌ "Rendered more hooks than during the previous render"

**Solution**: Use local state with `useState` + `useEffect` pattern. See **[Critical SSR Pitfalls](references/nextjs-16-patterns.md#critical-ssr-pitfalls-)** section for complete patterns.

**Quick Fix Template**:
```typescript
"use client"
import { useState, useEffect } from "react"

export function SSRSafeComponent() {
  const [mounted, setMounted] = useState(false)
  const [value, setValue] = useState(defaultValue)

  useEffect(() => {
    setMounted(true)
    // Access browser APIs here only
    const stored = localStorage.getItem('key')
    if (stored) setValue(JSON.parse(stored))
  }, [])

  if (!mounted) return <Placeholder />  // SSR-safe
  return <RealComponent value={value} />
}
```

---

## Next.js DevTools MCP

Use the next-devtools-mcp server for runtime diagnostics and development automation.

### Setup

```bash
claude mcp add next-devtools npx next-devtools-mcp @latest
```

### Key Tools

- `upgrade_nextjs_16`: Automated upgrade with codemods
- `enable_cache_components`: Configure Cache Components for Next.js 16
- `nextjs_docs`: Search official documentation

### Next.js 16 MCP Endpoint

Next.js 16+ exposes a built-in MCP endpoint at `http://localhost:3000/_next/mcp`.

---

## Verification

Run: `python3 scripts/verify.py`

Expected: `✓ building-nextjs-apps skill ready`

## Related Skills

- **frontend-designer** - Use for animation choreography and "Black Shirt" design aesthetic.
- **gemini-frontend-assistant** - Use for generating components from screenshots or descriptions.
- **theme-factory** - Use for generating professional color palettes and themes.
- **styling-with-shadcn** - UI components for Next.js apps
- **fetching-library-docs** - Latest Next.js docs: `--library-id /vercel/next.js --topic routing`
- **configuring-better-auth** - OAuth/SSO for Next.js apps
