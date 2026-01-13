'use client'

/**
 * TeamFlow ChatWidget using OpenAI ChatKit with custom backend.
 *
 * This component implements ChatKit with a self-hosted backend:
 * - Uses custom FastAPI backend instead of OpenAI-hosted
 * - Integrates with AgentOrchestrator for AI responses
 * - Supports RAG knowledge base queries
 * - Streams responses via Server-Sent Events (SSE)
 * - T101: Voice input integration with floating microphone button
 *
 * Backend Protocol: OpenAI ChatKit server protocol
 * Endpoint: /api/v1/chat/chatkit
 */

import { ChatKit, useChatKit } from '@openai/chatkit-react'
import { useState, useEffect, useCallback } from 'react'
import { MessageCircle, X, Maximize2, Minimize2, Sun, Moon } from 'lucide-react'
import { VoiceInputButton } from './VoiceInputButton'
import { useTheme } from '@/contexts/ThemeContext'

interface ChatWidgetProps {
  apiUrl?: string
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  isFullscreen?: boolean  // T094: Prop to control fullscreen mode from parent
  onFullscreenToggle?: () => void  // T094: Callback when fullscreen toggle is requested
  isOpen?: boolean  // Allow parent to control open state (for /chat page)
}

export function ChatWidget({
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  position = 'bottom-right',
  isFullscreen: isFullscreenProp = false,  // T094: Accept fullscreen prop
  onFullscreenToggle,  // T094: Accept toggle callback
  isOpen: isOpenProp,  // Accept isOpen prop for external control
}: ChatWidgetProps) {
  const [error, setError] = useState<string | null>(null)
  const [isOpenInternal, setIsOpenInternal] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const { theme, toggleTheme } = useTheme()

  // Resolve 'system' theme to actual 'light' or 'dark' for ChatKit
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
      setResolvedTheme(systemTheme)
    } else {
      setResolvedTheme(theme as 'light' | 'dark')
    }
  }, [theme])

  // Use external isOpen prop if provided, otherwise use internal state
  const isOpen = isOpenProp !== undefined ? isOpenProp : isOpenInternal

  // T094: Internal fullscreen state (can be controlled by prop or internal toggle)
  const [isFullscreen, setIsFullscreen] = useState(isFullscreenProp)

  // T098: Detect mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // T094: Sync internal state with prop changes
  useEffect(() => {
    setIsFullscreen(isFullscreenProp)
  }, [isFullscreenProp])

  // T094: Handle fullscreen toggle
  const handleFullscreenToggle = useCallback(() => {
    const newState = !isFullscreen
    setIsFullscreen(newState)
    if (onFullscreenToggle) {
      onFullscreenToggle()
    }
  }, [isFullscreen, onFullscreenToggle])

  // T099: Keyboard shortcut for fullscreen toggle (Ctrl+Shift+F or Escape)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey && event.shiftKey && event.key === 'F') || event.key === 'Escape') {
        event.preventDefault()
        handleFullscreenToggle()
      }
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', handleKeyDown as EventListener)
      return () => window.removeEventListener('keydown', handleKeyDown as EventListener)
    }
  }, [handleFullscreenToggle])

  // Build the full ChatKit endpoint URL
  const chatkitEndpoint = `${apiUrl}/api/v1/chat/chatkit`

  // T101: Handle voice transcript - send to ChatKit when ready
  const handleVoiceTranscriptReady = async (transcript: string): Promise<void> => {
    if (!transcript?.trim()) {
      return
    }

    try {
      // Use ChatKit's sendUserMessage API to send the transcript
      await sendUserMessage({
        text: transcript.trim(),
      })
    } catch {
      console.error('[ChatWidget] Failed to send voice message:')
      setError('Failed to send voice message. Please try again.')
    }
  }

  // useChatKit must be called unconditionally (React hooks rules)
  const { control, ref, sendUserMessage } = useChatKit({
    api: {
      url: chatkitEndpoint,
      domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || 'local-dev',
    },
    theme: resolvedTheme,
    startScreen: {
      greeting: 'Hello! I\'m TeamFlow AI. How can I help you today?',
      prompts: [
        {
          label: 'Ask about project docs',
          prompt: 'What are the design requirements for the landing page?',
          icon: 'document',
        },
        {
          label: 'Team management',
          prompt: 'Who is available for new tasks?',
          icon: 'profile',
        },
        {
          label: 'Project help',
          prompt: 'How do we handle authentication errors?',
          icon: 'circle-question',
        },
        {
          label: 'Create a task',
          prompt: 'Create a task for the landing page redesign',
          icon: 'plus',
        },
      ],
    },
    // Enable feedback actions for recommendations (T065)
    threadItemActions: {
      feedback: true, // Show thumbs up/down buttons
      retry: false,   // Hide retry button
    },
    onReady: () => {
      setIsInitialized(true)
    },
    onError: ({ error: _error }: { error: any }) => {
      console.error('[ChatWidget] onError:', _error)

      // Ignore domain verification errors - chat still works with self-hosted backend
      const errorMessage = _error?.message || _error?.toString() || ''
      if (errorMessage.includes('Domain verification failed') ||
          errorMessage.includes('domain_keys/verify')) {
        console.log('[ChatWidget] Ignoring domain verification error - using self-hosted backend')
        return
      }

      // Show error for other types of errors
      setError('Chat initialization failed. Please refresh the page.')
    },
  })

  const handleToggle = () => {
    // Only toggle if using internal state (not controlled by parent)
    if (isOpenProp === undefined) {
      setIsOpenInternal(!isOpenInternal)
    }
  }

  return (
    <>
      {/* Floating toggle button - only show when using internal state and not in fullscreen */}
      {isOpenProp === undefined && !isFullscreen && (
        <button
          onClick={handleToggle}
          // Use z-40 to stay behind modals (z-50) but above most content
          className="fixed z-40 flex h-14 w-14 items-center justify-center rounded-full bg-accent text-accent-foreground shadow-2xl transition-all hover:scale-105 hover:brightness-110"
          style={{
            bottom: (position as string).includes('bottom') ? '1.5rem' : undefined,
            top: (position as string).includes('top') ? '1.5rem' : undefined,
            left: (position as string).includes('left') ? '1.5rem' : undefined,
            right: (position as string).includes('right') ? '1.5rem' : undefined,
          }}
          aria-label={isOpen ? "Close chat" : "Open chat"}
        >
          {isOpen ? (
            <X className="h-6 w-6" strokeWidth={1.5} />
          ) : (
            <MessageCircle className="h-6 w-6" strokeWidth={1.5} />
          )}
        </button>
      )}

      {/* Error banner */}
      {error && (
        <div className="fixed top-4 right-4 z-40 max-w-sm rounded-lg bg-destructive/10 border border-destructive/20 p-4 shadow-lg">
          <div className="flex items-start">
            <p className="text-sm text-destructive">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-destructive hover:text-destructive/80"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* ChatKit - visible when open */}
      {isOpen && (
        <div
          className={`
            fixed z-50 bg-background shadow-2xl border border-border transition-all duration-300
            flex flex-col
            ${isFullscreen ? 'inset-0 rounded-none' : 'rounded-lg'}
            ${isFullscreen ? 'top-0 left-0 right-0 bottom-0' : ''}
            ${!isFullscreen ? (isMobile ? 'bottom-28 right-4 left-4' : 'bottom-24 right-6') : ''}
            ${!isFullscreen && (position as string).includes('left') && !isMobile ? 'left-6' : ''}
          `}
          style={{
            width: isFullscreen ? '100vw' : (isMobile ? 'calc(100vw - 32px)' : '400px'),
            height: isFullscreen ? '100vh' : '600px',
          }}
        >
          {/* Status bar */}
          <div className={`px-4 py-2 bg-muted border-b border-border ${isFullscreen ? '' : 'rounded-t-lg'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isInitialized ? 'bg-accent' : 'bg-yellow-500'}`} />
                <span className="text-xs font-medium text-foreground">
                  {isInitialized ? 'Connected' : 'Connecting...'}
                </span>
                {isFullscreen && (
                  <span className="text-xs text-muted-foreground ml-2">Fullscreen mode</span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {/* Theme toggle button */}
                <button
                  onClick={() => {
                    console.log('[ChatWidget] Theme toggle clicked, current theme:', theme)
                    toggleTheme()
                    console.log('[ChatWidget] Theme toggle called')
                  }}
                  className="text-muted-foreground hover:text-foreground p-1 rounded hover:bg-secondary"
                  aria-label={`Switch to ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
                  title={`Switch to ${resolvedTheme === 'light' ? 'dark' : 'light'} mode`}
                >
                  {resolvedTheme === 'light' ? (
                    <Moon className="h-4 w-4" strokeWidth={1.5} />
                  ) : (
                    <Sun className="h-4 w-4" strokeWidth={1.5} />
                  )}
                </button>
                {/* T095: Fullscreen toggle button */}
                <button
                  onClick={handleFullscreenToggle}
                  className="text-muted-foreground hover:text-foreground p-1 rounded hover:bg-secondary"
                  aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
                  title={`Press Ctrl+Shift+F or ${isFullscreen ? 'Escape' : 'click'} to ${isFullscreen ? 'exit' : 'enter'} fullscreen`}
                >
                  {isFullscreen ? (
                    <Minimize2 className="h-4 w-4" strokeWidth={1.5} />
                  ) : (
                    <Maximize2 className="h-4 w-4" strokeWidth={1.5} />
                  )}
                </button>
                <button
                  onClick={() => {
                    // Only allow closing if using internal state
                    if (isOpenProp === undefined) {
                      setIsOpenInternal(false)
                    }
                  }}
                  className="text-muted-foreground hover:text-foreground p-1 rounded hover:bg-secondary"
                  aria-label="Close chat"
                >
                  <X className="h-4 w-4" strokeWidth={1.5} />
                </button>
              </div>
            </div>
          </div>

          {/* ChatKit component */}
          <div className={`flex-1 overflow-hidden ${isFullscreen ? '' : 'rounded-b-lg'}`}>
            <ChatKit
              control={control}
              ref={ref as any}
              className="h-full w-full"
            />
          </div>

          {/* T101: Voice Input Button - Positioned above input, aligned with send button */}
          <div className="absolute bottom-20 right-6 z-10">
            <VoiceInputButton
              onTranscriptReady={handleVoiceTranscriptReady}
              language="en-US"
            />
          </div>
        </div>
      )}
    </>
  )
}

// Also export a simpler default export
export default ChatWidget
