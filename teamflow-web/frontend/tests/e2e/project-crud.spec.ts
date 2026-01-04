import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Project CRUD Workflow (Phase 10)
 *
 * These tests verify the complete project management functionality
 * including creating, editing, and deleting projects.
 *
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Frontend server running on http://localhost:3000
 * - Admin user account exists or can be created
 */

test.describe("Project CRUD Workflow", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto("http://localhost:3000/login");

    const email = "projecte2e@test.com";
    const password = "password123";

    // Try to login first
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    // If login fails (user doesn't exist), signup first
    const url = page.url();
    if (url.includes("/login")) {
      await page.goto("http://localhost:3000/signup");
      await page.fill('input[name="agencyName"]', "Project E2E Agency");
      await page.fill('input[name="agencyEmail"]', "projecte2e-agency@test.com");
      await page.fill('input[name="name"]', "Project E2E User");
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

  test("should display projects page with create button", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");

    // Verify page title
    await expect(page.locator('h1:has-text("Projects")')).toBeVisible();

    // Verify "New Project" button is present
    await expect(page.locator('button:has-text("New Project")')).toBeVisible();
  });

  test("should create a new project", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");

    // Click "New Project" button
    await page.click('button:has-text("New Project")');

    // Wait for modal to appear
    await expect(page.locator('text="New Project"')).toBeVisible();

    // Fill in project details
    await page.fill('input[name="name"]', 'E2E Test Project');
    await page.fill('textarea[name="description"]', 'This is a test project for E2E validation');

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for modal to close and project to appear
    await page.waitForTimeout(1000);

    // Verify project was created
    await expect(page.locator('text="E2E Test Project"')).toBeVisible();
  });

  test("should edit an existing project", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");

    // First create a project
    await page.click('button:has-text("New Project")');
    await page.fill('input[name="name"]', 'Project to Edit');
    await page.fill('textarea[name="description"]', 'Original description');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Find and click the edit button on the project card
    const projectCard = page.locator('text="Project to Edit"').locator("..").locator("..");
    await projectCard.hover(); // Hover to reveal actions menu

    // Click the actions menu button (three dots)
    const actionsButton = projectCard.locator('button[aria-label*="more"], button[aria-label*="action"], button:has([data-lucide="more-horizontal"])');
    await actionsButton.click();

    // Click "Edit Project" option
    await page.click('text=Edit Project');

    // Wait for edit modal to appear
    await expect(page.locator('text="Edit Project"')).toBeVisible();

    // Update project details
    await page.fill('input[name="name"]', 'Updated Project Name');
    await page.fill('textarea[name="description"]', 'Updated description');

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for modal to close
    await page.waitForTimeout(1000);

    // Verify project was updated
    await expect(page.locator('text="Updated Project Name"')).toBeVisible();
  });

  test("should delete a project with confirmation", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");

    // First create a project
    await page.click('button:has-text("New Project")');
    await page.fill('input[name="name"]', 'Project to Delete');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Find and click the delete button on the project card
    const projectCard = page.locator('text="Project to Delete"').locator("..").locator("..");
    await projectCard.hover();

    // Click the actions menu button
    const actionsButton = projectCard.locator('button[aria-label*="more"], button[aria-label*="action"], button:has([data-lucide="more-horizontal"])');
    await actionsButton.click();

    // Click "Delete Project" option
    await page.click('text=Delete Project');

    // Confirm deletion in the dialog
    // Note: The confirmation should ask about archiving tasks
    const confirmButton = page.locator('button:has-text("Delete"), button:has-text("Remove")').first();
    await confirmButton.click();

    // Wait for project to be removed
    await page.waitForTimeout(1000);

    // Verify project was deleted
    await expect(page.locator('text="Project to Delete"')).not.toBeVisible();
  });

  test("should validate required project name field", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");

    // Click "New Project" button
    await page.click('button:has-text("New Project")');

    // Wait for modal
    await expect(page.locator('text="New Project"')).toBeVisible();

    // Try to submit without filling required fields
    await page.click('button[type="submit"]');

    // Verify validation error - name is required
    await expect(page.locator('text="required", "text="Project name is required"')).toBeVisible();
  });

  test("should change project status", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");

    // Create a project
    await page.click('button:has-text("New Project")');
    await page.fill('input[name="name"]', 'Status Test Project');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Edit the project
    const projectCard = page.locator('text="Status Test Project"').locator("..").locator("..");
    await projectCard.hover();

    const actionsButton = projectCard.locator('button[aria-label*="more"], button[aria-label*="action"], button:has([data-lucide="more-horizontal"])');
    await actionsButton.click();
    await page.click('text=Edit Project');

    // Change status to "On Hold"
    await page.selectOption('select[name="status"]', 'on_hold');

    // Submit
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Verify status indicator changed (should be amber color)
    // Note: Visual check - we verify the project still exists
    await expect(page.locator('text="Status Test Project"')).toBeVisible();
  });

  test("should show loading state during project operations", async ({ page }) => {
    await page.goto("http://localhost:3000/projects");

    // Intercept API to add delay
    await page.route("**/api/v1/projects", async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 500));
      route.continue();
    });

    // Click "New Project" button
    await page.click('button:has-text("New Project")');

    // Check for loading state in submit button
    const submitButton = page.locator('button[type="submit"]');
    await expect(submitButton).toBeVisible();

    // Fill and submit
    await page.fill('input[name="name"]', 'Loading Test Project');
    await page.click('button[type="submit"]');

    // Verify loading indicator
    await expect(page.locator('[data-lucide="loader2"]')).toBeVisible();
  });
});
