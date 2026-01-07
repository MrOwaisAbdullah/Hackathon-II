'use client'

// """TeamFlow ChatWidget using OpenAI ChatKit.
// This component wraps the official ChatKit Chat component and integrates
// with our FastAPI backend endpoints.
// """

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

  // useChatKit must be called unconditionally (React hooks rules)
  const { control, ref } = useChatKit({
    api: {
      async getClientSecret(existing) {
        console.log('[ChatWidget] >>> getClientSecret called, existing:', existing)
        try {
          console.log('[ChatWidget] Creating chat session with API:', apiUrl)

          // Get auth token from localStorage (Better Auth JWT)
          const authToken = typeof window !== 'undefined'
            ? localStorage.getItem('auth_token')
            : null

          const headers: Record<string, string> = {
            'Content-Type': 'application/json',
          }

          // Add session token if available
          if (authToken) {
            headers['X-Session-Token'] = authToken
            console.log('[ChatWidget] Including auth token in request')
          }

          const res = await fetch(`${apiUrl}/api/v1/chat/sessions`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              user_id: 'temp-user',
            }),
          })

          if (!res.ok) {
            const errorText = await res.text()
            console.error('[ChatWidget] Session creation failed:', res.status, errorText)
            throw new Error(`Failed to create session: ${res.status} - ${errorText}`)
          }

          const data = await res.json()
          console.log('[ChatWidget] Session created successfully:', data.conversation_id)
          return data.conversation_id
        } catch (err) {
          const message = err instanceof Error ? err.message : 'Unknown error'
          console.error('[ChatWidget] getClientSecret error:', err)
          setError(message)
          throw err
        }
      },
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
        className="fixed z-[9999] flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-2xl transition-all hover:bg-blue-700 hover:scale-105"
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

      {/* ChatKit - temporarily always visible for testing */}
      <div className="fixed z-[9998] bg-white border-4 border-green-500" style={{
        bottom: '5rem',
        right: '1.5rem',
        width: '400px',
        height: '600px',
      }}>
        <div className="p-2 bg-green-100 text-xs">
          ChatKit Status: {isInitialized ? '✅ READY' : '⏳ Initializing...'}
        </div>
        <ChatKit
          control={control}
          ref={ref}
          className="h-[580px] w-[400px]"
        />
      </div>
    </>
  )
}

// Also export a simpler default export
export default ChatWidget
