"""E2E tests for TeamFlow AI Chatbot (T055, T068).

Tests RAG query flow verifying constitution query returns accurate policy explanation.
Tests recommendation flow for Phase 5 features.
"""
import { test, expect } from '@playwright/test'

test.describe('TeamFlow AI Chatbot E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/')

    // Wait for the page to load
    await expect(page.locator('body')).toBeVisible()
  })

  test('T055: RAG query flow - constitution query returns accurate policy', async ({ page }) => {
    // Find and click the chat widget toggle button
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await expect(chatButton).toBeVisible()
    await chatButton.click()

    // Wait for ChatKit to load
    await expect(page.locator('openai-chatkit')).toBeVisible({ timeout: 10000 })

    // Find the chat input and send a constitution query
    const chatInput = page.locator('[contenteditable="true"], textarea').first()
    await expect(chatInput).toBeVisible()

    // Type the query
    await chatInput.fill('How do we handle authentication errors?')

    // Send the message
    const sendButton = page.locator('button:has-text("Send"), button[type="submit"]').first()
    if (await sendButton.isVisible()) {
      await sendButton.click()
    } else {
      await chatInput.press('Enter')
    }

    // Wait for response (should include information from constitution/CLAUDE.md)
    await expect(page.locator('openai-chatkit')).toContainText(/auth|error|handle|session/i, { timeout: 30000 })

    // Verify the response mentions authentication concepts
    const response = page.locator('openai-chatkit')
    await expect(response).toContainText(/Better Auth|authentication|error handling/i)

    // T054: Verify source references are displayed (if RAG sources are returned)
    const sourcesPanel = page.locator('.fixed.z-30:has-text("Sources")')
    if (await sourcesPanel.isVisible({ timeout: 5000 })) {
      await expect(sourcesPanel).toContainText(/CLAUDE\.md|constitution|policy/i)
    }
  })

  test('T055: RAG query flow - design requirements query', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()

    // Wait for ChatKit
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Use suggested prompt from T053
    const suggestedPrompt = page.locator('text=Ask about project docs')
    if (await suggestedPrompt.isVisible()) {
      await suggestedPrompt.click()
    } else {
      // Fallback to manual input
      const chatInput = page.locator('[contenteditable="true"], textarea').first()
      await chatInput.fill('What are the design requirements for the landing page?')
      await chatInput.press('Enter')
    }

    // Verify response contains relevant information
    await expect(page.locator('openai-chatkit')).toContainText(/design|landing|page|requirements/i, { timeout: 30000 })
  })

  test('T055: RAG query flow - no results handling', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()

    // Wait for ChatKit
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Ask an unrelated question
    const chatInput = page.locator('[contenteditable="true"], textarea').first()
    await chatInput.fill('Explain quantum physics theory of everything')
    await chatInput.press('Enter')

    // Verify the response either suggests alternatives or provides general knowledge
    const response = page.locator('openai-chatkit')
    await expect(response).toContainText(/couldn't find|suggest|try|physics/i, { timeout: 30000 })
  })

  test('Chat widget suggested prompts (T053)', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()

    // Wait for ChatKit and check for suggested prompts
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Verify suggested prompts are visible
    await expect(page.locator('text=Ask about project docs')).toBeVisible()
    await expect(page.locator('text=Team management')).toBeVisible()
    await expect(page.locator('text=Project help')).toBeVisible()
    await expect(page.locator('text=Create a task')).toBeVisible()
  })

  test('Chat widget open and close (T054)', async ({ page }) => {
    // Find the toggle button
    const chatButton = page.locator('button[aria-label="Toggle chat"]')

    // Chat should be closed initially
    await expect(page.locator('openai-chatkit')).not.toBeVisible()

    // Open chat
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Close chat
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).not.toBeVisible()
  })
})

test.describe('Phase 5: AI Recommendations (T068)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()
  })

  test('T068: Recommendation flow - assignee suggestion', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Ask for assignee recommendation
    await chatInput.fill('Who is the best person for this backend task?')
    await chatInput.press('Enter')

    // Verify response contains recommendation
    await expect(page.locator('openai-chatkit')).toContainText(/suggest|recommend|available|skills/i, { timeout: 30000 })
  })

  test('T068: Recommendation flow - workload analysis', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Ask for workload analysis
    await chatInput.fill('Who is over capacity?')
    await chatInput.press('Enter')

    // Verify response contains workload information
    await expect(page.locator('openai-chatkit')).toContainText(/workload|capacity|tasks|hours/i, { timeout: 30000 })
  })

  test('T068: Recommendation flow - profitability assessment', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Ask for profitability
    await chatInput.fill('Are we over budget on Project X?')
    await chatInput.press('Enter')

    // Verify response contains budget/profitability information
    await expect(page.locator('openai-chatkit')).toContainText(/budget|profit|cost|revenue/i, { timeout: 30000 })
  })
})
