'use client'

/**
 * TeamFlow ChatWidget using OpenAI ChatKit with custom backend.
 *
 * This component implements ChatKit with a self-hosted backend:
 * - Uses custom FastAPI backend instead of OpenAI-hosted
 * - Integrates with AgentOrchestrator for AI responses
 * - Supports RAG knowledge base queries
 * - Streams responses via Server-Sent Events (SSE)
 *
 * Backend Protocol: OpenAI ChatKit server protocol
 * Endpoint: /api/v1/chat/chatkit
 */

import { ChatKit, useChatKit } from '@openai/chatkit-react'
import { useState } from 'react'

interface ChatWidgetProps {
  apiUrl?: string
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
}

export function ChatWidget({
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  position = 'bottom-right'
}: ChatWidgetProps) {
  console.log('[ChatWidget] Component mounting with apiUrl:', apiUrl)

  const [error, setError] = useState<string | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)

  // Build the full ChatKit endpoint URL
  const chatkitEndpoint = `${apiUrl}/api/v1/chat/chatkit`

  // useChatKit must be called unconditionally (React hooks rules)
  const { control, ref } = useChatKit({
    api: {
      url: chatkitEndpoint,
      domainKey: 'local-dev',
    },
    theme: 'light',
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
    onReady: () => {
      console.log('[ChatWidget] >>> onReady CALLED <<<')
      setIsInitialized(true)
    },
    onError: ({ error }: { error: any }) => {
      console.error('[ChatWidget] >>> onError CALLED <<<:', error)
      setError(error.message)
    },
  })

  console.log('[ChatWidget] useChatKit returned control:', !!control, 'ref:', !!ref, 'isInitialized:', isInitialized)

  const handleToggle = () => {
    console.log('[ChatWidget] Button clicked! isOpen:', isOpen, '->', !isOpen)
    setIsOpen(!isOpen)
  }

  return (
    <>
      {/* Floating toggle button */}
      <button
        onClick={handleToggle}
        className="fixed z-[9999] flex h-14 w-14 items-center justify-center rounded-full bg-gray-800 text-white shadow-2xl transition-all hover:bg-gray-900 hover:scale-105"
        style={{
          bottom: position.includes('bottom') ? '1.5rem' : undefined,
          top: position.includes('top') ? '1.5rem' : undefined,
          left: position.includes('left') ? '1.5rem' : undefined,
          right: position.includes('right') ? '1.5rem' : undefined,
        }}
        aria-label="Toggle chat"
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-6 w-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m2.25 0H12m10.5-9h.008v.008h-.008V12m10.5-9v.008V3m-10.5 9.75V12m10.5-9v.008h-.008V3m-9.75 9.75v.008h.008V12m9.75-9.75V12m10.5-9v.008H12.75V12" />
        </svg>
      </button>

      {/* Error banner */}
      {error && (
        <div className="fixed top-4 right-4 z-[10000] max-w-sm rounded-lg bg-red-50 border border-red-200 p-4 shadow-lg">
          <div className="flex items-start">
            <p className="text-sm text-red-800">{error}</p>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* ChatKit - visible when open */}
      {isOpen && (
        <div className="fixed z-[9998] bg-white rounded-lg shadow-2xl border border-gray-200" style={{
          bottom: '5rem',
          right: position.includes('right') ? '1.5rem' : undefined,
          left: position.includes('left') ? '1.5rem' : undefined,
          width: '400px',
          height: '600px',
        }}>
          {/* Status bar */}
          <div className="px-4 py-2 bg-gray-50 border-b border-gray-200 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isInitialized ? 'bg-gray-500' : 'bg-gray-400'}`} />
                <span className="text-xs font-medium text-gray-700">
                  {isInitialized ? 'Connected' : 'Connecting...'}
                </span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700"
                aria-label="Close chat"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-4 w-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* ChatKit component */}
          <div className="h-[560px] w-[400px]">
            <ChatKit
              control={control}
              ref={ref}
              className="h-full w-full"
            />
          </div>
        </div>
      )}
    </>
  )
}

// Also export a simpler default export
export default ChatWidget
