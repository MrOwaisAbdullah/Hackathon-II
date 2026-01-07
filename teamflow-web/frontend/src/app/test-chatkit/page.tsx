'use client'

import { ChatKit, useChatKit } from '@openai/chatkit-react'

export default function TestChatKitPage() {
  console.log('[TestChatKitPage] Rendering')

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const { control, ref } = useChatKit({
    api: {
      async getClientSecret(existing) {
        console.log('[TestChatKitPage] >>> getClientSecret called!', { existing })

        // Get auth token from localStorage
        const authToken = typeof window !== 'undefined'
          ? localStorage.getItem('auth_token')
          : null

        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
        }

        if (authToken) {
          headers['X-Session-Token'] = authToken
          console.log('[TestChatKitPage] Including auth token')
        }

        const res = await fetch(`${apiUrl}/api/v1/chat/sessions`, {
          method: 'POST',
          headers,
          body: JSON.stringify({ user_id: 'test-user' }),
        })

        if (!res.ok) {
          const errorText = await res.text()
          console.error('[TestChatKitPage] Session creation failed:', res.status, errorText)
          throw new Error(`Failed to create session: ${res.status} - ${errorText}`)
        }

        const data = await res.json()
        console.log('[TestChatKitPage] Session response:', data)
        return data.conversation_id
      },
    },
    onReady: () => {
      console.log('[TestChatKitPage] >>> onReady called!')
    },
    onError: ({ error }) => {
      console.error('[TestChatKitPage] >>> onError called!', error)
    },
  })

  console.log('[TestChatKitPage] useChatKit returned:', { control: !!control, ref: !!ref })

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">ChatKit Test Page</h1>

      <div className="mb-4 p-4 bg-gray-100 rounded">
        <p><strong>Control exists:</strong> {control ? '✅ Yes' : '❌ No'}</p>
        <p><strong>Ref exists:</strong> {ref ? '✅ Yes' : '❌ No'}</p>
      </div>

      <div className="border-4 border-blue-500 p-4" style={{ height: '600px', width: '400px' }}>
        <ChatKit control={control} ref={ref} className="h-full w-full" />
      </div>

      <p className="mt-4 text-sm text-gray-600">
        Check the console for logs. You should see:
        <br />1. [TestChatKitPage] Rendering
        <br />2. [TestChatKitPage] useChatKit returned
        <br />3. [TestChatKitPage] &gt;&gt;&gt; getClientSecret called! &lt;&lt;&lt; THIS IS MISSING
        <br />4. [TestChatKitPage] &gt;&gt;&gt; onReady called! &lt;&lt;&lt; THIS IS ALSO MISSING
      </p>
    </div>
  )
}
