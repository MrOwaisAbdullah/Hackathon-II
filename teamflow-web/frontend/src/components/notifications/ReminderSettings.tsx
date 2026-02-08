/**
 * T084: ReminderSettings Component
 *
 * A dialog component for configuring reminder settings for tasks.
 * Supports multiple offset selections, notification channels, and custom messages.
 */

"use client"

import { useState, useEffect } from "react"
import { createPortal } from "react-dom"
import { motion, AnimatePresence } from "framer-motion"
import { Bell, Mail, Smartphone } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

interface ReminderSettingsData {
  enabled: boolean
  offsets: string[]  // ["15m", "1h", "1d", "1w"]
  channels: string[]  // ["email", "push"]
  custom_message?: string
}

interface ReminderSettingsProps {
  onSave: (settings: ReminderSettingsData) => void
  initialSettings?: ReminderSettingsData
  trigger?: React.ReactNode
}

// Available offset options
const OFFSET_OPTIONS = [
  { value: "15m", label: "15 minutes before" },
  { value: "1h", label: "1 hour before" },
  { value: "1d", label: "1 day before" },
  { value: "1w", label: "1 week before" },
]

// Available channel options
const CHANNEL_OPTIONS = [
  { value: "email", label: "Email", icon: Mail },
  { value: "push", label: "Push Notification", icon: Smartphone },
]

export function ReminderSettings({ onSave, initialSettings, trigger }: ReminderSettingsProps) {
  const [open, setOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [settings, setSettings] = useState<ReminderSettingsData>(
    initialSettings || {
      enabled: false,
      offsets: [],
      channels: ["email"],
      custom_message: undefined,
    }
  )

  // Ensure we only render portal on client side
  useEffect(() => {
    setMounted(true)
  }, [])

  const handleSave = () => {
    onSave(settings)
    setOpen(false)
  }

  const handleClear = () => {
    const clearedSettings = {
      enabled: false,
      offsets: [],
      channels: ["email"],
      custom_message: undefined,
    }
    setSettings(clearedSettings)
    onSave(clearedSettings)
    setOpen(false)
  }

  const toggleOffset = (offset: string) => {
    setSettings((prev) => ({
      ...prev,
      enabled: true,
      offsets: prev.offsets.includes(offset)
        ? prev.offsets.filter((o) => o !== offset)
        : [...prev.offsets, offset],
    }))
  }

  const toggleChannel = (channel: string) => {
    setSettings((prev) => ({
      ...prev,
      enabled: true,
      channels: prev.channels.includes(channel)
        ? prev.channels.filter((c) => c !== channel)
        : [...prev.channels, channel],
    }))
  }

  return (
    <div className="relative">
      {/* Trigger Button */}
      <div onClick={() => setOpen(true)} className={trigger ? "" : "cursor-pointer"}>
        {trigger || (
          <Button type="button" variant="outline">
            <Bell className="w-4 h-4 mr-2" />
            Set Reminders
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
                    <Bell className="h-5 w-5" />
                    <h2 className="text-lg font-bold text-foreground">Set Reminders</h2>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    Configure when and how to be notified before this task is due
                  </p>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                  {/* Reminder Offsets */}
                  <div className="space-y-3">
                    <Label className="text-sm font-medium">Remind me</Label>
                    <div className="flex flex-wrap gap-2">
                      {OFFSET_OPTIONS.map((option) => (
                        <Button
                          key={option.value}
                          type="button"
                          variant={settings.offsets.includes(option.value) ? "default" : "outline"}
                          size="sm"
                          onClick={() => toggleOffset(option.value)}
                        >
                          {option.label}
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Notification Channels */}
                  <div className="space-y-3">
                    <Label className="text-sm font-medium">Notification channels</Label>
                    <div className="space-y-2">
                      {CHANNEL_OPTIONS.map((option) => {
                        const Icon = option.icon
                        return (
                          <Button
                            key={option.value}
                            type="button"
                            variant={settings.channels.includes(option.value) ? "default" : "outline"}
                            className="w-full justify-start"
                            onClick={() => toggleChannel(option.value)}
                          >
                            <Icon className="w-4 h-4 mr-2" />
                            {option.label}
                          </Button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Custom Message */}
                  <div className="space-y-2">
                    <Label htmlFor="custom-message" className="text-sm font-medium">Custom message (optional)</Label>
                    <Textarea
                      id="custom-message"
                      placeholder="Add a custom note for the reminder..."
                      value={settings.custom_message || ""}
                      onChange={(e) => setSettings((prev) => ({ ...prev, custom_message: e.target.value || undefined }))}
                      rows={3}
                      className="w-full"
                    />
                  </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 border-t border-border flex justify-between">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={handleClear}
                    disabled={!settings.enabled || settings.offsets.length === 0}
                  >
                    Clear Reminders
                  </Button>
                  <div className="flex gap-2">
                    <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                      Cancel
                    </Button>
                    <Button
                      type="button"
                      onClick={handleSave}
                      disabled={settings.offsets.length === 0}
                    >
                      Save Reminders
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
