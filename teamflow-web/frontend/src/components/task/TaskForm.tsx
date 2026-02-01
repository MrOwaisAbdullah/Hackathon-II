"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Plus, Sparkles, RefreshCw, Bell } from "lucide-react";
import { useCreateTask, useUsers, useProjects } from "@/lib/query";
import { TaskPriority } from "@/types";
import { useState } from "react";
import { PrioritySelector } from "./PrioritySelector";
import { RichTextEditor } from "./RichTextEditor";
import { AssigneeSelect } from "./AssigneeSelect";
import { ProjectSelect } from "./ProjectSelect";
import { DatePicker } from "./DatePicker";
import { RecurrenceDialog } from "@/components/tasks/RecurrenceDialog";
import { ReminderSettings } from "@/components/notifications/ReminderSettings";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface TaskFormProps {
  columnId?: string;
  onClose: () => void;
}

export function TaskForm({ columnId = "TODO", onClose }: TaskFormProps) {
  const createTask = useCreateTask();
  const { data: users = [] } = useUsers();
  const { data: projects = [] } = useProjects();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TaskPriority>(TaskPriority.MEDIUM);
  const [dueDate, setDueDate] = useState<string | undefined>("");
  const [assigneeId, setAssigneeId] = useState("");
  const [projectId, setProjectId] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);

  // T055, T056: Phase 5 - Recurrence state
  const [recurrenceRule, setRecurrenceRule] = useState<{
    frequency: "daily" | "weekly" | "monthly" | "yearly" | null
    interval: number
    daysOfWeek: string[]
    dayOfMonth: number | null
    endDate: string | null
    timeOfDay: string | null
  }>({
    frequency: null,
    interval: 1,
    daysOfWeek: [],
    dayOfMonth: null,
    endDate: null,
    timeOfDay: null,
  });

  // T056: Handler for saving recurrence rule
  const handleRecurrenceSave = (rule: typeof recurrenceRule) => {
    setRecurrenceRule(rule);
  };

  // T056: Get recurrence display text
  const getRecurrenceDisplay = () => {
    if (!recurrenceRule.frequency) return null;
    const parts = [];
    if (recurrenceRule.interval > 1) {
      parts.push(`Every ${recurrenceRule.interval}`);
    }
    parts.push(recurrenceRule.frequency.slice(0, -2) + "ly"); // daily, weekly, etc.
    return parts.join(" ");
  };

  // T085, T086: Phase 5 - Reminder state
  const [reminderSettings, setReminderSettings] = useState<{
    enabled: boolean
    offsets: string[]
    channels: string[]
    custom_message?: string
  }>({
    enabled: false,
    offsets: [],
    channels: ["email"],
    custom_message: undefined,
  });

  // T085: Handler for saving reminder settings
  const handleReminderSave = (settings: typeof reminderSettings) => {
    setReminderSettings(settings);
  };

  // T086: Get reminder display text
  const getReminderDisplay = () => {
    if (!reminderSettings.enabled || reminderSettings.offsets.length === 0) return null;
    const offsetLabels: Record<string, string> = {
      "15m": "15 min",
      "1h": "1 hour",
      "1d": "1 day",
      "1w": "1 week",
    };
    const labels = reminderSettings.offsets.map(o => offsetLabels[o] || o).join(", ");
    return `${labels} before`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      await createTask.mutateAsync({
        title: title.trim(),
        description: description.trim() || undefined,
        status: columnId as any,
        priority,
        due_date: dueDate || undefined,
        assignee_id: assigneeId || undefined,
        project_id: projectId || undefined,
        // T056: Include recurrence rule if set
        recurrence_rule: recurrenceRule.frequency ? recurrenceRule : undefined,
        // T087: Include reminder settings if enabled
        reminder_settings: reminderSettings.enabled ? reminderSettings : undefined,
      });

      // Reset form
      setTitle("");
      setDescription("");
      setPriority(TaskPriority.MEDIUM);
      setDueDate("");
      setAssigneeId("");
      setProjectId("");
      // T056: Reset recurrence rule
      setRecurrenceRule({
        frequency: null,
        interval: 1,
        daysOfWeek: [],
        dayOfMonth: null,
        endDate: null,
        timeOfDay: null,
      });
      // T085: Reset reminder settings
      setReminderSettings({
        enabled: false,
        offsets: [],
        channels: ["email"],
        custom_message: undefined,
      });

      // Close modal
      onClose();
    } catch {
      console.error("Failed to create task");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="absolute inset-0 bg-black/20 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: "spring", duration: 0.5, bounce: 0.3 }}
          className={cn(
            "relative w-full bg-card rounded-2xl border border-border shadow-2xl overflow-hidden",
            "max-w-3xl h-full sm:h-auto sm:max-h-[95vh]"
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header with gradient */}
          <div className="relative bg-gradient-to-r from-lime-50 to-emerald-50 dark:from-lime-950/20 dark:to-emerald-950/20 px-6 py-5 border-b border-border">
            {/* Decorative element */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-lime-400/10 to-transparent rounded-bl-full" />

            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-3">
                <motion.div
                  initial={{ rotate: -180, scale: 0 }}
                  animate={{ rotate: 0, scale: 1 }}
                  transition={{ type: "spring", delay: 0.2, stiffness: 200 }}
                  className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-lime-400 to-lime-500 text-black shadow-lg shadow-lime-500/20"
                >
                  <Sparkles className="w-5 h-5" />
                </motion.div>
                <div>
                  <h2 className="text-lg font-bold text-foreground">Create New Task</h2>
                  <p className="text-xs text-muted-foreground">Add a new task to your board</p>
                </div>
              </div>
              <motion.button
                whileHover={{ rotate: 90, scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onClose}
                className="p-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </motion.button>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto max-h-[calc(95vh-140px)] scrollbar-lime">
            {/* Title */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="space-y-2"
            >
              <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <span>Title</span>
                <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="What needs to be done?"
                onFocus={() => setFocusedField("title")}
                onBlur={() => setFocusedField(null)}
                className={cn(
                  "w-full px-4 py-3 bg-background border-2 rounded-xl",
                  "focus:outline-none focus:ring-0 transition-all duration-200",
                  "placeholder:text-muted-foreground/50",
                  focusedField === "title"
                    ? "border-accent ring-4 ring-accent/10"
                    : "border-input hover:border-input/80"
                )}
                autoFocus
                required
              />
            </motion.div>

            {/* Description - Rich Text Editor */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 }}
              className="space-y-2"
            >
              <label className="text-sm font-semibold text-foreground">
                Description
              </label>
              <RichTextEditor
                value={description}
                onChange={setDescription}
                placeholder="Add more details... Supports Markdown!"
              />
            </motion.div>

            {/* Priority - Full Width */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="space-y-2"
            >
              <label className="text-sm font-semibold text-foreground">
                Priority
              </label>
              <PrioritySelector
                value={priority}
                onChange={(p) => setPriority(p)}
              />
            </motion.div>

            {/* Due Date - Full Width */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.25 }}
            >
              <DatePicker
                value={dueDate}
                onChange={setDueDate}
              />
            </motion.div>

            {/* T056: Recurrence - Full Width */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.26 }}
              className="space-y-2"
            >
              <label className="text-sm font-semibold text-foreground">
                Recurrence (Optional)
              </label>
              <RecurrenceDialog
                onSave={handleRecurrenceSave}
                initialRule={recurrenceRule}
                trigger={
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    className={cn(
                      "w-full px-4 py-3 bg-background border-2 rounded-xl",
                      "flex items-center justify-between gap-3",
                      "focus:outline-none focus:ring-0 transition-all duration-200",
                      "hover:border-input/80",
                      recurrenceRule.frequency
                        ? "border-accent/50 ring-2 ring-accent/10"
                        : "border-input"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <RefreshCw className={cn(
                        "w-4 h-4",
                        recurrenceRule.frequency ? "text-accent" : "text-muted-foreground"
                      )} />
                      <span className="text-sm">
                        {recurrenceRule.frequency
                          ? getRecurrenceDisplay()
                          : "Set repeat schedule..."}
                      </span>
                    </div>
                    {recurrenceRule.frequency && (
                      <span className="text-xs text-accent bg-accent/10 px-2 py-1 rounded-md">
                        Active
                      </span>
                    )}
                  </motion.button>
                }
              />
            </motion.div>

            {/* T085, T086: Reminders - Full Width */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.27 }}
              className="space-y-2"
            >
              <label className="text-sm font-semibold text-foreground">
                Reminders (Optional)
              </label>
              <ReminderSettings
                onSave={handleReminderSave}
                initialSettings={reminderSettings}
                trigger={
                  <motion.button
                    type="button"
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                    className={cn(
                      "w-full px-4 py-3 bg-background border-2 rounded-xl",
                      "flex items-center justify-between gap-3",
                      "focus:outline-none focus:ring-0 transition-all duration-200",
                      "hover:border-input/80",
                      reminderSettings.enabled && reminderSettings.offsets.length > 0
                        ? "border-blue-500/50 ring-2 ring-blue-500/10"
                        : "border-input"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <Bell className={cn(
                        "w-4 h-4",
                        reminderSettings.enabled && reminderSettings.offsets.length > 0 ? "text-blue-500" : "text-muted-foreground"
                      )} />
                      <span className="text-sm">
                        {reminderSettings.enabled && reminderSettings.offsets.length > 0
                          ? getReminderDisplay()
                          : "Set reminders..."}
                      </span>
                    </div>
                    {reminderSettings.enabled && reminderSettings.offsets.length > 0 && (
                      <span className="text-xs text-blue-500 bg-blue-500/10 px-2 py-1 rounded-md">
                        Active
                      </span>
                    )}
                  </motion.button>
                }
              />
            </motion.div>

            {/* Two Column Grid: Assignee & Project */}
            <div className="grid grid-cols-1 gap-4">
              {/* Assignee with Avatar */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <AssigneeSelect
                  users={users}
                  value={assigneeId || null}
                  onChange={(val) => setAssigneeId(val || "")}
                  label="Assign To"
                  placeholder="Unassigned"
                />
              </motion.div>

              {/* Project */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.35 }}
              >
                <ProjectSelect
                  projects={projects}
                  value={projectId || null}
                  onChange={(val) => setProjectId(val || "")}
                  placeholder="No Project"
                />
              </motion.div>
            </div>

            {/* Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex gap-3 pt-4"
            >
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="flex-1">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={onClose}
                  disabled={isSubmitting}
                  className="w-full"
                >
                  Cancel
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="flex-1">
                <Button
                  type="submit"
                  disabled={isSubmitting || !title.trim()}
                  className="w-full"
                >
                  {isSubmitting ? (
                    <>
                      <motion.span
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        ⏳
                      </motion.span>
                      Creating...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      Create Task
                    </>
                  )}
                </Button>
              </motion.div>
            </motion.div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
