'use client'

/**
 * AI Reasoning Panel Component (T065)
 *
 * Displays AI reasoning for recommendations with accept/reject buttons.
 * Tracks user feedback via /chat/recommendations/track endpoint.
 *
 * Usage:
 *   <AIReasoningPanel
 *     recommendationId="rec-123"
 *     recommendationType="assignee"
 *     reasoning="Skills match: 85%, Workload: 12 tasks, Availability: 40h/week"
 *     context={{ task_id: "abc", project_id: "xyz" }}
 *     onAccept={() => console.log('Accepted')}
 *     onReject={() => console.log('Rejected')}
 *   />
 */

import { useState } from 'react'

interface AIReasoningPanelProps {
  /** Unique identifier for this recommendation */
  recommendationId: string
  /** Type of recommendation (assignee, task_creation, priority, etc.) */
  recommendationType: string
  /** AI reasoning text to display */
  reasoning: string
  /** Additional context (task_id, project_id, etc.) */
  context?: Record<string, unknown>
  /** Callback when user accepts recommendation */
  onAccept?: () => void
  /** Callback when user rejects recommendation */
  onReject?: () => void
  /** API URL for tracking endpoint */
  apiUrl?: string
}

export function AIReasoningPanel({
  recommendationId,
  recommendationType,
  reasoning,
  context = {},
  onAccept,
  onReject,
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
}: AIReasoningPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isTracking, setIsTracking] = useState(false)
  const [feedback, setFeedback] = useState<'accepted' | 'rejected' | null>(null)

  const trackFeedback = async (action: 'accepted' | 'rejected') => {
    setIsTracking(true)
    setFeedback(action)

    try {
      // Call the tracking endpoint (T066)
      const response = await fetch(`${apiUrl}/api/v1/chat/recommendations/track`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Note: In production, include X-Session-Token header
        },
        body: JSON.stringify({
          recommendation_type: recommendationType,
          recommendation_id: recommendationId,
          action,
          reasoning,
          context,
        }),
      })

      if (response.ok) {
        console.log(`[AIReasoningPanel] Recommendation ${action} tracked successfully`)
      } else {
        console.error(`[AIReasoningPanel] Failed to track ${action}:`, await response.text())
      }
    } catch {
      console.error(`[AIReasoningPanel] Error tracking ${action}:`, error)
    } finally {
      setIsTracking(false)
    }

    // Trigger callbacks
    if (action === 'accepted' && onAccept) onAccept()
    if (action === 'rejected' && onReject) onReject()
  }

  return (
    <div className="mt-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
      {/* Header with expand/collapse */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="h-4 w-4 text-blue-600"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
            />
          </svg>
          <span className="text-sm font-medium text-blue-900">
            AI Recommendation: {recommendationType}
          </span>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs text-blue-600 hover:text-blue-800"
          aria-label={isExpanded ? 'Collapse reasoning' : 'Expand reasoning'}
        >
          {isExpanded ? 'Hide' : 'Show'} Reasoning
        </button>
      </div>

      {/* Expandable reasoning section */}
      {isExpanded && (
        <div className="mt-2 rounded bg-white p-2 text-sm text-gray-700">
          <div className="mb-2 font-semibold text-gray-900">Why this recommendation?</div>
          <div className="whitespace-pre-wrap">{reasoning}</div>
        </div>
      )}

      {/* Accept/Reject buttons */}
      {feedback === null ? (
        <div className="mt-3 flex items-center space-x-2">
          <span className="text-xs text-gray-600">Was this helpful?</span>
          <button
            onClick={() => trackFeedback('accepted')}
            disabled={isTracking}
            className="flex items-center space-x-1 rounded-md bg-green-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="h-4 w-4"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            <span>Accept</span>
          </button>
          <button
            onClick={() => trackFeedback('rejected')}
            disabled={isTracking}
            className="flex items-center space-x-1 rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="h-4 w-4"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span>Reject</span>
          </button>
        </div>
      ) : (
        <div className="mt-3 flex items-center space-x-2 text-xs">
          {feedback === 'accepted' ? (
            <>
              <span className="text-green-600">✓ Accepted</span>
              <span className="text-gray-500">Thank you for your feedback!</span>
            </>
          ) : (
            <>
              <span className="text-red-600">✗ Rejected</span>
              <span className="text-gray-500">We&#39;ll use this to improve.</span>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default AIReasoningPanel
