import { test, expect } from '@playwright/test';

/**
 * Phase 13 Mobile Responsiveness E2E Tests
 *
 * Tests mobile viewport responsiveness including:
 * - T650: Dashboard layout on 375px viewport
 * - T651: Header layout on mobile viewport
 * - T652: Card overflow prevention on mobile
 * - T653: Mobile sidebar dark theme consistency
 */

test.describe('Mobile Responsiveness (Phase 13)', () => {
  // Use mobile viewport for all tests
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
  });

  test('T650: dashboard uses reduced padding on mobile', async ({ page }) => {
    await page.goto('/dashboard');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check main container padding
    const mainContainer = page.locator('div').filter({ hasText: 'Dashboard' }).first();
    const paddingTop = await mainContainer.evaluate(el => {
      return window.getComputedStyle(el).paddingTop;
    });

    // On mobile, padding should be less than 16px (p-2 = 8px)
    expect(parseInt(paddingTop)).toBeLessThan(16);

    // Verify dashboard content is visible
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('T651: header elements do not collapse on mobile', async ({ page }) => {
    await page.goto('/dashboard');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check for header elements
    const heading = page.locator('h1:has-text("Dashboard")');
    await expect(heading).toBeVisible();

    // Verify heading is not cut off or overlapping
    const headingBox = await heading.boundingBox();
    expect(headingBox).toBeTruthy();
    expect(headingBox!.y).toBeGreaterThan(0);
    expect(headingBox!.x).toBeLessThan(375); // Within viewport width
  });

  test('T651: projects page header does not collapse', async ({ page }) => {
    await page.goto('/projects');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check heading is visible
    const heading = page.locator('h1:has-text("Projects")');
    await expect(heading).toBeVisible();

    // Check button is visible and not overlapping
    const button = page.locator('button:has-text("New Project")');
    await expect(button).toBeVisible();

    // Verify button is clickable (not behind other elements)
    await button.click();
    // Should open form dialog, not do nothing
  });

  test('T651: team page header does not collapse', async ({ page }) => {
    await page.goto('/team');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check heading is visible
    const heading = page.locator('h1:has-text("Team")');
    await expect(heading).toBeVisible();

    // Check button is visible
    const button = page.locator('button:has-text("Add Team Member")');
    await expect(button).toBeVisible();
  });

  test('T652: card content does not overflow on dashboard', async ({ page }) => {
    await page.goto('/dashboard');

    // Wait for content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Extra time for data loading

    // Check for stat cards
    const cards = page.locator('.card-float').or(page.locator('[class*="card"]'));

    const cardCount = await cards.count();
    expect(cardCount).toBeGreaterThan(0);

    // Verify no horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBe(viewportWidth);
  });

  test('T652: task cards do not overflow on mobile', async ({ page }) => {
    await page.goto('/tasks');

    // Wait for content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Check for task cards
    const taskCards = page.locator('[class*="TaskCard"]').or(page.locator('.group.relative.border'));

    const cardCount = await taskCards.count();
    if (cardCount > 0) {
      // Check first task card
      const firstCard = taskCards.first();
      await expect(firstCard).toBeVisible();

      // Verify card content doesn't overflow
      const scrollWidth = await firstCard.evaluate(el => el.scrollWidth);
      const clientWidth = await firstCard.evaluate(el => el.clientWidth);
      expect(scrollWidth).toBe(clientWidth);
    }
  });

  test('T652: project cards do not overflow on mobile', async ({ page }) => {
    await page.goto('/projects');

    // Wait for content to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Check for project cards
    const projectCards = page.locator('[class*="ProjectCard"]').or(page.locator('.group.relative.border'));

    const cardCount = await projectCards.count();
    if (cardCount > 0) {
      // Check first project card
      const firstCard = projectCards.first();
      await expect(firstCard).toBeVisible();

      // Verify card content doesn't overflow
      const scrollWidth = await firstCard.evaluate(el => el.scrollWidth);
      const clientWidth = await firstCard.evaluate(el => el.clientWidth);
      expect(scrollWidth).toBe(clientWidth);
    }
  });

  test('T653: mobile sidebar uses dark theme', async ({ page }) => {
    await page.goto('/dashboard');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Toggle mobile menu
    const menuButton = page.locator('button[aria-label="Open menu"]').or(page.locator('button:has(svg.menu)'));
    await menuButton.click();

    // Wait for sidebar to appear
    await page.waitForTimeout(300);

    // Check for sidebar
    const sidebar = page.locator('[role="dialog"]').or(page.locator('.fixed.z-50'));

    // Get sidebar background color
    const bgColor = await sidebar.evaluate(el => {
      return window.getComputedStyle(el).backgroundColor;
    });

    // In dark theme (sidebar-dark), background should be dark (not white)
    // RGB values for white are 255, 255, 255
    const isWhite = bgColor === 'rgb(255, 255, 255)' || bgColor === '#ffffff' || bgColor === '#fff';
    expect(isWhite).toBeFalsy();

    // Close sidebar
    const closeButton = page.locator('button[aria-label="Close"]').or(page.locator('button:has(svg)'));
    await closeButton.click();
  });

  test('overall: no horizontal scroll on any mobile page', async ({ page }) => {
    const pages = ['/dashboard', '/tasks', '/projects', '/team'];

    for (const pagePath of pages) {
      await page.goto(pagePath);
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);

      // Check for no horizontal scroll
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);

      expect(bodyWidth).toBe(viewportWidth);
    }
  });
});
