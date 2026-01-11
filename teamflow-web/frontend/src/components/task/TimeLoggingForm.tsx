"use client";

/**
 * TimeLoggingForm - Form for logging time entries (US5 T133).
 *
 * Features:
 * - Manual time entry input (duration in minutes)
 * - Quick select buttons (15m, 30m, 1h, 2h, 4h, 8h)
 * - Optional note field
 * - Date picker for entry date (defaults to today)
 * - Integration with useTimeTracking hook
 */

import { useState } from "react";
import { motion } from "framer-motion";
import { useTimeTracking, formatDuration, formatTimer } from "@/hooks/useTimeTracking";
import { Clock, Play, Pause, Save, X, Plus } from "lucide-react";

interface TimeLoggingFormProps {
  taskId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const QUICK_DURATIONS = [15, 30, 60, 120, 240, 480]; // 15m, 30m, 1h, 2h, 4h, 8h

export function TimeLoggingForm({
  taskId,
  onSuccess,
  onCancel,
}: TimeLoggingFormProps) {
  const { timer, timeEntries, submitTimerEntry, createTimeEntry, isCreating, start, stop, reset } =
    useTimeTracking(taskId);

  // Manual entry state
  const [manualMinutes, setManualMinutes] = useState<number>(0);
  const [note, setNote] = useState<string>("");
  const [entryDate, setEntryDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );

  // Handle quick duration selection
  const handleQuickDuration = (minutes: number) => {
    setManualMinutes(minutes);
  };

  // Handle manual duration change
  const handleDurationChange = (value: string) => {
    const minutes = parseInt(value, 10);
    setManualMinutes(isNaN(minutes) ? 0 : Math.max(0, minutes));
  };

  // Submit manual time entry
  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (manualMinutes <= 0) return;

    try {
      await createTimeEntry({
        task_id: taskId,
        duration_minutes: manualMinutes,
        note: note || undefined,
        entry_date: entryDate || undefined,
      });

      // Reset form
      setManualMinutes(0);
      setNote("");
      setEntryDate(new Date().toISOString().split("T")[0]);

      onSuccess?.();
    } catch {
      console.error("Failed to create time entry");
    }
  };

  // Handle timer toggle
  const handleTimerToggle = () => {
    if (!timer) return;
    if (timer.isRunning) {
      stop();
    } else {
      start(taskId);
    }
  };

  // Submit timer as time entry
  const handleTimerSubmit = async () => {
    try {
      await submitTimerEntry(note || undefined);
      onSuccess?.();
    } catch {
      console.error("Failed to submit timer entry");
    }
  };

  // Safely get timer state
  const timerState = timer;

  return (
    <div className="space-y-4">
      {/* Timer Section */}
      <div className="p-4 bg-muted/30 rounded-lg border border-border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Timer
          </h3>
          <div className="text-2xl font-mono font-semibold">
            {formatTimer(timerState?.elapsedSeconds || 0)}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleTimerToggle}
            className={`
              flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors
              ${
                timerState?.isRunning
                  ? "bg-muted text-foreground hover:bg-muted/80"
                  : "bg-accent text-accent-foreground hover:bg-accent-hover"
              }
            `}
          >
            {timerState?.isRunning ? (
              <>
                <Pause className="w-4 h-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Start
              </>
            )}
          </motion.button>

          {(timerState?.elapsedSeconds || 0) > 0 && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleTimerSubmit}
              disabled={isCreating}
              className="px-4 py-2 bg-accent text-accent-foreground hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save
            </motion.button>
          )}

          {(timerState?.elapsedSeconds || 0) > 0 && timer && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={reset}
              className="px-3 py-2 border border-border rounded-lg hover:bg-muted transition-colors text-foreground"
            >
              <X className="w-4 h-4" />
            </motion.button>
          )}
        </div>
      </div>

      {/* Manual Entry Section */}
      <form onSubmit={handleManualSubmit} className="space-y-4">
        {/* Quick Duration Buttons */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">
            Quick Select
          </label>
          <div className="grid grid-cols-6 gap-2">
            {QUICK_DURATIONS.map((duration) => (
              <motion.button
                key={duration}
                type="button"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleQuickDuration(duration)}
                className={`
                  px-2 py-2 text-sm rounded-lg border transition-colors
                  ${
                    manualMinutes === duration
                      ? "bg-accent text-accent-foreground border-accent"
                      : "bg-card border-border hover:bg-muted text-foreground"
                  }
                `}
              >
                {formatDuration(duration)}
              </motion.button>
            ))}
          </div>
        </div>

        {/* Manual Duration Input */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">
            Duration (minutes)
          </label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="1"
              value={manualMinutes || ""}
              onChange={(e) => handleDurationChange(e.target.value)}
              className="flex-1 px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-accent text-foreground"
              placeholder="Enter minutes"
            />
            <span className="text-sm text-muted-foreground">minutes</span>
          </div>
        </div>

        {/* Date Picker */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">
            Date
          </label>
          <input
            type="date"
            value={entryDate}
            onChange={(e) => setEntryDate(e.target.value)}
            className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-accent text-foreground"
          />
        </div>

        {/* Note Field */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">
            Note (optional)
          </label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            className="w-full px-3 py-2 border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-accent resize-none text-foreground"
            placeholder="What did you work on?"
            rows={2}
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-2">
          <motion.button
            type="submit"
            whileHover={{ scale: manualMinutes > 0 ? 1.01 : 1 }}
            whileTap={{ scale: manualMinutes > 0 ? 0.99 : 1 }}
            disabled={manualMinutes <= 0 || isCreating}
            className={`
              flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors
              ${
                manualMinutes > 0
                  ? "bg-accent text-accent-foreground hover:bg-accent-hover"
                  : "bg-muted text-muted-foreground cursor-not-allowed"
              }
            `}
          >
            <Plus className="w-4 h-4" />
            {isCreating ? "Adding..." : "Add Time Entry"}
          </motion.button>

          {onCancel && (
            <motion.button
              type="button"
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={onCancel}
              className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors text-foreground"
            >
              Cancel
            </motion.button>
          )}
        </div>
      </form>

      {/* Recent Time Entries */}
      {timeEntries && timeEntries.length > 0 && (
        <div className="space-y-2 pt-4 border-t border-border">
          <h4 className="text-sm font-medium text-muted-foreground">
            Recent Entries
          </h4>
          <div className="space-y-2">
            {timeEntries.slice(0, 3).map((entry: any) => (
              <div
                key={entry.id}
                className="flex items-center justify-between p-2 bg-muted/30 rounded-lg text-sm"
              >
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span className="font-medium">{formatDuration(entry.duration_minutes)}</span>
                  {entry.note && <span className="text-muted-foreground truncate max-w-[150px]">{entry.note}</span>}
                </div>
                <span className="text-muted-foreground">
                  {entry.entry_date || "Today"}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
