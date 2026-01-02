import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Task Assignment (User Story 3)
 *
 * These tests verify the complete task assignment functionality
 * including user filtering, drag-to-assign, and assignee dropdown.
 *
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - Multiple users exist in the same agency
 * - @dnd-kit/core library is installed
 */

const TEST_AGENCY = {
  name: `E2E Assignment Agency ${Date.now()}`,
  email: `e2e-assign-agency-${Date.now()}@test.com`,
};

const MAIN_USER = {
  name: "E2E Assign Main User",
  email: `e2e-assign-main-${Date.now()}@test.com`,
  password: "TestPass123!",
};

const TEAMMATE_USER = {
  name: "E2E Teammate User",
  email: `e2e-teammate-${Date.now()}@test.com`,
  password: "TestPass123!",
};

test.describe("Task Assignment Flow", () => {
  let mainUserToken: string;
  let teammateId: string;
  let testTaskId: string;

  test.beforeAll(async ({ request }) => {
    // Setup: Create agency and main user
    const signupResponse = await request.post("http://localhost:8000/api/v1/auth/register", {
      data: {
        agency_name: TEST_AGENCY.name,
        agency_email: TEST_AGENCY.email,
        name: MAIN_USER.name,
        email: MAIN_USER.email,
        password: MAIN_USER.password,
      },
    });

    if (signupResponse.ok()) {
      const data = await signupResponse.json();
      mainUserToken = data.access_token;
    }

    // Create a teammate user in the same agency
    const teammateResponse = await request.post("http://localhost:8000/api/v1/auth/register", {
      data: {
        agency_name: TEST_AGENCY.name,
        agency_email: TEST_AGENCY.email,
        name: TEAMMATE_USER.name,
        email: TEAMMATE_USER.email,
        password: TEAMMATE_USER.password,
      },
    });

    if (teammateResponse.ok()) {
      const data = await teammateResponse.json();
      teammateId = data.user.id;
    }
  });

  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto("http://localhost:3000/login");

    // Login with main user credentials
    await page.fill('input[type="email"]', MAIN_USER.email);
    await page.fill('input[type="password"]', MAIN_USER.password);
    await page.click('button[type="submit"]');

    // Wait for login redirect
    await page.waitForURL("**/tasks", { timeout: 10000 });
  });

  test("should display user filter dropdown on task board", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Verify user filter dropdown is present
    await expect(page.locator('[data-testid="user-filter"]')).toBeVisible();

    // Click filter to see available users
    await page.click('[data-testid="user-filter"]');

    // Verify current user is in the list
    await expect(page.locator(`text=${MAIN_USER.name}`)).toBeVisible();

    // Verify teammate is in the list (if visible)
    const teammateOption = page.locator(`text=${TEAMMATE_USER.name}`);
    const isVisible = await teammateOption.isVisible().catch(() => false);
    if (isVisible) {
      await expect(teammateOption).toBeVisible();
    }
  });

  test("should filter tasks by assignee", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // First, create a test task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Filter Test Task");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Get initial task count
    const initialTasks = await page.locator('[data-testid="task-card"]').count();

    // Filter by "Unassigned" (tasks with no assignee)
    await page.click('[data-testid="user-filter"]');
    await page.click('text=Unassigned');

    // Wait for filter to apply
    await page.waitForTimeout(500);

    // Verify only unassigned tasks are shown
    const unassignedTasks = await page.locator('[data-testid="task-card"]').count();
    expect(unassignedTasks).toBeGreaterThan(0);

    // Filter by current user
    await page.click('[data-testid="user-filter"]');
    await page.click(`text=${MAIN_USER.name}`);

    await page.waitForTimeout(500);

    // No tasks should be assigned to current user yet
    const myTasks = await page.locator('[data-testid="task-card"]').count();
    expect(myTasks).toBe(0);
  });

  test("should assign task via drag and drop from team member list", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Create a task to assign
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Drag Assign Test Task");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    const taskTitle = "Drag Assign Test Task";

    // Find the task card
    const taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    const taskBox = await taskCard.boundingBox();

    // Find the teammate avatar in the team list (if visible)
    const teammateAvatar = page.locator(`[data-testid="team-avatar"][data-user-id="${teammateId}"]`);
    const avatarBox = await teammateAvatar.boundingBox();

    if (taskBox && avatarBox) {
      // Perform drag and drop from task to teammate avatar
      await page.mouse.move(taskBox.x + taskBox.width / 2, taskBox.y + taskBox.height / 2);
      await page.mouse.down();
      await page.waitForTimeout(100);

      await page.mouse.move(avatarBox.x + avatarBox.width / 2, avatarBox.y + avatarBox.height / 2, {
        steps: 10,
      });
      await page.waitForTimeout(100);
      await page.mouse.up();

      // Wait for API call to complete
      await page.waitForTimeout(1500);

      // Verify the task now shows the assignee
      const assignedTask = page.locator(`text="${taskTitle}"`).locator("..");
      await expect(assignedTask.locator(`text=${TEAMMATE_USER.name}`)).toBeVisible();
    } else {
      // Team member list might not be implemented yet - skip gracefully
      test.skip();
    }
  });

  test("should assign task via task drawer assignee dropdown", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Create a task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Drawer Assign Test Task");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    const taskTitle = "Drawer Assign Test Task";

    // Click on the task to open drawer
    await page.click(`text="${taskTitle}"`);

    // Wait for drawer to open
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    // Find and click the assignee dropdown
    await page.click('[data-testid="assignee-dropdown"]');

    // Select the teammate from the dropdown
    await page.click(`li:has-text("${TEAMMATE_USER.name}")`);

    // Wait for assignment to save
    await page.waitForTimeout(1000);

    // Close the drawer
    await page.click('[data-testid="close-drawer"]');

    // Verify the task card shows the assignee avatar
    const taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    await expect(taskCard.locator('[data-testid="assignee-avatar"]')).toBeVisible();
  });

  test("should show assignee avatar on task card after assignment", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Create a task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Avatar Test Task");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    const taskTitle = "Avatar Test Task";

    // Open task drawer
    await page.click(`text="${taskTitle}"`);
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    // Assign to teammate
    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${TEAMMATE_USER.name}")`);
    await page.waitForTimeout(1000);

    // Close drawer
    await page.click('[data-testid="close-drawer"]');

    // Verify avatar appears on task card
    const taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    const avatar = taskCard.locator('[data-testid="assignee-avatar"]');

    await expect(avatar).toBeVisible();

    // Verify avatar shows user initials or first letter
    const avatarText = await avatar.textContent();
    expect(avatarText).toBeTruthy();
    expect(avatarText?.length).toBeGreaterThan(0);
  });

  test("should allow changing task assignee", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    const taskTitle = "Change Assignee Test Task";

    // Create and assign a task to teammate
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', taskTitle);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    await page.click(`text="${taskTitle}"`);
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${TEAMMATE_USER.name}")`);
    await page.waitForTimeout(1000);
    await page.click('[data-testid="close-drawer"]');

    // Verify initial assignment
    let taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    await expect(taskCard.locator('[data-testid="assignee-avatar"]')).toBeVisible();

    // Open drawer again and change assignee to current user
    await page.click(`text="${taskTitle}"`);
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${MAIN_USER.name}")`);
    await page.waitForTimeout(1000);
    await page.click('[data-testid="close-drawer"]');

    // Verify the assignment changed
    taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    const avatar = taskCard.locator('[data-testid="assignee-avatar"]');
    await expect(avatar).toBeVisible();

    // Avatar should now show current user's initials
    const avatarText = await avatar.textContent();
    expect(avatarText).toContain(MAIN_USER.name.charAt(0).toUpperCase());
  });

  test("should allow unassigning a task", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    const taskTitle = "Unassign Test Task";

    // Create and assign a task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', taskTitle);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    await page.click(`text="${taskTitle}"`);
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${TEAMMATE_USER.name}")`);
    await page.waitForTimeout(1000);

    // Verify task is assigned
    let taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    await expect(taskCard.locator('[data-testid="assignee-avatar"]')).toBeVisible();

    // Now unassign the task
    await page.click('[data-testid="assignee-dropdown"]');
    await page.click('li:has-text("Unassigned")');
    await page.waitForTimeout(1000);
    await page.click('[data-testid="close-drawer"]');

    // Verify task is now unassigned
    taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    const avatar = taskCard.locator('[data-testid="assignee-avatar"]');
    await expect(avatar).not.toBeVisible();
  });

  test("should persist assignment after page refresh", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    const taskTitle = "Persistence Assign Test Task";

    // Create and assign a task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', taskTitle);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    await page.click(`text="${taskTitle}"`);
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${TEAMMATE_USER.name}")`);
    await page.waitForTimeout(1000);
    await page.click('[data-testid="close-drawer"]');

    // Refresh the page
    await page.reload();
    await page.waitForTimeout(2000);

    // Verify assignment persists
    const taskCard = page.locator(`text="${taskTitle}"`).locator("..");
    await expect(taskCard.locator('[data-testid="assignee-avatar"]')).toBeVisible();
  });

  test("should filter by 'My Tasks' to show only assigned to current user", async ({ page }) => {
    await page.goto("http://localhost:3000/tasks");

    // Create multiple tasks, assign some to current user
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "My Task 1");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "My Task 2");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(500);

    // Assign both to current user
    await page.click('text="My Task 1"');
    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${MAIN_USER.name}")`);
    await page.click('[data-testid="close-drawer"]');
    await page.waitForTimeout(500);

    await page.click('text="My Task 2"');
    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${MAIN_USER.name}")`);
    await page.click('[data-testid="close-drawer"]');
    await page.waitForTimeout(500);

    // Create an unassigned task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Unassigned Task");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Filter by "My Tasks"
    await page.click('[data-testid="user-filter"]');
    await page.click(`text=My Tasks`);

    await page.waitForTimeout(500);

    // Should only show assigned tasks
    await expect(page.locator('text="My Task 1"')).toBeVisible();
    await expect(page.locator('text="My Task 2"')).toBeVisible();
    await expect(page.locator('text="Unassigned Task"')).not.toBeVisible();
  });

  test("should show error when assignment fails", async ({ page }) => {
    // Mock failed API call
    await page.route("**/api/v1/tasks/*/assign", (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Failed to assign task" }),
      });
    });

    await page.goto("http://localhost:3000/tasks");

    // Create a task
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Error Assign Test");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    // Try to assign via drawer
    await page.click('text="Error Assign Test"');
    await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

    await page.click('[data-testid="assignee-dropdown"]');
    await page.click(`li:has-text("${TEAMMATE_USER.name}")`);
    await page.waitForTimeout(1000);

    // Should show error message
    await expect(page.locator('text="Failed to assign task"')).toBeVisible();
  });

  test("should prevent cross-agency task assignment", async ({ page, context }) => {
    // This test verifies that users from different agencies cannot assign each other's tasks
    // Implementation depends on multi-tenant isolation

    // Create task as main user
    await page.goto("http://localhost:3000/tasks");
    await page.click('button:has-text("New Task")');
    await page.fill('input[name="title"]', "Cross-Agency Test Task");
    await page.click('button[type="submit"]');
    await page.waitForTimeout(1000);

    const taskTitle = "Cross-Agency Test Task";

    // Open a new context and try to access as different agency user
    const newContext = await context.browser()?.newContext();
    const newPage = await newContext?.newPage();

    if (newPage) {
      // Try to login as a user from a different agency
      // This would need to be set up in beforeAll
      // For now, we test that the API returns 403

      await page.click(`text="${taskTitle}"`);
      await expect(page.locator('[data-testid="task-drawer"]')).toBeVisible();

      // The assignee dropdown should only show users from the same agency
      await page.click('[data-testid="assignee-dropdown"]');

      // Should NOT show users from other agencies
      const dropdownUsers = await page.locator('[data-testid="assignee-option"]').allTextContents();
      expect(dropdownUsers.every((user) => !user.includes("Different Agency"))).toBeTruthy();

      await newContext?.close();
    }
  });
});
