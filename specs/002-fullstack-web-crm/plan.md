# Implementation Plan: TeamFlow Web (Phase 2 - Full-Stack Agency CRM)

**Branch**: `002-fullstack-web-crm` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-web-crm/spec.md`

**Note**: This plan has evolved through multiple phases. Phase 13 focuses on mobile responsiveness fixes based on user-reported issues.

## Summary

TeamFlow Phase 2 transforms the CLI-based task management tool into a **full-stack web application** designed specifically for creative agencies. **Phase 13** addresses critical mobile responsiveness issues: excessive padding, header element collapsing, card content overflow, and mobile sidebar dark theme inconsistency.

### Phase 13 Specific Summary

User-reported mobile issues requiring remediation:
- **Excessive padding** on mobile devices (should use p-2/p-3 instead of p-6/p-8)
- **Header elements** collapsing/overlapping (need flex-wrap and proper gap spacing)
- **Card content** overflowing horizontally (need w-full, line-clamp truncation)
- **Mobile sidebar** not dark in light mode (missing `.sidebar-dark` class)
- **Touch targets** potentially below 44x44px minimum

---

## Technical Context

**Language/Version**: TypeScript 5.x, Python 3.13+
**Primary Dependencies**:
  - Frontend: Next.js 16, React Query, Motion.dev, @dnd-kit, Tailwind CSS
  - Backend: FastAPI, SQLModel, Pydantic, Better Auth
**Storage**: Neon PostgreSQL (serverless)
**Testing**:
  - Backend: pytest, pytest-cov, httpx
  - Frontend: Playwright (E2E), Vitest (unit)
**Target Platform**: Web (desktop 1920px+, tablet 768-1023px, mobile 320px+)
**Project Type**: Full-stack web application (frontend/backend separation)
**Performance Goals**:
  - LCP < 1.5s (mobile)
  - Animations 60fps
  - API p95 < 200ms
**Constraints**:
  - Mobile viewport minimum: 320px width
  - Touch targets: 44x44px minimum (WCAG AA)
  - Padding scale: p-2/p-3 (mobile) vs p-6/p-8 (desktop)
**Scale/Scope**:
  - Agencies: 2-50 team members
  - Tasks: Up to 100 per column with smooth animations
  - Viewports: 320px (mobile) to 4k (desktop)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase 13 Compliance Review

- [X] **Existing agents/skills consulted first**
  - Reviewed `frontend-designer` skill for mobile-first responsive patterns
  - Reviewed `building-nextjs-apps` for Next.js 16 SSR-safe component patterns
  - No specialized mobile-responsive agent exists → custom implementation

- [X] **SOLID principles followed**
  - SRP: Each component handles its own responsive classes (no global wrapper)
  - OCP: Extending existing components with mobile variants (not modifying desktop behavior)
  - DIP: Tailwind breakpoint system provides abstraction over media queries

- [X] **DRY applied**
  - Responsive utilities defined in Tailwind config (sm:, md:, lg: breakpoints)
  - Shared mobile padding scale (p-2/p-3) applied consistently

- [X] **Tests written first (TDD)**
  - E2E tests for mobile viewports (375px, 414px) included in Phase 13 tasks
  - Tests verify padding, header layout, overflow prevention, sidebar theme

- [X] **Type safety enforced**
  - TypeScript strict mode enabled
  - Tailwind classes validated at build time

- [X] **Security standards met**
  - No security changes in Phase 13 (UI-only fixes)

- [X] **Performance targets defined**
  - LCP < 1.5s on mobile (reduced padding improves perceived performance)
  - 60fps animations maintained

- [X] **MCP tools considered**
  - `chrome-devtools`: Can test mobile viewports
  - `web-search`: For mobile-first best practices research

- [N/A] **Skill refinement documented**
  - No new errors encountered (applying established responsive patterns)

**GATE STATUS**: ✅ PASSED - Phase 13 proceeds with mobile responsiveness fixes

---

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-crm/
├── plan.md              # This file (Phase 13 updates)
├── research.md          # Phase 0 research findings
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup instructions
├── contracts/           # API contracts
├── tasks.md             # All phase tasks (T001-T693)
└── AGENT_CONTEXT.md     # Agent runtime context
```

### Source Code (repository root)

```text
# Web application structure (active)
backend/
├── app/
│   ├── models/          # SQLModel entities
│   ├── services/        # Business logic
│   ├── api/             # FastAPI routers
│   └── core/            # Config, security
└── tests/

frontend/
├── src/
│   ├── app/             # Next.js 16 app router
│   │   ├── (main)/      # Authenticated pages
│   │   ├── (auth)/      # Public pages
│   │   └── api/         # API proxy routes
│   ├── components/      # React components
│   │   ├── dashboard/   # Dashboard components
│   │   ├── task/        # Task components
│   │   ├── project/     # Project components
│   │   ├── team/        # Team components
│   │   └── ui/          # Shadcn base components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities, API client
│   └── types/           # TypeScript types
└── tests/
    └── e2e/             # Playwright E2E tests
```

**Structure Decision**: Web application with frontend/backend separation. Backend is Python FastAPI with SQLModel ORM. Frontend is Next.js 16 App Router with TypeScript. Responsive design uses Tailwind CSS breakpoint system (sm:, md:, lg:, xl:).

---

## Phase 13: Mobile Responsiveness Implementation Strategy

### Problem Statement

User reported mobile issues on 320px-768px viewports:
1. **Excessive padding** wastes screen real estate
2. **Header elements** collapse and overlap each other
3. **Card content** overflows horizontally causing scroll
4. **Mobile sidebar** not dark-themed (inconsistent with desktop)

### Solution Approach

#### 1. Mobile Padding Optimization (FR-080)

**Tailwind Responsive Classes Pattern**:
```tsx
// Desktop: p-6 (1.5rem = 24px)
// Mobile: p-2 (0.5rem = 8px) or p-3 (0.75rem = 12px)
<div className="p-3 md:p-6">
  {/* Content */}
</div>
```

**Affected Components**:
- `dashboard/page.tsx`: Main container padding
- `StatCard.tsx`: Card padding
- `ProjectCard.tsx`: Card padding
- `UserCard.tsx`: Card padding
- `TaskDrawer.tsx`: Sheet padding
- `UpcomingDeadlines.tsx`: Card padding

#### 2. Header Layout Fixes (FR-081)

**Flex-Wrap Pattern**:
```tsx
// Prevents collapse, stacks on mobile
<header className="flex flex-wrap items-center gap-2">
  <h1 className="text-lg md:text-xl">Page Title</h1>
  <Button className="ml-auto shrink-0">Action</Button>
</header>
```

**Affected Components**:
- `dashboard/page.tsx`: Stats header
- `tasks/page.tsx`: Board header
- `projects/page.tsx`: Project grid header
- `team/page.tsx`: Team list header

#### 3. Card Overflow Prevention (FR-082)

**Width Constraints + Text Truncation**:
```tsx
// Prevents horizontal overflow
<div className="w-full min-w-0">
  <h3 className="truncate">Long title...</h3>
  <p className="line-clamp-2">Long description...</p>
</div>
```

**Affected Components**:
- `TaskCard.tsx`: Title truncate (line-clamp-2 on mobile)
- `ProjectCard.tsx`: Description truncate (line-clamp-2 on mobile)
- `UpcomingDeadlines.tsx`: Task title truncation
- Badge components: max-width constraints

#### 4. Mobile Sidebar Dark Theme (FR-083)

**Sidebar Dark Class Pattern**:
```tsx
// MobileNav.tsx
<Sheet className="sidebar-dark">
  {/* Sidebar content always dark */}
</Sheet>
```

**CSS Rules** (globals.css):
```css
.sidebar-dark {
  --sidebar-bg: 240 10% 3.9%; /* Zinc 950 */
  --sidebar-fg: 240 5% 96%;   /* Zinc 50 */
}
```

**Verification**:
- Check `.sidebar-dark` class applied to MobileNav Sheet
- Test in both light and dark themes
- Ensure consistency with desktop Sidebar

#### 5. Touch Target Verification (FR-084)

**Minimum Touch Target Pattern**:
```tsx
// Ensure 44x44px minimum
<Button className="min-h-11 min-w-11">
  <Icon size={20} />
</Button>
```

**Affected Elements**:
- TaskCard menu button (three-dot)
- Priority selector buttons in TaskDrawer
- Form inputs and buttons
- Avatar clickable areas

---

## Phase 13 Task Breakdown

### T600-T605: Mobile Padding Optimization

| Task | Component | Change |
|------|-----------|--------|
| T600 | Audit | Review all components with `p-6`+ on mobile |
| T601 | dashboard/page.tsx | `p-2 md:p-6` main container |
| T602 | StatCard.tsx | `p-3 md:p-6` card padding |
| T603 | ProjectCard.tsx | `p-3 md:p-6` card padding |
| T604 | UserCard.tsx | `p-3 md:p-6` card padding |
| T605 | TaskDrawer.tsx | `p-3 md:p-6` sheet content |

### T610-T615: Header Layout Fixes

| Task | Component | Change |
|------|-----------|--------|
| T610 | Audit | Review all page headers for collapse issues |
| T611 | dashboard/page.tsx | Add `flex-wrap gap-2` to header |
| T612 | tasks/page.tsx | Add `flex-wrap gap-2` to board header |
| T613 | projects/page.tsx | Add `flex-wrap gap-2` to project header |
| T614 | team/page.tsx | Add `flex-wrap gap-2` to team header |
| T615 | Global | Ensure buttons use `min-width` and `shrink-0` |

### T620-T625: Card Overflow Prevention

| Task | Component | Change |
|------|-----------|--------|
| T620 | Audit | Review all cards for overflow issues |
| T621 | Global | Add `w-full` to all card content containers |
| T622 | TaskCard.tsx | Add `line-clamp-2` to title on mobile |
| T623 | ProjectCard.tsx | Add `line-clamp-2` to description |
| T624 | Badges | Add `max-w-full truncate` to badges |
| T625 | UpcomingDeadlines.tsx | Ensure item truncation |

### T630-T633: Mobile Sidebar Dark Theme

| Task | Component | Change |
|------|-----------|--------|
| T630 | MobileNav.tsx | Verify `.sidebar-dark` class on Sheet |
| T631 | MobileNav.tsx | Add `.sidebar-dark` if missing |
| T632 | globals.css | Verify `.sidebar-dark` CSS rules |
| T633 | Manual test | Test in light/dark themes |

### T640-T643: Touch Target Verification

| Task | Component | Change |
|------|-----------|--------|
| T640 | Audit | Measure all interactive elements |
| T641 | TaskCard.tsx | Menu button `min-h-11 min-w-11` |
| T642 | TaskDrawer.tsx | Priority buttons `min-h-11` |
| T643 | Forms | All inputs `min-h-11` on mobile |

### T650-T653: E2E Testing for Mobile

| Task | Test Case | Viewport |
|------|-----------|----------|
| T650 | Dashboard layout | 375px |
| T651 | Header layout | 375px |
| T652 | Card overflow | 375px |
| T653 | Sidebar theme | 375px |

---

## Testing Strategy

### E2E Test Structure (mobile-phase13.spec.ts)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Mobile Responsiveness (Phase 13)', () => {
  test.beforeEach(async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
  });

  test('dashboard uses reduced padding on mobile', async ({ page }) => {
    const container = page.locator('.main-content');
    const padding = await container.evaluate(el => {
      return window.getComputedStyle(el).paddingTop;
    });
    expect(parseInt(padding)).toBeLessThan(16); // < p-4
  });

  test('header elements do not collapse', async ({ page }) => {
    const header = page.locator('header');
    const buttons = header.locator('button');
    await expect(buttons).toHaveCount(2);
    // Verify no overlap by checking positions
    const box1 = await buttons.nth(0).boundingBox();
    const box2 = await buttons.nth(1).boundingBox();
    expect(box1?.y).not.toBe(box2?.y); // Not on same Y if stacked
  });

  test('card content does not overflow', async ({ page }) => {
    const cards = page.locator('.card-float');
    const cardCount = await cards.count();
    for (let i = 0; i < cardCount; i++) {
      const card = cards.nth(i);
      const scrollWidth = await card.evaluate(el => el.scrollWidth);
      const clientWidth = await card.evaluate(el => el.clientWidth);
      expect(scrollWidth).toBe(clientWidth); // No overflow
    }
  });

  test('mobile sidebar uses dark theme', async ({ page }) => {
    // Toggle mobile menu
    await page.click('[data-testid="mobile-menu-toggle"]');
    const sidebar = page.locator('[role="dialog"]');
    const bgColor = await sidebar.evaluate(el => {
      return window.getComputedStyle(el).backgroundColor;
    });
    // Should be dark (not white)
    expect(bgColor).not.toBe('rgb(255, 255, 255)');
  });
});
```

---

## Rollback Strategy

If Phase 13 introduces regressions:
1. Revert specific component changes (not entire phase)
2. Use git bisect to identify problematic commit
3. Restore previous responsive classes
4. Re-run E2E tests to verify desktop functionality

---

## Success Criteria

Phase 13 is complete when:
- [ ] All mobile padding uses p-2/p-3 instead of p-6/p-8
- [ ] Headers display properly with flex-wrap on 375px viewport
- [ ] No horizontal scroll on any page (overflow-x: hidden)
- [ ] Mobile sidebar is dark in both light and dark themes
- [ ] All touch targets are >= 44x44px
- [ ] All E2E tests pass for 375px viewport
- [ ] Desktop layout unchanged (verified on 1920px)

---

## Complexity Tracking

> **No violations for Phase 13** - Simple responsive utility class updates following established Tailwind patterns.

---

## Dependencies

### Phase 13 Dependencies

- **Requires**: Phase 10 (Mobile Responsiveness baseline with MobileNav)
- **Blocks**: None (can be rolled back independently)
- **Parallel Tasks**: T600-T605, T610-T615, T620-T625, T640-T643 can all run in parallel

---

## Related ADRs

None for Phase 13 (responsive fixes, no architectural decisions).

---

**Phase 13 Plan Complete**: Ready for `/sp.implement` execution
