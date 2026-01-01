/**
 * E2E tests for authentication flow.
 *
 * These tests verify the complete signup and login flow
 * from the user's perspective using Playwright.
 */
import { test, expect } from '@playwright/test';

const TEST_AGENCY = {
  name: 'E2E Test Agency',
  email: `e2e-${Date.now()}@test.com`,
};

const TEST_USER = {
  name: 'E2E Test User',
  email: `e2e-user-${Date.now()}@test.com`,
  password: 'e2eTestPassword123',
};

test.describe('Authentication Flow', () => {
  test('should signup a new agency and user', async ({ page }) => {
    // Navigate to signup page
    await page.goto('/signup');

    // Fill agency information
    await page.fill('input[name="agencyName"]', TEST_AGENCY.name);
    await page.fill('input[name="agencyEmail"]', TEST_AGENCY.email);

    // Fill user information
    await page.fill('input[name="name"]', TEST_USER.name);
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.fill('input[name="confirmPassword"]', TEST_USER.password);

    // Submit form
    await page.click('button[type="submit"]');

    // Should redirect to dashboard after successful signup
    await page.waitForURL('/dashboard');
    await expect(page).toHaveURL('/dashboard');

    // Verify user is logged in (dashboard should have user info)
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    // First create a user (in a real app, this would be done via API)
    // For E2E testing, we'd typically use a test account

    // Navigate to login page
    await page.goto('/login');

    // Fill login form
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);

    // Submit form
    await page.click('button[type="submit"]');

    // Should redirect to dashboard after successful login
    await page.waitForURL('/dashboard');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should show error with invalid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');

    // Fill with invalid credentials
    await page.fill('input[name="email"]', 'invalid@test.com');
    await page.fill('input[name="password"]', 'wrongpassword');

    // Submit form
    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.locator('text=Invalid email or password')).toBeVisible();
  });

  test('should logout and redirect to home', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');

    // Click logout button (implementation dependent)
    await page.click('button:has-text("Logout")');

    // Should redirect to home page
    await page.waitForURL('/');
    await expect(page).toHaveURL('/');

    // Verify token is cleared
    const cookies = await page.context().cookies();
    const accessToken = cookies.find((c) => c.name === 'access_token');
    expect(accessToken).toBeUndefined();
  });

  test('should protect dashboard route when not logged in', async ({ page }) => {
    // Try to access dashboard directly
    await page.goto('/dashboard');

    // Should redirect to login page
    await page.waitForURL('/login');
    await expect(page).toHaveURL('/login');
  });

  test('should validate password requirements on signup', async ({ page }) => {
    await page.goto('/signup');

    // Fill agency info
    await page.fill('input[name="agencyName"]', TEST_AGENCY.name);
    await page.fill('input[name="agencyEmail"]', `validate-${Date.now()}@test.com`);

    // Fill user info with weak password
    await page.fill('input[name="name"]', TEST_USER.name);
    await page.fill('input[name="email"]', `validate-${Date.now()}@test.com`);
    await page.fill('input[name="password"]', '123'); // Too short

    // Submit form
    await page.click('button[type="submit"]');

    // Should show validation error
    await expect(page.locator('text=Password must be at least 8 characters')).toBeVisible();
  });

  test('should validate email format on signup', async ({ page }) => {
    await page.goto('/signup');

    // Fill with invalid email
    await page.fill('input[name="agencyEmail"]', 'not-an-email');

    // Should show validation error
    await expect(page.locator('input[name="agencyEmail"]')).toHaveAttribute(
      'aria-invalid',
      'true'
    );
  });
});
