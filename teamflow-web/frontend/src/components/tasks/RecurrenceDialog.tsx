"""
T054: RecurrenceDialog Component

A dialog component for configuring recurring task rules.
Supports frequency, interval, days of week, end date, and time-of-day selection.
"""

"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon, RefreshCw } from "lucide-react"
import { format } from "date-fns"

interface RecurrenceRule {
  frequency: "daily" | "weekly" | "monthly" | "yearly" | null
  interval: number
  daysOfWeek: string[]
  dayOfMonth: number | null
  endDate: string | null
  timeOfDay: string | null
}

interface RecurrenceDialogProps {
  onSave: (rule: RecurrenceRule) => void
  initialRule?: RecurrenceRule
  trigger?: React.ReactNode
}

export function RecurrenceDialog({ onSave, initialRule, trigger }: RecurrenceDialogProps) {
  const [open, setOpen] = useState(false)
  const [rule, setRule] = useState<RecurrenceRule>(
    initialRule || {
      frequency: null,
      interval: 1,
      daysOfWeek: [],
      dayOfMonth: null,
      endDate: null,
      timeOfDay: null,
    }
  )

  const weekDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

  const handleSave = () => {
    if (rule.frequency) {
      onSave(rule)
      setOpen(false)
    }
  }

  const handleClear = () => {
    setRule({
      frequency: null,
      interval: 1,
      daysOfWeek: [],
      dayOfMonth: null,
      endDate: null,
      timeOfDay: null,
    })
    onSave(rule)
    setOpen(false)
  }

  const toggleDayOfWeek = (day: string) => {
    setRule((prev) => ({
      ...prev,
      daysOfWeek: prev.daysOfWeek.includes(day)
        ? prev.daysOfWeek.filter((d) => d !== day)
        : [...prev.daysOfWeek, day],
    }))
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Set Recurrence
          </DialogTitle>
          <DialogDescription>
            Configure how often this task should repeat automatically
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Frequency Selection */}
          <div className="space-y-2">
            <Label htmlFor="frequency">Frequency</Label>
            <Select
              value={rule.frequency || ""}
              onValueChange={(value) =>
                setRule((prev) => ({ ...prev, frequency: value as any }))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Select frequency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Interval */}
          {rule.frequency && (
            <div className="space-y-2">
              <Label htmlFor="interval">Every</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="interval"
                  type="number"
                  min={1}
                  value={rule.interval}
                  onChange={(e) =>
                    setRule((prev) => ({ ...prev, interval: parseInt(e.target.value) || 1 }))
                  }
                  className="w-20"
                />
                <span className="text-sm text-muted-foreground">
                  {rule.frequency === "daily"
                    ? "day(s)"
                    : rule.frequency === "weekly"
                      ? "week(s)"
                      : rule.frequency === "monthly"
                        ? "month(s)"
                        : "year(s)"}
                </span>
              </div>
            </div>
          )}

          {/* Days of Week (for weekly frequency) */}
          {rule.frequency === "weekly" && (
            <div className="space-y-2">
              <Label>Repeat on</Label>
              <div className="flex flex-wrap gap-2">
                {weekDays.map((day) => (
                  <Button
                    key={day}
                    type="button"
                    variant={rule.daysOfWeek.includes(day) ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleDayOfWeek(day)}
                  >
                    {day.slice(0, 3)}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Day of Month (for monthly frequency) */}
          {rule.frequency === "monthly" && (
            <div className="space-y-2">
              <Label htmlFor="dayOfMonth">Day of month</Label>
              <Input
                id="dayOfMonth"
                type="number"
                min={1}
                max={31}
                placeholder="e.g., 15"
                value={rule.dayOfMonth || ""}
                onChange={(e) =>
                  setRule((prev) => ({ ...prev, dayOfMonth: parseInt(e.target.value) || null }))
                }
              />
            </div>
          )}

          {/* Time of Day */}
          <div className="space-y-2">
            <Label htmlFor="timeOfDay">Time of day (optional)</Label>
            <Input
              id="timeOfDay"
              type="time"
              value={rule.timeOfDay || ""}
              onChange={(e) => setRule((prev) => ({ ...prev, timeOfDay: e.target.value || null }))}
            />
            <p className="text-xs text-muted-foreground">
              e.g., 14:00 for 2 PM
            </p>
          </div>

          {/* End Date */}
          <div className="space-y-2">
            <Label>End date (optional)</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-start text-left font-normal"
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {rule.endDate
                    ? format(new Date(rule.endDate), "MMM d, yyyy")
                    : "Pick a date"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <Calendar
                  mode="single"
                  selected={rule.endDate ? new Date(rule.endDate) : undefined}
                  onSelect={(date) =>
                    setRule((prev) => ({
                      ...prev,
                      endDate: date ? date.toISOString().split("T")[0] : null,
                    }))
                  }
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
        </div>

        <DialogFooter className="flex justify-between">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClear}
            disabled={!rule.frequency}
          >
            Clear Recurrence
          </Button>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="button" onClick={handleSave} disabled={!rule.frequency}>
              Save Recurrence
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
