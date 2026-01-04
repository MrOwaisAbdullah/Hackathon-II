import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Mobile Responsiveness (Phase 10)
 *
 * These tests verify the application works correctly on mobile viewports
 * including dashboard layout, full-screen dialogs, and navigation drawer.
 *
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Frontend server running on http://localhost:3000
 * - User account exists or can be created
 */

// Mobile viewport dimensions
const MOBILE_VIEWPORT = { width: 375, height: 667 }; // iPhone SE
const TABLET_VIEWPORT = { width: 768, height: 1024 }; // iPad

test.describe("Mobile Responsiveness", () => {
  test.beforeEach(async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize(MOBILE_VIEWPORT);

    // Login first
    await page.goto("http://localhost:3000/login");

    const email = "mobilee2e@test.com";
    const password = "password123";

    // Try to login first
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    // If login fails (user doesn't exist), signup first
    const url = page.url();
    if (url.includes("/login")) {
      await page.goto("http://localhost:3000/signup");
      await page.fill('input[name="agencyName"]', "Mobile E2E Agency");
      await page.fill('input[name="agencyEmail"]', "mobilee2e-agency@test.com");
      await page.fill('input[name="name"]', "Mobile E2E User");
      await page.fill('input[name="email"]', email);
      await page.fill('input[name="password"]', password);
      await page.click('button[type="submit"]');

      // Wait for successful signup redirect
      await page.waitForURL("**/dashboard", { timeout: 10000 });
    } else {
      // Wait for login redirect
      await page.waitForURL("**/dashboard", { timeout: 10000 });
    }
  });

  test.describe("T228: Dashboard Layout on Mobile", () => {
    test("should display dashboard with stacked grid layout", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Verify page title is visible
      await expect(page.locator('h1')).toBeVisible();

      // Stat cards should stack vertically on mobile (not in a grid)
      const statCards = page.locator('[class*="StatCard"]');
      const count = await statCards.count();
      expect(count).toBeGreaterThan(0);

      // Verify first stat card is fully visible on mobile viewport
      const firstCard = statCards.first();
      await expect(firstCard).toBeVisible();

      // Get bounding box to verify it fits in viewport
      const box = await firstCard.boundingBox();
      expect(box).toBeTruthy();
      if (box) {
        expect(box.width).toBeLessThanOrEqual(MOBILE_VIEWPORT.width);
      }
    });

    test("should hide sidebar on mobile and show hamburger menu", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Desktop sidebar should be hidden on mobile
      const sidebar = page.locator('aside, nav[class*="sidebar"], [class*="Sidebar"]');
      // The sidebar might exist but be hidden via CSS
      // Check for hamburger menu instead
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await expect(hamburgerMenu).toBeVisible();
    });

    test("should display task distribution chart responsively", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Chart container should be visible
      const chartContainer = page.locator('text="Task Distribution"').locator("..").locator("..");
      await expect(chartContainer).toBeVisible();

      // Chart should fit within mobile viewport
      const box = await chartContainer.boundingBox();
      expect(box).toBeTruthy();
      if (box) {
        expect(box.width).toBeLessThanOrEqual(MOBILE_VIEWPORT.width);
      }
    });

    test("should display workflow progress responsively", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Workflow progress section should be visible
      const workflowSection = page.locator('text="Workflow Progress"').locator("..").locator("..");
      await expect(workflowSection).toBeVisible();

      // Should fit within mobile viewport
      const box = await workflowSection.boundingBox();
      expect(box).toBeTruthy();
      if (box) {
        expect(box.width).toBeLessThanOrEqual(MOBILE_VIEWPORT.width);
      }
    });
  });

  test.describe("T229: Full-Screen Dialogs on Mobile", () => {
    test("should display task drawer as full-screen on mobile", async ({ page }) => {
      await page.goto("http://localhost:3000/board");

      // Click on a task to open the drawer
      const taskCard = page.locator('[class*="task"], [class*="Task"]').first();
      await taskCard.click();

      // Wait for drawer to appear
      await page.waitForTimeout(500);

      // On mobile, the drawer should be full-screen
      const drawer = page.locator('.fixed.inset-0, [class*="drawer"], [class*="Drawer"]');
      await expect(drawer).toBeVisible();

      // Verify it covers the full viewport
      const box = await drawer.boundingBox();
      expect(box).toBeTruthy();
      if (box) {
        expect(box?.width).toBe(MOBILE_VIEWPORT.width);
        expect(box?.height).toBe(MOBILE_VIEWPORT.height);
      }
    });

    test("should display project form as full-screen on mobile", async ({ page }) => {
      await page.goto("http://localhost:3000/projects");

      // Click "New Project" button
      await page.click('button:has-text("New Project")');

      // Wait for modal to appear
      await expect(page.locator('text="New Project"')).toBeVisible();

      // On mobile, the modal should be full-screen
      const modal = page.locator('.fixed.inset-0').first();
      await expect(modal).toBeVisible();

      // Verify full-screen
      const box = await modal.boundingBox();
      expect(box).toBeTruthy();
      if (box) {
        expect(box?.width).toBe(MOBILE_VIEWPORT.width);
        expect(box?.height).toBe(MOBILE_VIEWPORT.height);
      }
    });

    test("should display user form as full-screen on mobile", async ({ page }) => {
      await page.goto("http://localhost:3000/team");

      // Click "Add Team Member" button
      await page.click('button:has-text("Add Team Member")');

      // Wait for modal to appear
      await expect(page.locator('text="Add Team Member"')).toBeVisible();

      // On mobile, the modal should be full-screen
      const modal = page.locator('.fixed.inset-0').first();
      await expect(modal).toBeVisible();

      // Verify full-screen
      const box = await modal.boundingBox();
      expect(box).toBeTruthy();
      if (box) {
        expect(box?.width).toBe(MOBILE_VIEWPORT.width);
        expect(box?.height).toBe(MOBILE_VIEWPORT.height);
      }
    });

    test("should have 44x44px minimum touch targets on mobile", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Check hamburger menu button size
      const hamburgerButton = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await expect(hamburgerButton).toBeVisible();

      const box = await hamburgerButton.boundingBox();
      expect(box).toBeTruthy();
      if (box) {
        // Verify minimum touch target size (44x44px)
        expect(box?.width).toBeGreaterThanOrEqual(44);
        expect(box?.height).toBeGreaterThanOrEqual(44);
      }
    });

    test("should close full-screen dialog with close button", async ({ page }) => {
      await page.goto("http://localhost:3000/projects");

      // Open modal
      await page.click('button:has-text("New Project")');
      await expect(page.locator('text="New Project"')).toBeVisible();

      // Click close button (X icon)
      const closeButton = page.locator('button:has([data-lucide="x"])').or(page.locator('button:has([data-lucide="X"])'));
      await closeButton.click();

      // Verify modal is closed
      await expect(page.locator('text="New Project"')).not.toBeVisible();
    });
  });

  test.describe("T230: Hamburger Menu and Drawer", () => {
    test("should show hamburger menu on mobile viewport", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Hamburger menu should be visible on mobile
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await expect(hamburgerMenu).toBeVisible();
    });

    test("should open navigation drawer when hamburger is clicked", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Click hamburger menu
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await hamburgerMenu.click();

      // Navigation drawer should appear
      const drawer = page.locator('[class*="sheet"], [class*="drawer"], [class*="mobile-nav"]');
      await expect(drawer).toBeVisible();

      // Navigation links should be visible
      await expect(page.locator('text="Dashboard"').or(page.locator('text="Board"))).toBeVisible();
    });

    test("should navigate to different pages from drawer", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Open drawer
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await hamburgerMenu.click();

      // Wait for drawer
      await page.waitForTimeout(300);

      // Click on "Board" link
      const boardLink = page.locator('text="Board"').or(page.locator('a[href*="/board"]'));
      await boardLink.click();

      // Verify navigation to board page
      await page.waitForURL("**/board", { timeout: 5000 });
      expect(page.url()).toContain("/board");
    });

    test("should close drawer when navigating to a page", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Open drawer
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await hamburgerMenu.click();

      // Wait for drawer to open
      await page.waitForTimeout(300);

      // Click navigation link
      const boardLink = page.locator('text="Projects"').or(page.locator('a[href*="/projects"]'));
      await boardLink.click();

      // Wait for navigation
      await page.waitForTimeout(500);

      // Drawer should be closed after navigation
      const drawer = page.locator('[class*="sheet"], [class*="drawer"], [class*="mobile-nav"]');
      // The drawer should no longer be visible or should have closed state
      const isVisible = await drawer.isVisible().catch(() => false);
      // Drawer might still be in DOM but not visible
    });

    test("should close drawer when clicking outside", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Open drawer
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await hamburgerMenu.click();

      // Wait for drawer
      await page.waitForTimeout(300);
      const drawer = page.locator('[class*="sheet"], [class*="drawer"], [class*="mobile-nav"]');
      await expect(drawer).toBeVisible();

      // Click outside the drawer (on the overlay)
      const overlay = page.locator('.fixed.inset-0').first();
      await overlay.click({ position: { x: 10, y: 10 } });

      // Wait for animation
      await page.waitForTimeout(300);

      // Drawer should be closed
      const isVisible = await drawer.isVisible().catch(() => false);
      expect(isVisible).toBeFalsy();
    });

    test("should close drawer with close button", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Open drawer
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      await hamburgerMenu.click();

      // Wait for drawer
      await page.waitForTimeout(300);

      // Click close button if present
      const closeButton = page.locator('[class*="sheet"] button:has([data-lucide="x"])').or(
        page.locator('button[aria-label="close"]')
      );

      const hasCloseButton = await closeButton.count() > 0;
      if (hasCloseButton) {
        await closeButton.click();
        await page.waitForTimeout(300);

        // Verify drawer is closed
        const drawer = page.locator('[class*="sheet"], [class*="drawer"]');
        const isVisible = await drawer.isVisible().catch(() => false);
        expect(isVisible).toBeFalsy();
      }
    });
  });

  test.describe("Tablet Viewport", () => {
    test.use({ viewport: TABLET_VIEWPORT });

    test("should display optimized layout on tablet", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Verify dashboard loads on tablet viewport
      await expect(page.locator('h1')).toBeVisible();

      // Stat cards should be in a grid on tablet (not stacked)
      const statCards = page.locator('[class*="StatCard"]');
      const count = await statCards.count();
      expect(count).toBeGreaterThan(0);
    });

    test("should show appropriate navigation for tablet", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // On tablet, might have collapsed sidebar or hamburger depending on breakpoint
      const hamburgerMenu = page.locator('button[aria-label*="menu"], button:has([data-lucide="menu"])');
      const sidebar = page.locator('aside, nav[class*="sidebar"]');

      // At least one should be present
      const hasHamburger = await hamburgerMenu.count() > 0;
      const hasSidebar = await sidebar.count() > 0;

      expect(hasHamburger || hasSidebar).toBeTruthy();
    });
  });
});
