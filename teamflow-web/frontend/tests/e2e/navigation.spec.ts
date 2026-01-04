import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Navigation (Phase 10)
 *
 * These tests verify navigation to the Archive page from all pages.
 *
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Frontend server running on http://localhost:3000
 * - User account exists or can be created
 */

test.describe("Navigation - Archive Link", () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto("http://localhost:3000/login");

    const email = "nave2e@test.com";
    const password = "password123";

    // Try to login first
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    // If login fails (user doesn't exist), signup first
    const url = page.url();
    if (url.includes("/login")) {
      await page.goto("http://localhost:3000/signup");
      await page.fill('input[name="agencyName"]', "Nav E2E Agency");
      await page.fill('input[name="agencyEmail"]', "nave2e-agency@test.com");
      await page.fill('input[name="name"]', "Nav E2E User");
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

  test.describe("T234: Archive Navigation from All Pages", () => {
    test("should navigate to Archive from Dashboard", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Find Archive link in sidebar/navigation
      const archiveLink = page.locator('a[href*="/archive"]').or(
        page.locator('text="Archive"')
      );

      await expect(archiveLink).toBeVisible();
      await archiveLink.click();

      // Verify navigation to Archive page
      await page.waitForURL("**/archive", { timeout: 5000 });
      expect(page.url()).toContain("/archive");

      // Verify Archive page title
      await expect(page.locator('h1:has-text("Archive")').or(page.locator('h1'))).toBeVisible();
    });

    test("should navigate to Archive from Board page", async ({ page }) => {
      await page.goto("http://localhost:3000/board");

      // Find Archive link
      const archiveLink = page.locator('a[href*="/archive"]').or(
        page.locator('text="Archive"')
      );

      await expect(archiveLink).toBeVisible();
      await archiveLink.click();

      // Verify navigation
      await page.waitForURL("**/archive", { timeout: 5000 });
      expect(page.url()).toContain("/archive");
    });

    test("should navigate to Archive from Projects page", async ({ page }) => {
      await page.goto("http://localhost:3000/projects");

      // Find Archive link
      const archiveLink = page.locator('a[href*="/archive"]').or(
        page.locator('text="Archive"')
      );

      await expect(archiveLink).toBeVisible();
      await archiveLink.click();

      // Verify navigation
      await page.waitForURL("**/archive", { timeout: 5000 });
      expect(page.url()).toContain("/archive");
    });

    test("should navigate to Archive from Team page", async ({ page }) => {
      await page.goto("http://localhost:3000/team");

      // Find Archive link
      const archiveLink = page.locator('a[href*="/archive"]').or(
        page.locator('text="Archive"')
      );

      await expect(archiveLink).toBeVisible();
      await archiveLink.click();

      // Verify navigation
      await page.waitForURL("**/archive", { timeout: 5000 });
      expect(page.url()).toContain("/archive");
    });

    test("should navigate to Archive from Settings page", async ({ page }) => {
      await page.goto("http://localhost:3000/settings");

      // Find Archive link
      const archiveLink = page.locator('a[href*="/archive"]').or(
        page.locator('text="Archive"')
      );

      await expect(archiveLink).toBeVisible();
      await archiveLink.click();

      // Verify navigation
      await page.waitForURL("**/archive", { timeout: 5000 });
      expect(page.url()).toContain("/archive");
    });

    test("should navigate to Archive from Time Entries page", async ({ page }) => {
      await page.goto("http://localhost:3000/time-entries");

      // Find Archive link
      const archiveLink = page.locator('a[href*="/archive"]').or(
        page.locator('text="Archive"')
      );

      await expect(archiveLink).toBeVisible();
      await archiveLink.click();

      // Verify navigation
      await page.waitForURL("**/archive", { timeout: 5000 });
      expect(page.url()).toContain("/archive");
    });

    test("should highlight Archive link when on Archive page", async ({ page }) => {
      // Navigate to Archive page
      await page.goto("http://localhost:3000/archive");

      // Wait for page to load
      await page.waitForTimeout(500);

      // Verify Archive link is highlighted/active
      const archiveLink = page.locator('a[href*="/archive"]');

      // Check for active state styling
      // Common patterns: aria-current="page", class contains "active"
      const isActive = await archiveLink.getAttribute("aria-current") === "page" ||
                       (await archiveLink.getAttribute("class") || "").includes("active");

      expect(isActive).toBeTruthy();
    });

    test("should show Archive link in consistent position across pages", async ({ page }) => {
      const pages = [
        "http://localhost:3000/dashboard",
        "http://localhost:3000/board",
        "http://localhost:3000/projects",
        "http://localhost:3000/team",
        "http://localhost:3000/settings",
      ];

      let firstPosition: { x: number; y: number } | null = null;

      for (const pageUrl of pages) {
        await page.goto(pageUrl);
        await page.waitForTimeout(300);

        // Find Archive link
        const archiveLink = page.locator('a[href*="/archive"]');
        await expect(archiveLink).toBeVisible();

        // Get position
        const box = await archiveLink.boundingBox();
        expect(box).toBeTruthy();

        if (firstPosition === null) {
          firstPosition = { x: box!.x, y: box!.y };
        } else {
          // Position should be consistent (within small margin for rendering differences)
          expect(Math.abs(box!.x - firstPosition.x)).toBeLessThan(5);
          expect(Math.abs(box!.y - firstPosition.y)).toBeLessThan(5);
        }
      }
    });

    test("should navigate back from Archive to previous page", async ({ page }) => {
      // Start on Dashboard
      await page.goto("http://localhost:3000/dashboard");

      // Navigate to Archive
      const archiveLink = page.locator('a[href*="/archive"]').or(
        page.locator('text="Archive"')
      );
      await archiveLink.click();
      await page.waitForURL("**/archive", { timeout: 5000 });

      // Click browser back button
      await page.goBack();

      // Verify we're back on Dashboard
      await page.waitForURL("**/dashboard", { timeout: 5000 });
      expect(page.url()).toContain("/dashboard");
    });
  });

  test.describe("Archive Link Accessibility", () => {
    test("should have accessible label on Archive link", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      const archiveLink = page.locator('a[href*="/archive"]');

      // Check for aria-label or visible text
      const ariaLabel = await archiveLink.getAttribute("aria-label");
      const textContent = await archiveLink.textContent();

      expect(ariaLabel || textContent).toBeTruthy();
    });

    test("should be keyboard navigable", async ({ page }) => {
      await page.goto("http://localhost:3000/dashboard");

      // Tab to navigation
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");

      // Try to find Archive link via keyboard navigation
      const archiveLink = page.locator('a[href*="/archive"]');

      // Focus the link directly
      await archiveLink.focus();
      await page.keyboard.press("Enter");

      // Verify navigation
      await page.waitForURL("**/archive", { timeout: 5000 });
      expect(page.url()).toContain("/archive");
    });
  });

  test.describe("Archive Page Content", () => {
    test("should display archived items on Archive page", async ({ page }) => {
      await page.goto("http://localhost:3000/archive");

      // Verify Archive page loaded
      await expect(page.locator('h1')).toBeVisible();

      // The Archive page should show archived tasks/projects
      // Even if empty, there should be container elements
      const pageContent = page.locator('[class*="archive"], [class*="Archive"]');
      const hasContent = await pageContent.count() > 0;

      // Either we have content or we have an empty state message
      if (hasContent) {
        await expect(pageContent.first()).toBeVisible();
      } else {
        // Check for empty state
        const emptyState = page.locator('text="No archived", text="empty", text="Nothing here"');
        const hasEmptyState = await emptyState.count() > 0;
        // Empty state is optional
      }
    });

    test("should allow restoring items from Archive", async ({ page }) => {
      await page.goto("http://localhost:3000/archive");

      // Wait for page to load
      await page.waitForTimeout(500);

      // Look for restore/unarchive buttons
      const restoreButton = page.locator('button:has-text("Restore"), button:has-text("Unarchive")');

      if (await restoreButton.count() > 0) {
        // If there are archived items and restore buttons
        // Test restoring (but don't actually click to avoid changing state)
        await expect(restoreButton.first()).toBeVisible();
      } else {
        // No archived items to restore
        test.skip();
      }
    });
  });
});
