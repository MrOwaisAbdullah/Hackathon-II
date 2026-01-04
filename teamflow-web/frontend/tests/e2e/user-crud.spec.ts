import { test, expect } from "@playwright/test";

/**
 * E2E Tests for User CRUD Workflow (Phase 10)
 *
 * These tests verify the complete team member management functionality
 * including adding, editing, and removing team members.
 *
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Frontend server running on http://localhost:3000
 * - Admin user account exists or can be created
 */

test.describe("User CRUD Workflow", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto("http://localhost:3000/login");

    const email = "usere2e@test.com";
    const password = "password123";

    // Try to login first
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    // If login fails (user doesn't exist), signup first
    const url = page.url();
    if (url.includes("/login")) {
      await page.goto("http://localhost:3000/signup");
      await page.fill('input[name="agencyName"]', "User E2E Agency");
      await page.fill('input[name="agencyEmail"]', "usere2e-agency@test.com");
      await page.fill('input[name="name"]', "User E2E Admin");
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

  test("should display team page with add button", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Verify page title
    await expect(page.locator('h1:has-text("Team")')).toBeVisible();

    // Verify "Add Team Member" button is present
    await expect(page.locator('button:has-text("Add Team Member")')).toBeVisible();
  });

  test("should add a new team member with temp password", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Wait for modal to appear
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Generate unique email for this test run
    const timestamp = Date.now();
    const testEmail = `newmember${timestamp}@test.com`;

    // Fill in user details
    await page.fill('input[name="name"]', 'New Team Member');
    await page.fill('input[name="email"]', testEmail);

    // Select role (default is Member)
    await page.selectOption('select[name="role"]', 'member');

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for temp password display
    await page.waitForTimeout(1000);

    // Verify temp password is displayed
    await expect(page.locator('text="Team Member Added!"')).toBeVisible();

    // Verify temp password field exists and has content (12+ chars)
    const tempPassword = page.locator('.font-mono.font-bold');
    await expect(tempPassword).toBeVisible();
    const passwordText = await tempPassword.textContent();
    expect(passwordText?.length).toBeGreaterThanOrEqual(12);

    // Click Done to close modal
    await page.click('button:has-text("Done")');

    // Verify user was added to the list
    await expect(page.locator(`text="${testEmail}"`)).toBeVisible();
  });

  test("should add a team member with admin role", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Wait for modal
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Fill in user details
    const timestamp = Date.now();
    await page.fill('input[name="name"]', 'Admin User');
    await page.fill('input[name="email"]', `admin${timestamp}@test.com`);

    // Select Admin role
    await page.selectOption('select[name="role"]', 'admin');

    // Submit
    await page.click('button[type="submit"]');

    // Wait for temp password display and close it
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Done")');

    // Verify user was added with Admin badge
    await expect(page.locator('text="Admin User"')).toBeVisible();

    // Check for Admin badge (purple color)
    const adminBadge = page.locator('.bg-purple-100, .dark\\:bg-purple-900\\/30');
    await expect(adminBadge).toBeVisible();
  });

  test("should add a project manager", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Wait for modal
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Fill in user details
    const timestamp = Date.now();
    await page.fill('input[name="name"]', 'Project Manager User');
    await page.fill('input[name="email"]', `pm${timestamp}@test.com`);

    // Check the Project Manager checkbox
    await page.check('input[name="is_project_manager"]');

    // Submit
    await page.click('button[type="submit"]');

    // Wait and close
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Done")');

    // Verify PM badge is shown
    await expect(page.locator('text="Project Manager User"')).toBeVisible();
    await expect(page.locator('text="PM"')).toBeVisible();
  });

  test("should validate required fields", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Wait for modal
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Try to submit without filling required fields
    await page.click('button[type="submit"]');

    // Verify validation errors
    await expect(page.locator('text="Name is required"')).toBeVisible();
    await expect(page.locator('text="Email is required"')).toBeVisible();
  });

  test("should validate email format", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Wait for modal
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Fill name but invalid email
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="email"]', 'not-an-email');

    // Blur the email field to trigger validation
    await page.blur('input[name="email"]');

    // Verify email validation error
    await expect(page.locator('text="Invalid email address"')).toBeVisible();
  });

  test("should edit an existing team member", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // First create a user to edit
    await page.click('button:has-text("Add Team Member")');
    const timestamp = Date.now();
    await page.fill('input[name="name"]', 'User to Edit');
    await page.fill('input[name="email"]', `edit${timestamp}@test.com`);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Done")');

    // Find and click the edit button on the user card
    const userCard = page.locator(`text="User to Edit"`).locator("..").locator("..").locator("..");
    await userCard.hover();

    // Click the actions menu button (three dots)
    const actionsButton = userCard.locator('button').filter({ hasText: '' }).nth(1); // MoreHorizontal button
    await actionsButton.click();

    // Click "Edit Member" option
    await page.click('text=Edit Member');

    // Wait for edit modal to appear
    await expect(page.locator('text="Edit Team Member"')).toBeVisible();

    // Update user details
    await page.fill('input[name="name"]', 'Updated User Name');

    // Change role to Admin
    await page.selectOption('select[name="role"]', 'admin');

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for modal to close
    await page.waitForTimeout(1000);

    // Verify user was updated
    await expect(page.locator('text="Updated User Name"')).toBeVisible();
  });

  test("should remove a team member with confirmation", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // First create a user to delete
    await page.click('button:has-text("Add Team Member")');
    const timestamp = Date.now();
    await page.fill('input[name="name"]', 'User to Delete');
    await page.fill('input[name="email"]', `delete${timestamp}@test.com`);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);
    await page.click('button:has-text("Done")');

    // Find and click the delete button on the user card
    const userCard = page.locator(`text="User to Delete"`).locator("..").locator("..").locator("..");
    await userCard.hover();

    // Click the actions menu button
    const actionsButton = userCard.locator('button').filter({ hasText: '' }).nth(1);
    await actionsButton.click();

    // Click "Remove Member" option
    await page.click('text=Remove Member');

    // Handle the confirm dialog (browser native confirm)
    page.on("dialog", (dialog) => {
      expect(dialog.message()).toContain("User to Delete");
      dialog.accept();
    });

    // Wait for user to be removed
    await page.waitForTimeout(1000);

    // Verify user was deleted
    await expect(page.locator('text="User to Delete"')).not.toBeVisible();
  });

  test("should prevent deleting the last admin", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Count current admin users
    const adminBadges = await page.locator('.bg-purple-100, .dark\\:bg-purple-900\\/30').count();

    // If there's only one admin (the current user), try to find and delete them
    if (adminBadges === 1) {
      // Find the admin card
      const adminCard = page.locator('.bg-purple-100, .dark\\:bg-purple-900\\/30').locator("..").locator("..").locator("..").locator("..");
      await adminCard.hover();

      // Try to delete
      const actionsButton = adminCard.locator('button').filter({ hasText: '' }).nth(1);
      await actionsButton.click();
      await page.click('text=Remove Member');

      // The deletion should be blocked with a warning message
      // Either the confirm dialog won't show, or there will be an error message
      await page.waitForTimeout(1000);

      // Verify error/warning message about last admin
      const errorMessage = page.locator('text="Cannot remove the last admin", text="last admin"');
      await expect(errorMessage).toBeVisible();
    }
  });

  test("should show loading state during user operations", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Intercept API to add delay
    await page.route("**/api/v1/users", async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 500));
      route.continue();
    });

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Check for modal
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Fill and submit
    const timestamp = Date.now();
    await page.fill('input[name="name"]', 'Loading Test User');
    await page.fill('input[name="email"]', `loading${timestamp}@test.com`);
    await page.click('button[type="submit"]');

    // Verify loading indicator
    await expect(page.locator('[data-lucide="loader2"]')).toBeVisible();
  });

  test("should close modal when clicking cancel", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Wait for modal
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Click Cancel button
    await page.click('button:has-text("Cancel")');

    // Verify modal is closed
    await expect(page.locator('text="Add Team Member"')).not.toBeVisible();
  });

  test("should close modal when clicking outside", async ({ page }) => {
    await page.goto("http://localhost:3000/team");

    // Click "Add Team Member" button
    await page.click('button:has-text("Add Team Member")');

    // Wait for modal
    await expect(page.locator('text="Add Team Member"')).toBeVisible();

    // Click outside the modal (on the backdrop)
    const backdrop = page.locator('.fixed.inset-0.bg-black\\/50');
    await backdrop.click({ position: { x: 10, y: 10 } });

    // Verify modal is closed
    await expect(page.locator('text="Add Team Member"')).not.toBeVisible();
  });
});
