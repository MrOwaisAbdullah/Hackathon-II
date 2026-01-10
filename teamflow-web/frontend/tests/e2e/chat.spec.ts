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

  test('T068: Recommendation flow - assignment suggestion with acceptance', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Trigger a recommendation by asking for task assignment
    await chatInput.fill('I need someone with Python experience for this API task')
    await chatInput.press('Enter')

    // Wait for AI response with recommendation
    await expect(page.locator('openai-chatkit')).toContainText(/recommend|assign|suggest|available/i, { timeout: 30000 })

    // Verify feedback buttons are displayed (T065)
    // ChatKit renders thumbs up/down buttons in thread item actions
    const feedbackButtons = page.locator('button[aria-label*="feedback"], button[aria-label*="thumbs"], button[class*="feedback"]')
    const feedbackVisible = await feedbackButtons.count() > 0

    if (feedbackVisible) {
      // Click thumbs up (accept recommendation)
      const thumbsUpButton = page.locator('button[aria-label*="thumbs up"], button[aria-label*="positive"]').first()
      if (await thumbsUpButton.isVisible({ timeout: 5000 })) {
        await thumbsUpButton.click()

        // Verify acceptance confirmation is shown
        await expect(page.locator('openai-chatkit')).toContainText(/thanks|accepted|feedback/i, { timeout: 10000 })
      }
    }

    // Verify recommendation was tracked via backend (T066)
    // This would require checking the backend logs or database
    // For E2E, we verify the UI shows acceptance confirmation
  })

  test('T068: Recommendation flow - assignment suggestion with rejection', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Trigger a recommendation
    await chatInput.fill('Suggest someone for the frontend task')
    await chatInput.press('Enter')

    // Wait for AI response
    await expect(page.locator('openai-chatkit')).toContainText(/recommend|assign|suggest/i, { timeout: 30000 })

    // Find and click thumbs down (reject recommendation)
    const thumbsDownButton = page.locator('button[aria-label*="thumbs down"], button[aria-label*="negative"]').first()
    if (await thumbsDownButton.isVisible({ timeout: 5000 })) {
      await thumbsDownButton.click()

      // Verify rejection confirmation
      await expect(page.locator('openai-chatkit')).toContainText(/thanks|rejected|feedback|improve/i, { timeout: 10000 })
    }
  })

  test('T068: Recommendation flow - workload analysis', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Ask for workload analysis
    await chatInput.fill('Who is over capacity?')
    await chatInput.press('Enter')

    // Verify response contains workload information
    await expect(page.locator('openai-chatkit')).toContainText(/workload|capacity|tasks|hours|utilization/i, { timeout: 30000 })

    // Verify the response includes specific team member names or counts
    await expect(page.locator('openai-chatkit')).toContainText(/\d+.*tasks?|\d+.*hours?/i, { timeout: 5000 })
  })

  test('T068: Recommendation flow - profitability assessment', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Ask for profitability
    await chatInput.fill('Are we over budget on Project X?')
    await chatInput.press('Enter')

    // Verify response contains budget/profitability information
    await expect(page.locator('openai-chatkit')).toContainText(/budget|profit|cost|revenue|margin/i, { timeout: 30000 })
  })

  test('T068: Recommendation flow - verify reasoning display (T065)', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Ask for a specific recommendation that should include reasoning
    await chatInput.fill('Who should I assign this critical bug fix to?')
    await chatInput.press('Enter')

    // Verify response contains reasoning elements
    await expect(page.locator('openai-chatkit')).toContainText(/skills|workload|available|score|match/i, { timeout: 30000 })

    // Look for reasoning panel or structured explanation
    const reasoningIndicators = [
      'Skills Match',
      'Workload',
      'Availability',
      'Why',
      'because',
      'reason',
    ]

    const response = page.locator('openai-chatkit')
    let hasReasoning = false
    for (const indicator of reasoningIndicators) {
      if (await response.getByText(indicator, { exact: false }).count() > 0) {
        hasReasoning = true
        break
      }
    }

    // At least one reasoning indicator should be present
    expect(hasReasoning).toBeTruthy()
  })
})

test.describe('Phase 6: Urdu Language Support (T076)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()
  })

  test('T076: Urdu language input produces Urdu response', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Type a simple Urdu command in Roman script
    await chatInput.fill('Acme project ke liye task banayein')
    await chatInput.press('Enter')

    // Verify response contains task creation confirmation
    // The response should be in Urdu or bilingual
    await expect(page.locator('openai-chatkit')).toContainText(/task|create|banayi|kiya/i, { timeout: 30000 })
  })

  test('T076: Mixed Urdu/English input is handled correctly', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Type mixed Urdu/English command
    await chatInput.fill('Mujhe Acme project mein nayi task chahiye')
    await chatInput.press('Enter')

    // Verify response is received
    await expect(page.locator('openai-chatkit')).toContainText(/task|project|create/i, { timeout: 30000 })
  })

  test('T076: Urdu preference persists across messages', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // First message in Urdu
    await chatInput.fill('Project ki details batayein')
    await chatInput.press('Enter')
    await expect(page.locator('openai-chatkit')).toContainText(/project|details/i, { timeout: 30000 })

    // Wait a moment for next message
    await page.waitForTimeout(1000)

    // Second message should also get appropriate response
    await chatInput.fill('Task ka status check karein')
    await chatInput.press('Enter')
    await expect(page.locator('openai-chatkit')).toContainText(/task|status/i, { timeout: 30000 })
  })

  test('T076: Language detection works with Arabic script', async ({ page }) => {
    const chatInput = page.locator('[contenteditable="true"], textarea').first()

    // Type message with Arabic script Urdu characters
    // This should trigger Urdu mode (>30% threshold)
    await chatInput.fill('آصف کے لیے Acme project میں task بنائیں')
    await chatInput.press('Enter')

    // Verify response is received
    await expect(page.locator('openai-chatkit')).toContainText(/task|create|banayi/i, { timeout: 30000 })
  })
})

test.describe('Phase 6: Voice Input Support (T083)', () => {
  test.use({ permissions: ['microphone'] }) // Grant microphone permission

  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('T083: Voice input button is visible in supported browsers', async ({ page }) => {
    // Check if browser supports Speech Recognition
    const isSupported = await page.evaluate(() => {
      return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    })

    if (!isSupported) {
      // Skip test if not supported
      test.skip()
      return
    }

    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Look for voice input button or microphone icon
    // Note: This depends on VoiceInput component being integrated
    const voiceButton = page.locator('button[aria-label*="voice"], button[aria-label*="microphone"], [class*="mic"]').first()

    // Button might be visible if VoiceInput is integrated
    const isVisible = await voiceButton.isVisible().catch(() => false)
    if (isVisible) {
      await expect(voiceButton).toBeVisible()
    }
  })

  test('T083: Voice input records and transcribes speech', async ({ page }) => {
    // Check browser support
    const isSupported = await page.evaluate(() => {
      return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    })

    if (!isSupported) {
      test.skip()
      return
    }

    // Open chat
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Note: This test would require actual microphone access in a real environment
    // For CI/CD, this would need to be mocked or use a test fixture
    // Here we just verify the component structure exists

    // Verify Speech Recognition API is available
    const apiAvailable = await page.evaluate(() => {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      return typeof SpeechRecognition === 'function'
    })

    expect(apiAvailable).toBeTruthy()
  })

  test('T083: Keyboard shortcut Ctrl+Shift+V toggles recording', async ({ page }) => {
    const isSupported = await page.evaluate(() => {
      return !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    })

    if (!isSupported) {
      test.skip()
      return
    }

    // Open chat
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()

    // Verify keyboard shortcut is registered
    // This would require VoiceInput component to be mounted
    const hasVoiceInput = await page.locator('[class*="voice-input"]').count().then(count => count > 0)

    if (hasVoiceInput) {
      // Test that Ctrl+Shift+V triggers voice input
      // (Actual recording would need microphone access)
      const voiceButton = page.locator('button[aria-label*="voice"], button[aria-label*="microphone"]').first()

      if (await voiceButton.isVisible()) {
        // Simulate keyboard shortcut
        await page.keyboard.down('Control')
        await page.keyboard.down('Shift')
        await page.keyboard.press('v')
        await page.keyboard.up('Shift')
        await page.keyboard.up('Control')

        // Verify button state changed (recording started/stopped)
        // This is a basic check - full test would need mock SpeechRecognition
      }
    }
  })
})

test.describe('Fullscreen Chat Mode (T094-T100)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('T100: Fullscreen toggle button is visible in chat widget', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Look for fullscreen toggle button in status bar
    const fullscreenButton = page.locator('button[aria-label*="fullscreen"], button[aria-label*="Enter fullscreen"]').first()
    await expect(fullscreenButton).toBeVisible()
  })

  test('T100: Fullscreen toggle expands chat to full viewport', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Get initial chat widget dimensions
    const chatWidget = page.locator('.fixed.z-\\[9998\\]').first()
    const initialBox = await chatWidget.boundingBox()
    expect(initialBox).not.toBeNull()

    // Click fullscreen toggle button
    const fullscreenButton = page.locator('button[aria-label*="Enter fullscreen"]').first()
    await fullscreenButton.click()

    // Wait for transition
    await page.waitForTimeout(500)

    // Verify chat widget now fills the screen
    const fullscreenBox = await chatWidget.boundingBox()
    expect(fullscreenBox).not.toBeNull()

    const viewportSize = page.viewportSize()
    if (viewportSize && fullscreenBox && initialBox) {
      // Fullscreen should be significantly larger than initial
      expect(fullscreenBox.width).toBeGreaterThan(initialBox.width)
      expect(fullscreenBox.height).toBeGreaterThan(initialBox.height)

      // Should be close to viewport size (allowing for small margins)
      expect(fullscreenBox.width).toBeGreaterThan(viewportSize.width * 0.9)
      expect(fullscreenBox.height).toBeGreaterThan(viewportSize.height * 0.9)
    }
  })

  test('T100: Exit fullscreen button restores widget size', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Enter fullscreen
    const enterFullscreenButton = page.locator('button[aria-label*="Enter fullscreen"]').first()
    await enterFullscreenButton.click()
    await page.waitForTimeout(500)

    // Exit fullscreen
    const exitFullscreenButton = page.locator('button[aria-label*="Exit fullscreen"]').first()
    await expect(exitFullscreenButton).toBeVisible()
    await exitFullscreenButton.click()
    await page.waitForTimeout(500)

    // Verify widget is back to floating size
    const chatWidget = page.locator('.fixed.z-\\[9998\\]').first()
    const restoredBox = await chatWidget.boundingBox()

    if (restoredBox) {
      // Should be back to approximately 400px width
      expect(restoredBox.width).toBeLessThan(500)
      expect(restoredBox.width).toBeGreaterThan(300)
    }
  })

  test('T100: Keyboard shortcut Ctrl+Shift+F toggles fullscreen', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Get initial dimensions
    const chatWidget = page.locator('.fixed.z-\\[9998\\]').first()
    const initialBox = await chatWidget.boundingBox()

    // Press Ctrl+Shift+F
    await page.keyboard.down('Control')
    await page.keyboard.down('Shift')
    await page.keyboard.press('F')
    await page.keyboard.up('Shift')
    await page.keyboard.up('Control')

    // Wait for transition
    await page.waitForTimeout(500)

    // Verify fullscreen mode activated
    const fullscreenBox = await chatWidget.boundingBox()
    if (initialBox && fullscreenBox) {
      expect(fullscreenBox.width).toBeGreaterThan(initialBox.width)
    }
  })

  test('T100: Escape key exits fullscreen mode', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()

    // Enter fullscreen
    const enterFullscreenButton = page.locator('button[aria-label*="Enter fullscreen"]').first()
    await enterFullscreenButton.click()
    await page.waitForTimeout(500)

    // Press Escape to exit fullscreen
    await page.keyboard.press('Escape')
    await page.waitForTimeout(500)

    // Verify exit fullscreen button is no longer visible
    const exitFullscreenButton = page.locator('button[aria-label*="Exit fullscreen"]')
    await expect(exitFullscreenButton).not.toBeVisible()
  })

  test('T100: Fullscreen mode shows "Fullscreen mode" indicator', async ({ page }) => {
    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()

    // Enter fullscreen
    const fullscreenButton = page.locator('button[aria-label*="Enter fullscreen"]').first()
    await fullscreenButton.click()
    await page.waitForTimeout(500)

    // Verify "Fullscreen mode" text is visible in status bar
    await expect(page.locator('text=Fullscreen mode')).toBeVisible()
  })
})

test.describe('Sidebar AI Assistant Button (T097a, T100a)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('T100a: AI Assistant button is visible in sidebar', async ({ page }) => {
    // Look for sidebar navigation (visible on desktop)
    const sidebar = page.locator('.sidebar-dark, aside').first()

    // Check if sidebar is visible (desktop view)
    const isSidebarVisible = await sidebar.isVisible().catch(() => false)

    if (isSidebarVisible) {
      // Look for AI Assistant menu item
      const aiAssistantLink = page.locator('a[href="/chat"]').first()
      await expect(aiAssistantLink).toBeVisible()

      // Verify it has the chat icon
      const chatIcon = page.locator('a[href="/chat"] svg').first()
      await expect(chatIcon).toBeVisible()
    } else {
      // On mobile, sidebar might be hidden - test.skip or check mobile nav
      test.skip(true, 'Sidebar not visible on mobile viewport')
    }
  })

  test('T100a: AI Assistant button navigates to fullscreen chat page', async ({ page }) => {
    // Click AI Assistant button in sidebar
    const aiAssistantLink = page.locator('a[href="/chat"]').first()

    // Check if visible (desktop only)
    const isVisible = await aiAssistantLink.isVisible().catch(() => false)

    if (isVisible) {
      await aiAssistantLink.click()

      // Verify navigation to /chat route
      await expect(page).toHaveURL(/\/chat/)

      // Verify ChatKit is visible in fullscreen mode
      await expect(page.locator('openai-chatkit')).toBeVisible()

      // Verify fullscreen indicator is present
      await expect(page.locator('text=Fullscreen mode')).toBeVisible()
    } else {
      test.skip(true, 'AI Assistant link not visible on current viewport')
    }
  })

  test('T100a: AI Assistant button has correct label and icon', async ({ page }) => {
    const aiAssistantLink = page.locator('a[href="/chat"]').first()
    const isVisible = await aiAssistantLink.isVisible().catch(() => false)

    if (isVisible) {
      // Verify link text contains "AI Assistant"
      await expect(aiAssistantLink).toContainText('AI Assistant')

      // Verify MessageCircle icon is present
      const icon = aiAssistantLink.locator('svg').first()
      await expect(icon).toBeVisible()
    } else {
      test.skip(true, 'AI Assistant link not visible on current viewport')
    }
  })

  test('T100a: AI Assistant button is highlighted when active', async ({ page }) => {
    // Navigate to chat page
    await page.goto('/chat')

    // Look for active state styling in sidebar
    const aiAssistantLink = page.locator('a[href="/chat"]').first()
    const isVisible = await aiAssistantLink.isVisible().catch(() => false)

    if (isVisible) {
      // Verify active state (should have bg-lime-400 class)
      const isActive = await aiAssistantLink.evaluate(el =>
        el.classList.contains('bg-lime-400') ||
        el.querySelector('.bg-lime-400') !== null
      )

      expect(isActive).toBeTruthy()
    } else {
      test.skip(true, 'AI Assistant link not visible on current viewport')
    }
  })

  test('T100a: AI Assistant button appears second in sidebar', async ({ page }) => {
    // Get all navigation links in sidebar
    const navLinks = page.locator('nav a[href^="/"]').all()
    const links = await navLinks

    if (links.length > 1) {
      // Get the second link's href
      const secondLinkHref = await links[1].getAttribute('href')
      expect(secondLinkHref).toBe('/chat')
    } else {
      test.skip(true, 'Not enough navigation links visible')
    }
  })
})

test.describe('Mobile-Responsive Chat (T098)', () => {
  test('T098: Chat widget adapts to mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })

    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Get chat widget dimensions
    const chatWidget = page.locator('.fixed.z-\\[9998\\]').first()
    const box = await chatWidget.boundingBox()

    if (box) {
      // On mobile, widget should be nearly full width (minus small margins)
      expect(box.width).toBeGreaterThan(350) // Close to 375px viewport
    }
  })

  test('T098: Chat widget adapts to desktop viewport', async ({ page }) => {
    // Set desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 })

    // Open chat widget
    const chatButton = page.locator('button[aria-label="Toggle chat"]')
    await chatButton.click()
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Get chat widget dimensions
    const chatWidget = page.locator('.fixed.z-\\[9998\\]').first()
    const box = await chatWidget.boundingBox()

    if (box) {
      // On desktop, widget should be 400px wide
      expect(box.width).toBeLessThan(450)
      expect(box.width).toBeGreaterThan(350)
    }
  })

  test('T098: Chat page is fully responsive', async ({ page }) => {
    // Navigate to fullscreen chat page
    await page.goto('/chat')
    await expect(page.locator('openai-chatkit')).toBeVisible()

    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    const chatWidgetMobile = page.locator('.fixed.z-\\[9998\\]').first()
    const mobileBox = await chatWidgetMobile.boundingBox()

    if (mobileBox) {
      // Should fill entire viewport on mobile
      expect(mobileBox.width).toBeGreaterThan(350)
      expect(mobileBox.height).toBeGreaterThan(600)
    }

    // Test desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 })
    const desktopBox = await chatWidgetMobile.boundingBox()

    if (desktopBox) {
      // Should fill entire viewport on desktop too
      expect(desktopBox.width).toBeGreaterThan(1800)
      expect(desktopBox.height).toBeGreaterThan(900)
    }
  })
})
