"use client"

import * as React from "react"

export type CalendarProps = {
  _mode?: "single" | "range" | "multiple"
  _selected?: Date | Date[] | Range | undefined
  onSelect?: (date: Date | Date[] | Range | undefined) => void
  className?: string
  disabled?: boolean | ((date: Date) => boolean) | undefined
  _numberOfMonths?: number
}

export type Range = { from: Date; to?: Date }

export function Calendar({
  onSelect,
  className,
  disabled,
}: CalendarProps) {
  // Simple placeholder calendar
  return (
    <div className={className}>
      <div className="p-4 border rounded-md">
        <p className="text-sm text-gray-500">Calendar Component</p>
        <input
          type="date"
          disabled={!!disabled}
          className="mt-2 px-3 py-2 border rounded w-full"
          onChange={(e) => {
            if (onSelect) {
              const date = e.target.value ? new Date(e.target.value) : undefined
              onSelect(date)
            }
          }}
        />
      </div>
    </div>
  )
}
