"use client";

/** TaskDrawer - Side panel for viewing/editing task details.
 *
 * This component follows the incremental enhancement pattern:
 * - T033a (Foundational): Basic shell with slide-in animation
 * - T103 (US3): Add assignee dropdown
 * - T143 (US6): Rich editing with priority, date picker, description editor
 * - T147 (US6): Archive button with confirmation modal
 * - T134 (US5): Time entries section with logging form
 */

import { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  useTask,
  useUpdateTask,
  useAssignTask,
  useArchiveTask,
  useUsers,
} from "@/lib/query";
import { AssigneeAvatar } from "./AssigneeAvatar";
import { PrioritySelector } from "./PrioritySelector";
import { DatePicker } from "./DatePicker";
import { RichTextEditor } from "./RichTextEditor";
import { TimeLoggingForm } from "./TimeLoggingForm";
import { useTimeTracking, formatDuration } from "@/hooks/useTimeTracking";
import {
  ChevronDown,
  User,
  Loader2,
  Archive,
  X,
  AlertTriangle,
  Clock,
  ChevronDown as ChevronDownIcon,
} from "lucide-react";
import type { TaskPriority } from "@/types/task";

interface TaskDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  taskId?: string;
}

export function TaskDrawer({ isOpen, onClose, taskId }: TaskDrawerProps) {
  const { data: task, isLoading: isLoadingTask } = useTask(taskId || "");
  const { data: users = [], isLoading: isLoadingUsers } = useUsers();
  const updateTask = useUpdateTask();
  const assignTask = useAssignTask();
  const archiveTask = useArchiveTask();

  const [isAssigneeDropdownOpen, setIsAssigneeDropdownOpen] = useState(false);
  const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false);
  const [isTimeLoggingFormOpen, setIsTimeLoggingFormOpen] = useState(false);

  // Local state for editing
  const [editedTitle, setEditedTitle] = useState("");
  const [editedDescription, setEditedDescription] = useState("");
  const [editedPriority, setEditedPriority] = useState<TaskPriority | null>();
  const [editedDueDate, setEditedDueDate] = useState<string | undefined>();

  // Time tracking hook (US5 T134)
  const { timeEntries, formattedTime, refetchTotalTime } = useTimeTracking(taskId);

  // Sync local state with task data whenever task changes
  useEffect(() => {
    if (task) {
      setEditedTitle(task.title);
      setEditedDescription(task.description || "");
      setEditedPriority(task.priority);
      setEditedDueDate(task.due_date);
    }
  }, [task]);

  const handleAssigneeChange = async (assigneeId: string | null) => {
    if (!taskId) return;

    if (assigneeId) {
      await assignTask.mutateAsync({
        taskId,
        assigneeId,
      });
    }
    setIsAssigneeDropdownOpen(false);
  };

  const handleSave = async () => {
    if (!taskId || !task) return;

    await updateTask.mutateAsync({
      id: taskId,
      data: {
        title: editedTitle,
        description: editedDescription || undefined,
        priority: editedPriority || undefined,
        due_date: editedDueDate,
      },
    });

    onClose();
  };

  const handleArchive = async () => {
    if (!taskId) return;

    await archiveTask.mutateAsync(taskId);
    setIsArchiveModalOpen(false);
    onClose();
  };

  // Helper to normalize dates for comparison (handle null/undefined/empty strings)
  const normalizeDate = (date: string | undefined | null): string | undefined => {
    if (!date) return undefined;
    // Extract just the date part (YYYY-MM-DD) for comparison
    return date.split('T')[0];
  };

  const hasChanges = task && (
    editedTitle !== task.title ||
    editedDescription !== (task.description || "") ||
    editedPriority !== task.priority ||
    normalizeDate(editedDueDate) !== normalizeDate(task.due_date)
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-card shadow-xl z-50"
            data-testid="task-drawer"
          >
            <div className="flex h-full flex-col">
              {/* Header - T605: Mobile padding optimization */}
              <div className="flex items-center justify-between border-b border-border p-3 md:p-4">
                <h2 className="text-lg font-semibold">Task Details</h2>
                <button
                  onClick={onClose}
                  className="rounded p-2 hover:bg-muted"
                  aria-label="Close drawer"
                  data-testid="close-drawer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content - T605: Mobile padding optimization */}
              <div className="flex-1 overflow-y-auto p-3 md:p-4 scrollbar-lime">
                {isLoadingTask ? (
                  <div className="flex items-center justify-center h-full">
                    <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                  </div>
                ) : task ? (
                  <div className="space-y-6">
                    {/* Title - Editable */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Title
                      </label>
                      <input
                        type="text"
                        name="title"
                        value={editedTitle}
                        onChange={(e) => setEditedTitle(e.target.value)}
                        className="w-full px-3 py-2 border-2 border-input rounded-xl bg-background focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent hover:border-input/80"
                        placeholder="Task title"
                      />
                    </div>

                    {/* Description - Rich Text Editor */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">
                        Description
                      </label>
                      <RichTextEditor
                        value={editedDescription}
                        onChange={setEditedDescription}
                        placeholder="Add a detailed description..."
                      />
                    </div>

                    {/* Assignee Section (T103) */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                        <User className="w-4 h-4" />
                        Assignee
                      </label>

                      <div className="relative" data-testid="assignee-section">
                        {/* Trigger Button */}
                        <motion.button
                          whileHover={{ scale: 1.01 }}
                          whileTap={{ scale: 0.99 }}
                          onClick={() => setIsAssigneeDropdownOpen(!isAssigneeDropdownOpen)}
                          className="w-full flex items-center justify-between gap-3 px-3 py-2 bg-muted/30 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                          data-testid="assignee-dropdown"
                        >
                          <div className="flex items-center gap-3">
                            <AssigneeAvatar
                              name={task.assignee?.name}
                              email={task.assignee?.email}
                              size="md"
                            />
                            <span className="text-sm font-medium">
                              {task.assignee?.name || "Unassigned"}
                            </span>
                          </div>
                          <ChevronDown
                            className={`w-4 h-4 text-muted-foreground transition-transform ${
                              isAssigneeDropdownOpen ? "rotate-180" : ""
                            }`}
                          />
                        </motion.button>

                        {/* Dropdown */}
                        <AnimatePresence>
                          {isAssigneeDropdownOpen && (
                            <>
                              {/* Backdrop */}
                              <div
                                className="fixed inset-0 z-10"
                                onClick={() => setIsAssigneeDropdownOpen(false)}
                              />

                              {/* Dropdown Menu */}
                              <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.15 }}
                                className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-lg z-20 overflow-hidden"
                              >
                                <div className="p-1">
                                  {/* Unassigned */}
                                  <button
                                    onClick={() => handleAssigneeChange(null)}
                                    className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/50 transition-colors text-left"
                                    data-testid="assignee-option"
                                  >
                                    <div className="w-7 h-7 rounded-full border-2 border-dashed border-muted-foreground/30" />
                                    <span className="text-sm">Unassigned</span>
                                    {!task.assignee_id && (
                                      <span className="ml-auto text-xs text-accent">
                                        Current
                                      </span>
                                    )}
                                  </button>

                                  {/* Team Members */}
                                  {isLoadingUsers ? (
                                    <div className="px-3 py-2 text-sm text-muted-foreground">
                                      Loading team members...
                                    </div>
                                  ) : (
                                    users.map((user) => (
                                      <button
                                        key={user.id}
                                        onClick={() => handleAssigneeChange(user.id)}
                                        className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/50 transition-colors text-left"
                                        data-testid="assignee-option"
                                      >
                                        <AssigneeAvatar
                                          name={user.name}
                                          email={user.email}
                                          size="md"
                                        />
                                        <span className="text-sm font-medium">{user.name}</span>
                                        {task.assignee_id === user.id && (
                                          <span className="ml-auto text-xs text-accent">
                                            Current
                                          </span>
                                        )}
                                      </button>
                                    ))
                                  )}
                                </div>
                              </motion.div>
                            </>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>

                    {/* Status - Full Width (Read-only) */}
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">
                        Status
                      </div>
                      <div className="px-3 py-2 bg-muted/30 rounded-lg text-sm">
                        {task.status}
                      </div>
                    </div>

                    {/* Priority - Full Width (Editable) */}
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">
                        Priority
                      </div>
                      <PrioritySelector
                        value={editedPriority}
                        onChange={setEditedPriority}
                      />
                    </div>

                    {/* Due Date - Editable (T146) */}
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">
                        Due Date
                      </div>
                      <DatePicker
                        value={editedDueDate}
                        onChange={setEditedDueDate}
                      />
                    </div>

                    {/* Time Entries Section (US5 T134) */}
                    <div className="space-y-3 pt-4 border-t border-border">
                      <div className="flex items-center justify-between">
                        <div className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          Time Tracked
                        </div>
                        <span className="text-lg font-semibold">{formattedTime}</span>
                      </div>

                      {/* Time Entries List (Collapsible) */}
                      <div className="space-y-2">
                        <motion.button
                          whileHover={{ scale: 1.01 }}
                          whileTap={{ scale: 0.99 }}
                          onClick={() => setIsTimeLoggingFormOpen(!isTimeLoggingFormOpen)}
                          className="w-full flex items-center justify-between px-3 py-2 bg-muted/30 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <span className="text-sm font-medium">
                            {timeEntries?.length || 0} entries
                          </span>
                          <ChevronDownIcon
                            className={`w-4 h-4 text-muted-foreground transition-transform ${
                              isTimeLoggingFormOpen ? "rotate-180" : ""
                            }`}
                          />
                        </motion.button>

                        <AnimatePresence>
                          {isTimeLoggingFormOpen && taskId && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: "auto" }}
                              exit={{ opacity: 0, height: 0 }}
                              transition={{ duration: 0.2 }}
                              className="overflow-hidden"
                            >
                              <div className="p-4 bg-muted/20 rounded-lg border border-border space-y-4">
                                {/* Time Logging Form */}
                                <TimeLoggingForm
                                  taskId={taskId}
                                  onSuccess={() => {
                                    refetchTotalTime();
                                  }}
                                />

                                {/* Existing Time Entries */}
                                {timeEntries &&
                                  timeEntries.length > 0 && (
                                  <div className="space-y-2 pt-4 border-t border-border">
                                    <h4 className="text-sm font-medium text-muted-foreground">
                                      All Entries
                                    </h4>
                                    <div className="space-y-2 max-h-[200px] overflow-y-auto">
                                      {timeEntries.map((entry) => (
                                        <div
                                          key={entry.id}
                                          className="flex items-start justify-between p-2 bg-background rounded-lg text-sm"
                                        >
                                          <div className="flex-1">
                                            <div className="flex items-center gap-2">
                                              <Clock className="w-3 h-3 text-muted-foreground" />
                                              <span className="font-medium">
                                                {formatDuration(entry.duration_minutes)}
                                              </span>
                                            </div>
                                            {entry.note && (
                                              <p className="text-muted-foreground text-xs mt-1 line-clamp-2">
                                                {entry.note}
                                              </p>
                                            )}
                                          </div>
                                          <span className="text-muted-foreground text-xs">
                                            {entry.entry_date || "Today"}
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>

                      {/* Quick Add Button */}
                      {!isTimeLoggingFormOpen && (
                        <motion.button
                          whileHover={{ scale: 1.01 }}
                          whileTap={{ scale: 0.99 }}
                          onClick={() => setIsTimeLoggingFormOpen(true)}
                          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-accent/10 text-accent hover:bg-accent/20 border border-accent/30 rounded-lg transition-colors"
                        >
                          <Clock className="w-4 h-4" />
                          <span className="text-sm font-medium">Log Time</span>
                        </motion.button>
                      )}
                    </div>

                    {/* Archive Button (T147) */}
                    <div className="pt-4 border-t border-border">
                      <motion.button
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                        onClick={() => setIsArchiveModalOpen(true)}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 text-destructive hover:bg-destructive/10 border border-destructive/30 rounded-lg transition-colors"
                        data-testid="archive-button"
                      >
                        <Archive className="w-4 h-4" />
                        <span className="text-sm font-medium">Archive Task</span>
                      </motion.button>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">
                    {taskId ? "Task not found" : "Select a task to view details"}
                  </p>
                )}
              </div>

              {/* Footer with Save Button */}
              {task && (
                <div className="flex items-center gap-3 p-4 border-t border-border">
                  <button
                    onClick={onClose}
                    className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    Cancel
                  </button>
                  <motion.button
                    whileHover={{ scale: hasChanges ? 1.01 : 1 }}
                    whileTap={{ scale: hasChanges ? 0.99 : 1 }}
                    onClick={handleSave}
                    disabled={!hasChanges || updateTask.isPending}
                    className={`
                      flex-1 px-4 py-2 rounded-lg font-medium transition-colors
                      ${hasChanges
                        ? "bg-accent text-accent-foreground hover:bg-accent-hover"
                        : "bg-muted text-muted-foreground cursor-not-allowed"
                      }
                    `}
                  >
                    {updateTask.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin mx-auto" />
                    ) : (
                      "Save Changes"
                    )}
                  </motion.button>
                </div>
              )}
            </div>
          </motion.div>

          {/* Archive Confirmation Modal (T147) */}
          <AnimatePresence>
            {isArchiveModalOpen && (
              <>
                {/* Backdrop */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsArchiveModalOpen(false)}
                  className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50"
                />

                {/* Modal */}
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-card border border-border rounded-lg shadow-xl max-w-sm w-full"
                    data-testid="archive-modal"
                  >
                    <div className="p-6">
                      {/* Icon */}
                      <div className="flex items-center justify-center w-12 h-12 rounded-full bg-destructive/10 mx-auto mb-4">
                        <Archive className="w-6 h-6 text-destructive" />
                      </div>

                      {/* Title */}
                      <h3 className="text-lg font-semibold text-center mb-2">
                        Archive Task?
                      </h3>

                      {/* Message */}
                      <p className="text-sm text-muted-foreground text-center mb-6">
                        Are you sure you want to archive "{task?.title}"? The task
                        will be hidden from the board but can be restored later.
                      </p>

                      {/* Actions */}
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => setIsArchiveModalOpen(false)}
                          className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
                        >
                          Cancel
                        </button>
                        <motion.button
                          whileHover={{ scale: 1.01 }}
                          whileTap={{ scale: 0.99 }}
                          onClick={handleArchive}
                          disabled={archiveTask.isPending}
                          className="flex-1 px-4 py-2 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors flex items-center justify-center gap-2"
                        >
                          {archiveTask.isPending ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <>
                              <AlertTriangle className="w-4 h-4" />
                              Archive
                            </>
                          )}
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </>
            )}
          </AnimatePresence>
        </>
      )}
    </AnimatePresence>
  );
}
