"""
T084: ReminderSettings Component

A dialog component for configuring reminder settings for tasks.
Supports multiple offset selections, notification channels, and custom messages.
"""

"use client"

import { useState } from "react"
import { Bell, Mail, Smartphone } from "lucide-react"
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
  const [settings, setSettings] = useState<ReminderSettingsData>(
    initialSettings || {
      enabled: false,
      offsets: [],
      channels: ["email"],
      custom_message: undefined,
    }
  )

  const handleSave = () => {
    onSave(settings)
    setOpen(false)
  }

  const handleClear = () => {
    setSettings({
      enabled: false,
      offsets: [],
      channels: ["email"],
      custom_message: undefined,
    })
    onSave(settings)
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
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Set Reminders
          </DialogTitle>
          <DialogDescription>
            Configure when and how to be notified before this task is due
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Reminder Offsets */}
          <div className="space-y-3">
            <Label>Remind me</Label>
            <div className="flex flex-wrap gap-2">
              {OFFSET_OPTIONS.map((option) => (
                <Button
                  key={option.value}
                  type="button"
                  variant={settings.offsets.includes(option.value) ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleOffset(option.value)}
                  className="flex-shrink-0"
                >
                  {option.label}
                </Button>
              ))}
            </div>
            {settings.offsets.length === 0 && (
              <p className="text-xs text-muted-foreground">
                Select at least one reminder time
              </p>
            )}
          </div>

          {/* Notification Channels */}
          <div className="space-y-3">
            <Label>Notification channels</Label>
            <div className="flex flex-wrap gap-2">
              {CHANNEL_OPTIONS.map((option) => {
                const Icon = option.icon
                return (
                  <Button
                    key={option.value}
                    type="button"
                    variant={settings.channels.includes(option.value) ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleChannel(option.value)}
                    className="flex items-center gap-2"
                  >
                    <Icon className="h-4 w-4" />
                    {option.label}
                  </Button>
                )
              })}
            </div>
          </div>

          {/* Custom Message */}
          <div className="space-y-2">
            <Label htmlFor="custom-message">Custom message (optional)</Label>
            <Textarea
              id="custom-message"
              placeholder="Add a custom note to include in the reminder..."
              value={settings.custom_message || ""}
              onChange={(e) =>
                setSettings((prev) => ({
                  ...prev,
                  enabled: true,
                  custom_message: e.target.value || undefined,
                }))
              }
              rows={3}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              This message will be included in the reminder notification
            </p>
          </div>
        </div>

        <DialogFooter className="flex justify-between">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClear}
            disabled={!settings.enabled && settings.offsets.length === 0}
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
              disabled={settings.offsets.length === 0 || settings.channels.length === 0}
            >
              Save Reminders
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
