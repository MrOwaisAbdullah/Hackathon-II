import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Task Board Drag-and-Drop (User Story 2)
 *
 * These tests verify the complete drag-and-drop functionality
 * of the Kanban task board including status updates and animations.
 *
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Test user account exists or can be created
 * - @dnd-kit/core library is installed
 */

test.describe("Task Board Drag-and-Drop", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto("http://localhost:3000/login");

    // Login with test credentials (or signup first)
    const email = "e2e@test.com";
    const password = "password123";

    // Try to login first
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    // If login fails (user doesn't exist), signup first
    const url = page.url();
    if (url.includes("/login")) {
      await page.goto("http://localhost:3000/signup");
      await page.fill('input[name="agencyName"]', "E2E Test Agency");
      await page.fill('input[name="agencyEmail"]', "e2e-agency@test.com");
      await page.fill('input[name="name"]', "E2E Test User");
      await page.fill('input[name="email"]', email);
      await page.fill('input[name="password"]', password);
      await page.click('button[type="submit"]');

      // Wait for successful signup redirect
      await page.waitForURL("**/tasks", { timeout: 10000 });
    } else {
      // Wait for login redirect
      await page.waitForURL("**/tasks", { timeout: 10000 });
    }
  });

  test("should display task board with four columns", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Verify all four columns are present
    await expect(page.locator('text="To Do"')).toBeVisible();
    await expect(page.locator('text="In Progress"')).toBeVisible();
    await expect(page.locator('text="In Review"')).toBeVisible();
    await expect(page.locator('text="Done"')).toBeVisible();

    // Verify "New Task" button is present
    await expect(page.locator('button:has-text("New Task")')).toBeVisible();
  });

  test("should create a new task in To Do column", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Click "New Task" button
    await page.click('button:has-text("New Task")');

    // Fill in task details
    await page.fill('input[name="title"]', "E2E Drag Test Task");

    // Submit the form
    await page.click('button[type="submit"]');

    // Wait for task to appear in To Do column
    await expect(page.locator('text="E2E Drag Test Task"')).toBeVisible({ timeout: 5000 });

    // Verify task is in To Do column (first column)
    const todoColumn = page.locator('text="To Do"').locator("..").locator("..");
    await expect(todoColumn.locator('text="E2E Drag Test Task"')).toBeVisible();
  });

  test("should drag task from To Do to In Progress", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Create a test task first
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Drag Me To Progress");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Get the task card
    const taskCard = page.locator('text="Drag Me To Progress"').locator("..");

    // Get source and drop zone positions
    const sourceBox = await taskCard.boundingBox();
    const doingColumn = page.locator('text="In Progress"').locator("..").locator("..");
    const targetBox = await doingColumn.boundingBox();

    if (!sourceBox || !targetBox) {
      throw new Error("Could not get element positions");
    }

    // Perform drag and drop
    await page.mouse.move(sourceBox.x + sourceBox.width / 2, sourceBox.y + sourceBox.height / 2);
    await page.mouse.down();
    await page.waitForTimeout(100);

    // Move to target column
    await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y + targetBox.height / 2, { steps: 10 });
    await page.waitForTimeout(100);
    await page.mouse.up();

    // Wait for API call to complete
    await page.waitForTimeout(1000);

    // Verify task is now in In Progress column
    const doingColumnTasks = doingColumn.locator('text="Drag Me To Progress"');
    await expect(doingColumnTasks).toBeVisible();
  });

  test("should drag task through complete workflow: To Do → In Progress → In Review → Done", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    const taskTitle = "Workflow Test Task";

    // Create task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', taskTitle);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Step 1: Drag from To Do to In Progress
    const taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    const todoBox = await taskCard.boundingBox();
    const doingColumn = page.locator('text="In Progress"').locator("..").locator("..");
    const doingBox = await doingColumn.boundingBox();

    if (todoBox && doingBox) {
      await page.mouse.move(todoBox.x + todoBox.width / 2, todoBox.y + todoBox.height / 2);
      await page.mouse.down();
      await page.waitForTimeout(100);
      await page.mouse.move(doingBox.x + doingBox.width / 2, doingBox.y + doingBox.height / 2, { steps: 10 });
      await page.mouse.up();
      await page.waitForTimeout(1000);
    }

    // Verify in In Progress
    await expect(doingColumn.locator(`text="${taskTitle}"`)).toBeVisible();

    // Step 2: Drag from In Progress to In Review
    const reviewColumn = page.locator('text="In Review"').locator("..").locator("..");
    const reviewBox = await reviewColumn.boundingBox();

    if (doingBox && reviewBox) {
      await page.mouse.move(doingBox.x + doingBox.width / 2, doingBox.y + doingBox.height / 2);
      await page.mouse.down();
      await page.waitForTimeout(100);
      await page.mouse.move(reviewBox.x + reviewBox.width / 2, reviewBox.y + reviewBox.height / 2, { steps: 10 });
      await page.mouse.up();
      await page.waitForTimeout(1000);
    }

    // Verify in In Review
    await expect(reviewColumn.locator(`text="${taskTitle}"`)).toBeVisible();

    // Step 3: Drag from In Review to Done (should trigger confetti)
    const doneColumn = page.locator('text="Done"').locator("..").locator("..");
    const doneBox = await doneColumn.boundingBox();

    if (reviewBox && doneBox) {
      await page.mouse.move(reviewBox.x + reviewBox.width / 2, reviewBox.y + reviewBox.height / 2);
      await page.mouse.down();
      await page.waitForTimeout(100);
      await page.mouse.move(doneBox.x + doneBox.width / 2, doneBox.y + doneBox.height / 2, { steps: 10 });
      await page.mouse.up();
      await page.waitForTimeout(1500); // Extra wait for confetti animation
    }

    // Verify in Done
    await expect(doneColumn.locator(`text="${taskTitle}"`)).toBeVisible();

    // Verify task completion celebration (confetti should have been triggered)
    // Note: Confetti is client-side only, so we verify the task is in Done column
  });

  test("should show drag overlay while dragging", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Create a task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Overlay Test Task");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    const taskCard = page.locator('text="Overlay Test Task"').locator("..");
    const box = await taskCard.boundingBox();

    if (!box) {
      throw new Error("Could not get task card position");
    }

    // Start dragging
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    await page.mouse.down();
    await page.waitForTimeout(200);

    // Check for drag overlay (rotated/scaled element)
    const dragOverlay = page.locator(".rotate-3");
    await expect(dragOverlay).toBeVisible();

    // Drop the element
    await page.mouse.up();
  });

  test("should persist status changes after page refresh", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    const taskTitle = "Persistence Test Task";

    // Create task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', taskTitle);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Move to In Progress
    const taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    const box = await taskCard.boundingBox();
    const doingColumn = page.locator('text="In Progress"').locator("..").locator("..");
    const doingBox = await doingColumn.boundingBox();

    if (box && doingBox) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(doingBox.x + doingBox.width / 2, doingBox.y + doingBox.height / 2, { steps: 10 });
      await page.mouse.up();
    }

    await page.waitForTimeout(1000);

    // Refresh the page
    await page.reload();

    // Wait for tasks to load
    await page.waitForTimeout(2000);

    // Verify task is still in In Progress column
    await expect(doingColumn.locator(`text="${taskTitle}"`)).toBeVisible();
  });

  test("should show loading skeleton while fetching tasks", async ({ page }) => {
    // Intercept the API call to delay response
    await page.route("**/api/v1/tasks", async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      route.continue();
    });

    await page.goto("http://localhost:3000/tasks");

    // Check for loading skeletons (animate-pulse elements)
    await expect(page.locator(".animate-pulse")).toBeVisible();

    // Wait for loading to complete
    await page.waitForSelector(".animate-pulse", { state: "hidden", timeout: 5000 });
  });

  test("should display error message when API fails", async ({ page }) => {
    // Mock API failure
    await page.route("**/api/v1/tasks", (route) => {
      route.abort("failed");
    });

    await page.goto("http://localhost:3000/tasks");

    // Verify error message is displayed
    await expect(page.locator('text="Failed to load tasks"')).toBeVisible();
    await expect(page.locator('text="Please check your connection and try again"')).toBeVisible();
  });
});
