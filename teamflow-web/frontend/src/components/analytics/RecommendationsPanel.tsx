'use client'

/**
 * Recommendations Panel Component (T070)
 *
 * Displays recommendation acceptance rate analytics dashboard.
 * Shows:
 * - Overall acceptance rate vs target (70% SC-005)
 * - Acceptance rate by recommendation type
 * - Weekly trend chart
 * - Total recommendations with accepted/rejected breakdown
 *
 * Data source: /api/v1/chat/recommendations/stats endpoint
 */

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'

interface RecommendationStats {
  total_recommendations: number
  accepted: number
  rejected: number
  acceptance_rate: number
  target_rate: number
  meets_target: boolean | null
  message?: string
  by_type: {
    assignee: { total: number; accepted: number; rate: number }
    task_creation: { total: number; accepted: number; rate: number }
  }
  trend_7_days: Array<{ date: string; rate: number; total: number }>
}

export function RecommendationsPanel({ apiUrl }: { apiUrl?: string }) {
  const [stats, setStats] = useState<RecommendationStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const baseUrl = apiUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchStats() {
      try {
        const response = await fetch(`${baseUrl}/api/v1/chat/recommendations/stats`)
        if (response.ok) {
          const data = await response.json()
          setStats(data)
        } else {
          setError('Failed to fetch statistics')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [baseUrl])

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading recommendation analytics...</div>
        </div>
      </Card>
    )
  }

  if (error || !stats) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-red-500">Error: {error || 'No data available'}</div>
        </div>
      </Card>
    )
  }

  // Calculate metrics
  const overallRate = stats.acceptance_rate
  const targetRate = stats.target_rate * 100
  const meetsTarget = stats.meets_target === true
  const gap = Math.max(0, targetRate - overallRate)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">AI Recommendation Analytics</h2>
        <p className="text-sm text-gray-600">Track how users respond to AI-driven suggestions (SC-005: 70% target)</p>
      </div>

      {/* Overall Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600">Total Recommendations</div>
          <div className="text-2xl font-bold text-gray-900">{stats.total_recommendations}</div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-gray-600">Accepted</div>
          <div className="text-2xl font-bold text-green-600">{stats.accepted}</div>
        </Card>

        <Card className="p-4">
          <div className="text-sm text-gray-600">Rejected</div>
          <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
        </Card>

        <Card className={`p-4 ${meetsTarget ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
          <div className="text-sm text-gray-600">Acceptance Rate</div>
          <div className={`text-2xl font-bold ${meetsTarget ? 'text-green-600' : 'text-yellow-600'}`}>
            {overallRate.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">Target: {targetRate.toFixed(0)}%</div>
        </Card>
      </div>

      {/* Status Banner */}
      <Card className={`p-4 ${meetsTarget ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
        <div className="flex items-center space-x-3">
          {meetsTarget ? (
            <>
              <div className="text-green-600 text-2xl">✅</div>
              <div>
                <div className="font-semibold text-green-900">MEETS TARGET</div>
                <div className="text-sm text-green-700">
                  Acceptance rate of {overallRate.toFixed(1)}% meets the 70% target (SC-005)
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="text-yellow-600 text-2xl">⚠️</div>
              <div>
                <div className="font-semibold text-yellow-900">BELOW TARGET</div>
                <div className="text-sm text-yellow-700">
                  {gap.toFixed(1)} percentage points below target. Consider improving recommendation quality or user communication.
                </div>
              </div>
            </>
          )}
        </div>
      </Card>

      {/* Breakdown by Type */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Breakdown by Type</h3>
        <div className="space-y-4">
          {/* Assignee Recommendations */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Assignee Recommendations</span>
              <span className={`text-sm font-semibold ${stats.by_type.assignee.rate >= 70 ? 'text-green-600' : 'text-yellow-600'}`}>
                {stats.by_type.assignee.rate.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${stats.by_type.assignee.rate >= 70 ? 'bg-green-600' : 'bg-yellow-600'}`}
                style={{ width: `${Math.min(stats.by_type.assignee.rate, 100)}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
              <span>{stats.by_type.assignee.accepted} accepted</span>
              <span>{stats.by_type.assignee.total} total</span>
            </div>
          </div>

          {/* Task Creation Recommendations */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Task Creation Recommendations</span>
              <span className={`text-sm font-semibold ${stats.by_type.task_creation.rate >= 70 ? 'text-green-600' : 'text-yellow-600'}`}>
                {stats.by_type.task_creation.rate.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${stats.by_type.task_creation.rate >= 70 ? 'bg-green-600' : 'bg-yellow-600'}`}
                style={{ width: `${Math.min(stats.by_type.task_creation.rate, 100)}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-1 text-xs text-gray-500">
              <span>{stats.by_type.task_creation.accepted} accepted</span>
              <span>{stats.by_type.task_creation.total} total</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Weekly Trend */}
      {stats.trend_7_days && stats.trend_7_days.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">7-Day Trend</h3>
          <div className="flex items-end justify-between h-40 gap-2">
            {stats.trend_7_days.map((day, index) => {
              const height = Math.max(5, day.rate) // Minimum height for visibility
              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div
                    className={`w-full rounded-t ${day.rate >= 70 ? 'bg-green-500' : 'bg-yellow-500'}`}
                    style={{ height: `${height}%` }}
                    title={`${day.date}: ${day.rate.toFixed(1)}% (${day.total} recommendations)`}
                  />
                  <div className="text-xs text-gray-500 mt-2 transform -rotate-45 origin-top-left truncate w-full">
                    {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                  </div>
                </div>
              )
            })}
          </div>
          <div className="mt-4 text-sm text-gray-600">
            <div className="flex items-center justify-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded" />
                <span>≥ 70% (Target Met)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-yellow-500 rounded" />
                <span>&lt; 70% (Below Target)</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Info Message */}
      {stats.message && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="flex items-start space-x-3">
            <div className="text-blue-600 text-xl">ℹ️</div>
            <div className="text-sm text-blue-800">{stats.message}</div>
          </div>
        </Card>
      )}
    </div>
  )
}

export default RecommendationsPanel
