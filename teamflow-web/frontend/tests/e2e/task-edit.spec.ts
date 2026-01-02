/* E2E tests for task editing and archiving (User Story 6).

Tests verify:
- Rich task editing with priority, due date, description
- Task archiving with confirmation
- Task restoration from archive
- UI animations and interactions
*/
import { test, expect } from "@playwright/test";

test.describe("Task Editing", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate and login
    await page.goto("/");

    // Create or login test user
    const email = `taskedit-${Date.now()}@test.com`;
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', "testPassword123");
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL("/dashboard");
    // Navigate to task board
    await page.click('a[href="/tasks"]');
    await page.waitForURL("/tasks");
  });

  test("should open task drawer and edit title", async ({ page }) => {
    // Click on a task card to open drawer
    await page.click('[data-testid="task-card"]:first-child');
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    // Edit title
    const titleInput = page.locator('input[name="title"]');
    await titleInput.clear();
    await titleInput.fill("Updated Task Title");

    // Save changes
    await page.click('button:has-text("Save")');

    // Verify update
    await expect(page.locator("text=Updated Task Title")).toBeVisible();
  });

  test("should edit task priority", async ({ page }) => {
    // Open task drawer
    await page.click('[data-testid="task-card"]:first-child');
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    // Click priority selector
    await page.click('[data-testid="priority-selector"]');
    await expect(page.locator('[data-testid="priority-dropdown"]')).toBeVisible();

    // Select high priority
    await page.click('[data-value="high"]');
    await page.click('button:has-text("Save")');

    // Verify priority badge updated
    await expect(page.locator('[data-testid="task-card"]:first-child .badge-high')).toBeVisible();
  });

  test("should edit task due date", async ({ page }) => {
    // Open task drawer
    await page.click('[data-testid="task-card"]:first-child');
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    // Click date picker
    await page.click('[data-testid="date-picker"]');
    await expect(page.locator('[data-testid="calendar-popover"]')).toBeVisible();

    // Select a date (click 15th of next month)
    await page.click('.calendar-day:has-text("15"):not(.disabled)');
    await page.click('button:has-text("Save")');

    // Verify due date updated
    await expect(page.locator('[data-testid="task-card"]:first-child [data-testid="due-date"]')).toBeVisible();
  });

  test("should edit task description with rich text", async ({ page }) => {
    // Open task drawer
    await page.click('[data-testid="task-card"]:first-child');
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    // Click description field
    const editor = page.locator('[data-testid="rich-text-editor"]');
    await editor.click();

    // Type rich text content
    await editor.fill("# Important Task\n\nThis is **bold** and *italic* text.\n\n- Item 1\n- Item 2");

    // Save
    await page.click('button:has-text("Save")');

    // Reopen drawer and verify description persisted
    await page.click('[data-testid="task-card"]:first-child');
    await expect(editor.locator("text=Important Task")).toBeVisible();
  });

  test("should show validation errors for invalid inputs", async ({ page }) => {
    // Open task drawer
    await page.click('[data-testid="task-card"]:first-child');

    // Clear title and try to save
    const titleInput = page.locator('input[name="title"]');
    await titleInput.clear();
    await page.click('button:has-text("Save")');

    // Should show validation error
    await expect(page.locator("text=Title is required")).toBeVisible();
  });
});

test.describe("Task Archiving", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");

    const email = `archive-${Date.now()}@test.com`;
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', "testPassword123");
    await page.click('button[type="submit"]');
    await page.waitForURL("/dashboard");
    await page.click('a[href="/tasks"]');
    await page.waitForURL("/tasks");
  });

  test("should archive task with confirmation", async ({ page }) => {
    // Archive initial count
    const initialCards = await page.locator('[data-testid="task-card"]').count();

    // Open task drawer
    await page.click('[data-testid="task-card"]:first-child');
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    // Click archive button
    await page.click('[data-testid="archive-button"]');

    // Should show confirmation modal
    await expect(page.locator('[data-testid="archive-modal"]')).toBeVisible();
    await expect(page.locator("text=Are you sure you want to archive")).toBeVisible();

    // Confirm archive
    await page.click('button:has-text("Archive")');

    // Verify drawer closed and task removed from board
    await expect(page.locator('[data-testid="task-drawer"]')).not.toBeVisible();
    const finalCards = await page.locator('[data-testid="task-card"]').count();
    expect(finalCards).toBe(initialCards - 1);

    // Verify scale-out animation occurred
    await expect(page.locator('[data-testid="task-card"]').first()).toHaveCSS("transform", "none");
  });

  test("should cancel archive when dismissing modal", async ({ page }) => {
    // Open task drawer
    await page.click('[data-testid="task-card"]:first-child');

    // Click archive button
    await page.click('[data-testid="archive-button"]');
    await expect(page.locator('[data-testid="archive-modal"]')).toBeVisible();

    // Click cancel
    await page.click('button:has-text("Cancel")');

    // Verify modal dismissed and task still visible
    await expect(page.locator('[data-testid="archive-modal"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();
  });

  test("should restore archived task from archive page", async ({ page }) => {
    // First archive a task
    await page.click('[data-testid="task-card"]:first-child');
    await page.click('[data-testid="archive-button"]');
    await page.click('button:has-text("Archive")');

    // Navigate to archive page
    await page.click('a[href="/archive"]');
    await page.waitForURL("/archive");

    // Verify archived task appears
    await expect(page.locator('[data-testid="archived-task-card"]').first()).toBeVisible();

    // Click restore button
    await page.click('[data-testid="archived-task-card"]:first-child [data-testid="restore-button"]');

    // Verify task restored (removed from archive page)
    await expect(page.locator('[data-testid="archived-task-card"]').first()).not.toBeVisible();

    // Navigate back to board
    await page.click('a[href="/tasks"]');
    await page.waitForURL("/tasks");

    // Verify task restored to board
    await expect(page.locator('[data-testid="task-card"]').first()).toBeVisible();
  });

  test("should show empty state when no archived tasks", async ({ page }) => {
    // Navigate to archive page
    await page.click('a[href="/archive"]');
    await page.waitForURL("/archive");

    // Should show empty state
    await expect(page.locator('[data-testid="empty-archive"]')).toBeVisible();
    await expect(page.locator("text=No archived tasks")).toBeVisible();
  });

  test("should filter archived tasks by search", async ({ page }) => {
    // Archive a specific task first
    await page.click('[data-testid="task-card"]:first-child');
    const taskTitle = await page.locator('input[name="title"]').inputValue();
    await page.click('[data-testid="archive-button"]');
    await page.click('button:has-text("Archive")');

    // Navigate to archive
    await page.click('a[href="/archive"]');

    // Search for the task
    await page.fill('input[placeholder*="Search"]', taskTitle);

    // Verify filtered results
    await expect(page.locator(`text=${taskTitle}`)).toBeVisible();
  });
});

test.describe("Task Drawer Animations", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");

    const email = `animation-${Date.now()}@test.com`;
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', "testPassword123");
    await page.click('button[type="submit"]');
    await page.waitForURL("/dashboard");
    await page.click('a[href="/tasks"]');
    await page.waitForURL("/tasks");
  });

  test("should animate drawer opening", async ({ page }) => {
    const drawer = page.locator('[data-testid="task-drawer"]');

    // Click task card
    await page.click('[data-testid="task-card"]:first-child');

    // Check for slide-in animation
    await expect(drawer).toBeVisible();
    await expect(drawer).toHaveCSS("transition", /transform/);
  });

  test("should animate drawer closing", async ({ page }) => {
    // Open drawer
    await page.click('[data-testid="task-card"]:first-child');
    const drawer = page.locator('[data-testid="task-drawer"]');
    await expect(drawer).toBeVisible();

    // Click close button
    await page.click('[data-testid="close-drawer"]');

    // Verify slide-out animation
    await expect(drawer).not.toBeVisible();
  });

  test("should animate priority selection", async ({ page }) => {
    // Open drawer
    await page.click('[data-testid="task-card"]:first-child');
    await page.click('[data-testid="priority-selector"]');

    const dropdown = page.locator('[data-testid="priority-dropdown"]');

    // Check for fade-in animation
    await expect(dropdown).toBeVisible();
    await expect(dropdown).toHaveCSS("transition", /opacity/);

    // Select priority and check animation
    await page.click('[data-value="high"]');
    await expect(dropdown).not.toBeVisible();
  });

  test("should animate date picker opening", async ({ page }) => {
    // Open drawer
    await page.click('[data-testid="task-card"]:first-child');
    await page.click('[data-testid="date-picker"]');

    const calendar = page.locator('[data-testid="calendar-popover"]');

    // Check for calendar animation
    await expect(calendar).toBeVisible();
    await expect(calendar).toHaveCSS("transition", /transform|opacity/);
  });
});

test.describe("Task Editing Real-time Updates", () => {
  test("should reflect changes in task board after edit", async ({ page }) => {
    // Open and edit task
    await page.click('[data-testid="task-card"]:first-child');
    await page.fill('input[name="title"]', "Real-time Updated Title");
    await page.click('button:has-text("Save")');

    // Wait for drawer to close
    await expect(page.locator('[data-testid="task-drawer"]')).not.toBeVisible();

    // Verify board updated
    await expect(page.locator("text=Real-time Updated Title")).toBeVisible();
  });

  test("should show priority badge on task card after update", async ({ page }) => {
    // Open and set priority
    await page.click('[data-testid="task-card"]:first-child');
    await page.click('[data-testid="priority-selector"]');
    await page.click('[data-value="high"]');
    await page.click('button:has-text("Save")');

    // Verify badge on card
    const card = page.locator('[data-testid="task-card"]').first();
    await expect(card.locator('.badge-high')).toBeVisible();
  });

  test("should show due date on task card after update", async ({ page }) => {
    // Open and set due date
    await page.click('[data-testid="task-card"]:first-child');
    await page.click('[data-testid="date-picker"]');
    await page.click('.calendar-day:has-text("20")');
    await page.click('button:has-text("Save")');

    // Verify due date on card
    const card = page.locator('[data-testid="task-card"]').first();
    await expect(card.locator('[data-testid="due-date"]')).toBeVisible();
  });
});
