/**
 * T054: RecurrenceDialog Component
 *
 * A dialog component for configuring recurring task rules.
 * Supports frequency, interval, days of week, end date, and time-of-day selection.
 */

"use client"

import { useState, useEffect } from "react"
import { createPortal } from "react-dom"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { CalendarIcon, RefreshCw, ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

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

// Helper to generate calendar days
function generateCalendarDays(year: number, month: number): (number | null)[] {
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const days: (number | null)[] = []

  for (let i = 0; i < firstDay; i++) {
    days.push(null)
  }

  for (let day = 1; day <= daysInMonth; day++) {
    days.push(day)
  }

  return days
}

const monthNames = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
]

export function RecurrenceDialog({ onSave, initialRule, trigger }: RecurrenceDialogProps) {
  const [open, setOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [calendarOpen, setCalendarOpen] = useState(false)
  const [viewYear, setViewYear] = useState(new Date().getFullYear())
  const [viewMonth, setViewMonth] = useState(new Date().getMonth())
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

  useEffect(() => {
    setMounted(true)
  }, [])

  const weekDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

  const handleSave = () => {
    if (rule.frequency) {
      onSave(rule)
      setOpen(false)
    }
  }

  const handleClear = () => {
    const clearedRule = {
      frequency: null,
      interval: 1,
      daysOfWeek: [],
      dayOfMonth: null,
      endDate: null,
      timeOfDay: null,
    }
    setRule(clearedRule)
    onSave(clearedRule)
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

  const calendarDays = generateCalendarDays(viewYear, viewMonth)

  const selectedEndDate = rule.endDate ? new Date(rule.endDate) : null

  const handleDateSelect = (day: number) => {
    const newDate = new Date(viewYear, viewMonth, day)
    setRule((prev) => ({
      ...prev,
      endDate: newDate.toISOString().split('T')[0],
    }))
    setCalendarOpen(false)
  }

  const handleClearDate = () => {
    setRule((prev) => ({ ...prev, endDate: null }))
  }

  const handlePreviousMonth = () => {
    if (viewMonth === 0) {
      setViewMonth(11)
      setViewYear(viewYear - 1)
    } else {
      setViewMonth(viewMonth - 1)
    }
  }

  const handleNextMonth = () => {
    if (viewMonth === 11) {
      setViewMonth(0)
      setViewYear(viewYear + 1)
    } else {
      setViewMonth(viewMonth + 1)
    }
  }

  return (
    <div className="relative">
      {/* Trigger Button */}
      <div onClick={() => setOpen(true)} className={trigger ? "" : "cursor-pointer"}>
        {trigger || (
          <Button type="button" variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Set Recurrence
          </Button>
        )}
      </div>

      {/* Dialog - Rendered via Portal to escape stacking contexts */}
      {mounted && open && createPortal(
        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4"
              onClick={() => setOpen(false)}
            >
              {/* Backdrop */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="absolute inset-0 bg-black/20 backdrop-blur-sm"
              />

              {/* Dialog Content */}
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                transition={{ type: "spring", duration: 0.5, bounce: 0.3 }}
                className="relative w-full max-w-md bg-card rounded-2xl border border-border shadow-2xl max-h-[80vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                {/* Header */}
                <div className="px-6 py-5 border-b border-border">
                  <div className="flex items-center gap-2">
                    <RefreshCw className="h-5 w-5" />
                    <h2 className="text-lg font-bold text-foreground">Set Recurrence</h2>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    Configure how often this task should repeat automatically
                  </p>
                </div>

                {/* Content */}
                <div className="p-6 space-y-4">
                  {/* Frequency Selection */}
                  <div className="space-y-2">
                    <Label htmlFor="frequency" className="text-sm font-medium">Frequency</Label>
                    <Select
                      value={rule.frequency || ""}
                      onValueChange={(value) =>
                        setRule((prev) => ({ ...prev, frequency: value as any }))
                      }
                    >
                      <SelectTrigger className="w-full">
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
                      <Label htmlFor="interval" className="text-sm font-medium">Every</Label>
                      <div className="flex items-center gap-3">
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
                      <Label className="text-sm font-medium">Repeat on</Label>
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
                      <Label htmlFor="dayOfMonth" className="text-sm font-medium">Day of month</Label>
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
                        className="w-full"
                      />
                    </div>
                  )}

                  {/* Time of Day */}
                  <div className="space-y-2">
                    <Label htmlFor="timeOfDay" className="text-sm font-medium">Time of day (optional)</Label>
                    <Input
                      id="timeOfDay"
                      type="time"
                      value={rule.timeOfDay || ""}
                      onChange={(e) => setRule((prev) => ({ ...prev, timeOfDay: e.target.value || null }))}
                      className="w-full"
                    />
                    <p className="text-xs text-muted-foreground">
                      e.g., 14:00 for 2 PM
                    </p>
                  </div>

                  {/* End Date - Custom Calendar */}
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">End date (optional)</Label>
                    <div className="relative">
                      <motion.button
                        type="button"
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                        onClick={() => setCalendarOpen(!calendarOpen)}
                        className="w-full flex items-center justify-between gap-3 px-4 py-3 border-2 rounded-xl bg-background transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent border-input hover:border-input/80"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center">
                            <CalendarIcon className="w-4 h-4 text-accent" />
                          </div>
                          <span className="text-sm font-medium text-foreground">
                            {rule.endDate
                              ? new Date(rule.endDate).toLocaleDateString("en-US", {
                                  month: "short",
                                  day: "numeric",
                                  year: "numeric",
                                })
                              : "Pick a date"}
                          </span>
                        </div>
                        {rule.endDate && (
                          <button
                            type="button"
                            onClick={handleClearDate}
                            className="p-1 rounded-lg hover:bg-muted transition-colors"
                          >
                            ×
                          </button>
                        )}
                      </motion.button>

                      {/* Calendar Popover */}
                      <AnimatePresence>
                        {calendarOpen && (
                          <>
                            <div
                              className="fixed inset-0 z-10"
                              onClick={() => setCalendarOpen(false)}
                            />
                            <motion.div
                              initial={{ opacity: 0, y: -10, scale: 0.95 }}
                              animate={{ opacity: 1, y: 0, scale: 1 }}
                              exit={{ opacity: 0, y: -10, scale: 0.95 }}
                              transition={{ duration: 0.15 }}
                              className="absolute top-full right-0 mt-2 w-72 bg-card border border-input rounded-xl shadow-xl z-20 overflow-hidden"
                            >
                              {/* Header with Navigation */}
                              <div className="flex items-center justify-between p-3 border-b border-input bg-muted/30">
                                <motion.button
                                  type="button"
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={handlePreviousMonth}
                                  className="p-1 rounded-lg hover:bg-accent/10 transition-colors"
                                >
                                  <ChevronLeft className="w-4 h-4 text-accent" />
                                </motion.button>

                                <span className="font-semibold text-sm text-foreground">
                                  {monthNames[viewMonth]} {viewYear}
                                </span>

                                <motion.button
                                  type="button"
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={handleNextMonth}
                                  className="p-1 rounded-lg hover:bg-accent/10 transition-colors"
                                >
                                  <ChevronRight className="w-4 h-4 text-accent" />
                                </motion.button>
                              </div>

                              {/* Day Headers */}
                              <div className="grid grid-cols-7 gap-1 p-2 bg-background">
                                {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map((day) => (
                                  <div
                                    key={day}
                                    className="text-center text-xs text-muted-foreground font-medium py-1"
                                  >
                                    {day}
                                  </div>
                                ))}

                                {/* Calendar Days */}
                                {calendarDays.map((day, index) => {
                                  const isSelected =
                                    day &&
                                    selectedEndDate &&
                                    selectedEndDate.getDate() === day &&
                                    selectedEndDate.getMonth() === viewMonth &&
                                    selectedEndDate.getFullYear() === viewYear

                                  const isToday =
                                    day &&
                                    new Date().getDate() === day &&
                                    new Date().getMonth() === viewMonth &&
                                    new Date().getFullYear() === viewYear

                                  return (
                                    <button
                                      key={index}
                                      type="button"
                                      onClick={() => day && handleDateSelect(day)}
                                      disabled={!day}
                                      className={cn(
                                        "aspect-square flex items-center justify-center text-sm rounded-lg transition-all duration-200",
                                        day ? "hover:bg-accent/10 cursor-pointer" : "cursor-default",
                                        isSelected && "bg-accent text-accent-foreground font-semibold shadow-md",
                                        isToday && !isSelected && "border-2 border-accent text-accent"
                                      )}
                                    >
                                      {day || ""}
                                    </button>
                                  )
                                })}
                              </div>
                            </motion.div>
                          </>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-border flex justify-between">
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
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>,
        document.body
      )}
    </div>
  )
}
