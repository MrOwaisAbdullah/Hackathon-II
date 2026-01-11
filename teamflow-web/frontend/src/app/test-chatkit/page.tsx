'use client'

import { ChatKit, useChatKit } from '@openai/chatkit-react'

export default function TestChatKitPage() {
  console.log('[TestChatKitPage] Rendering')

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const chatkitEndpoint = `${apiUrl}/api/v1/chat/chatkit`

  const { control, ref } = useChatKit({
    api: {
      url: chatkitEndpoint,
      domainKey: 'local-dev',
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
      <p className="mb-4 text-sm text-gray-600">Endpoint: {chatkitEndpoint}</p>

      <div className="mb-4 p-4 bg-gray-100 rounded">
        <p><strong>Control exists:</strong> {control ? '✅ Yes' : '❌ No'}</p>
        <p><strong>Ref exists:</strong> {ref ? '✅ Yes' : '❌ No'}</p>
      </div>

      <div className="border-4 border-blue-500 p-4" style={{ height: '600px', width: '400px' }}>
        <ChatKit control={control} ref={ref} className="h-full w-full" />
      </div>

      <p className="mt-4 text-sm text-gray-600">
        Try sending a message like &quot;Hello!&quot; to test the chat integration.
      </p>
    </div>
  )
}
