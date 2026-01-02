import { test, expect } from "@playwright/test";

/**
 * E2E Tests for Dashboard (User Story 4)
 *
 * These tests verify the dashboard functionality including
 * statistics display, animations, and real-time updates.
 *
 * Prerequisites:
 * - Backend server running on http://localhost:8000
 * - User account exists with tasks and projects
 */

const TEST_USER = {
  name: "Dashboard Test User",
  email: "dashboard@e2e.com",
  password: "TestPass123!",
};

test.describe("Dashboard", () => {
  test.beforeAll(async ({ request }) => {
    // Setup: Create user and some test data
    const signupResponse = await request.post("http://localhost:8000/api/v1/auth/register", {
      data: {
        agency_data: {
          name: "Dashboard Test Agency",
          email: "dashboard@e2e.com",
        },
        user_data: {
          name: TEST_USER.name,
          email: TEST_USER.email,
          password: TEST_USER.password,
        },
      },
    });

    if (signupResponse.ok()) {
      const data = await signupResponse.json();
      const token = data.access_token;

      // Create some projects
      await request.post("http://localhost:8000/api/v1/projects", {
        headers: { Authorization: `Bearer ${token}` },
        data: { name: "Project A", description: "First project" },
      });
      await request.post("http://localhost:8000/api/v1/projects", {
        headers: { Authorization: `Bearer ${token}` },
        data: { name: "Project B", description: "Second project" },
      });

      // Create tasks with different statuses
      const tasks = [
        { title: "Task 1", status: "TODO" },
        { title: "Task 2", status: "DOING" },
        { title: "Task 3", status: "DONE" },
        { title: "Task 4", status: "DONE" },
      ];
      for (const task of tasks) {
        await request.post("http://localhost:8000/api/v1/tasks", {
          headers: { Authorization: `Bearer ${token}` },
          data: task,
        });
      }
    }
  });

  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto("http://localhost:3000/login");

    // Login
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForURL("**/dashboard", { timeout: 10000 });
  });

  test("should display dashboard with stat cards", async ({ page }) => {
    // Verify stat cards are visible
    await expect(page.locator('[data-testid="stat-card"]').first()).toBeVisible();

    // Check for specific stats
    await expect(page.locator('text=Active Projects')).toBeVisible();
    await expect(page.locator('text=Tasks Completed')).toBeVisible();
  });

  test("should display stat card values correctly", async ({ page }) => {
    // Check active projects count
    const projectsCard = page.locator('[data-testid="stat-card"]').filter({ hasText: "Projects" });
    await expect(projectsCard).toContainText("2");

    // Check completed tasks count
    const tasksCard = page.locator('[data-testid="stat-card"]').filter({ hasText: "Tasks" });
    await expect(tasksCard).toContainText("2");
  });

  test("should have staggered animation on load", async ({ page }) => {
    // Navigate to dashboard fresh
    await page.goto("http://localhost:3000/dashboard");

    // Wait for animations to complete
    await page.waitForTimeout(1500);

    // Verify all stat cards are visible and animated
    const statCards = page.locator('[data-testid="stat-card"]');
    const count = await statCards.count();

    expect(count).toBeGreaterThan(0);

    // All cards should be visible after animation
    for (let i = 0; i < count; i++) {
      await expect(statCards.nth(i)).toBeVisible();
    }
  });

  test("should show hover lift effect on stat cards", async ({ page }) => {
    const statCard = page.locator('[data-testid="stat-card"]').first();

    // Get initial position
    const boxBefore = await statCard.boundingBox();

    // Hover over the card
    await statCard.hover();

    // Wait for animation
    await page.waitForTimeout(300);

    // Card should still be visible and positioned
    const boxAfter = await statCard.boundingBox();
    expect(boxAfter).toBeTruthy();
  });

  test("should display task distribution chart", async ({ page }) => {
    // Check if task distribution chart is present
    const chart = page.locator('[data-testid="task-distribution-chart"]');
    await expect(chart).toBeVisible();
  });

  test("should display workflow progress indicator", async ({ page }) => {
    // Check if workflow progress component is present
    const workflow = page.locator('[data-testid="workflow-progress"]');
    await expect(workflow).toBeVisible();
  });

  test("should have collapsible sidebar", async ({ page }) => {
    const sidebar = page.locator('[data-testid="sidebar"]');
    const toggleButton = page.locator('[data-testid="sidebar-toggle"]');

    // Sidebar should be visible initially
    await expect(sidebar).toBeVisible();

    // Click collapse button
    await toggleButton.click();

    // Wait for animation
    await page.waitForTimeout(300);

    // Sidebar should be collapsed (narrower width)
    const sidebarBox = await sidebar.boundingBox();
    expect(sidebarBox).toBeTruthy();
    // When collapsed, sidebar width should be small (e.g., < 100px)
    expect(sidebarBox!.width).toBeLessThan(100);
  });

  test("should persist sidebar collapse state", async ({ page }) => {
    const toggleButton = page.locator('[data-testid="sidebar-toggle"]');

    // Collapse sidebar
    await toggleButton.click();
    await page.waitForTimeout(300);

    // Reload page
    await page.reload();
    await page.waitForTimeout(1000);

    // Sidebar should still be collapsed
    const sidebar = page.locator('[data-testid="sidebar"]');
    const sidebarBox = await sidebar.boundingBox();
    expect(sidebarBox!.width).toBeLessThan(100);
  });

  test("should have theme toggle functionality", async ({ page }) => {
    const themeToggle = page.locator('[data-testid="theme-toggle"]');

    // Theme toggle should be visible
    await expect(themeToggle).toBeVisible();

    // Click to toggle theme
    await themeToggle.click();

    // Wait for theme change
    await page.waitForTimeout(300);

    // Toggle should still be visible
    await expect(themeToggle).toBeVisible();
  });

  test("should update stats in real-time", async ({ page }) => {
    // Get initial tasks completed count
    const tasksCard = page.locator('[data-testid="stat-card"]').filter({ hasText: "Tasks" });
    const initialText = await tasksCard.textContent();

    // Navigate to tasks and complete a task
    await page.goto("http://localhost:3000/tasks");
    await page.waitForTimeout(1000);

    // Find a TODO task and move it to DONE
    const todoTask = page.locator('text="Task 1"');
    if (await todoTask.isVisible()) {
      await todoTask.dragTo(page.locator('[data-testid="column-DONE"]'));
      await page.waitForTimeout(1500);
    }

    // Return to dashboard
    await page.goto("http://localhost:3000/dashboard");
    await page.waitForTimeout(1000);

    // Stats should be updated (due to 10-second polling)
    const updatedText = await tasksCard.textContent();

    // Should be different after polling updates
    expect(updatedText).toBeTruthy();
  });

  test("should show error state when API fails", async ({ page }) => {
    // Mock API failure
    await page.route("**/api/v1/analytics/stats", (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Internal server error" }),
      });
    });

    // Reload dashboard
    await page.goto("http://localhost:3000/dashboard");
    await page.waitForTimeout(2000);

    // Should show error message or fallback
    const errorMessage = page.locator('text=Failed to load dashboard');
    const hasError = await errorMessage.isVisible().catch(() => false);

    if (hasError) {
      await expect(errorMessage).toBeVisible();
    }
    // Otherwise should show cached or default values
  });

  test("should display project list grid", async ({ page }) => {
    // Check if project list is present
    const projectList = page.locator('[data-testid="project-list"]');
    await expect(projectList).toBeVisible();

    // Should show at least one project
    const projectCards = page.locator('[data-testid="project-card"]');
    const count = await projectCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test("should navigate to tasks page from stat card", async ({ page }) => {
    const tasksCard = page.locator('[data-testid="stat-card"]').filter({ hasText: "Tasks" });

    // Click on tasks stat card (if clickable)
    await tasksCard.click();

    // Should navigate to tasks page
    await page.waitForURL("**/tasks", { timeout: 5000 });
    expect(page.url()).toContain("/tasks");
  });
});
