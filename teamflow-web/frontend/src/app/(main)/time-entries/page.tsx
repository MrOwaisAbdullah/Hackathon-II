"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Plus, Clock, Filter, X, Save, Pencil, Trash2, MoreVertical } from "lucide-react";
import {
  useTimeEntries,
  useTasks,
  useProjects,
  useCreateTimeEntry,
  useUpdateTimeEntry,
  useDeleteTimeEntry,
} from "@/lib/query";
import { useState } from "react";
import { toast } from "sonner";
import type { Project, Task } from "@/types";

// Helper function to format relative time without date-fns
const formatDistanceToNow = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return "just now";
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  return date.toLocaleDateString();
};

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

const QUICK_DURATIONS = [15, 30, 60, 120, 240, 480]; // 15m, 30m, 1h, 2h, 4h, 8h

export default function TimeEntriesPage() {
  const { data: timeEntries = [], isLoading: entriesLoading } = useTimeEntries();
  const { data: tasks = [] } = useTasks();
  const { data: projects = [] } = useProjects();
  const createTimeEntry = useCreateTimeEntry();
  const updateTimeEntry = useUpdateTimeEntry();
  const deleteTimeEntry = useDeleteTimeEntry();

  // Filter state
  const [filters, setFilters] = useState({
    taskFilter: "all", // all, or specific task ID
    projectFilter: "all", // all, or specific project ID
    timeRange: "all", // all, today, week, month
  });

  // Modal state
  const [showLogModal, setShowLogModal] = useState(false);
  const [editingEntryId, setEditingEntryId] = useState<string | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string>("");
  const [manualMinutes, setManualMinutes] = useState<number>(0);
  const [note, setNote] = useState<string>("");
  const [entryDate, setEntryDate] = useState<string>(
    new Date().toISOString().split("T")[0]
  );

  // Helper to get task name by ID
  const getTaskName = (taskId: string) => {
    const task = tasks.find((t: Task) => t.id === taskId);
    return task?.title || "Unknown Task";
  };

  // Helper to get project name by task ID
  const getProjectName = (taskId: string) => {
    const task = tasks.find((t: Task) => t.id === taskId);
    if (!task?.project_id) return "No Project";
    const project = projects.find((p: Project) => p.id === task.project_id);
    return project?.name || "Unknown Project";
  };

  // Handle edit entry
  const handleEditEntry = (entry: any) => {
    setEditingEntryId(entry.id);
    setSelectedTaskId(entry.task_id);
    setManualMinutes(entry.duration_minutes);
    setNote(entry.note || "");
    setEntryDate(entry.entry_date || new Date().toISOString().split("T")[0]);
    setShowLogModal(true);
  };

  // Handle delete entry
  const handleDeleteEntry = async (entryId: string, taskTitle: string) => {
    if (confirm(`Are you sure you want to delete this time entry for "${taskTitle}"?`)) {
      try {
        await deleteTimeEntry.mutateAsync(entryId);
        toast.success("Time entry deleted successfully");
      } catch {
        toast.error("Failed to delete time entry");
      }
    }
  };

  // Filter entries based on current filters
  const filteredEntries = timeEntries.filter((entry) => {
    // Task filter
    if (filters.taskFilter !== "all" && entry.task_id !== filters.taskFilter) {
      return false;
    }

    // Project filter
    if (filters.projectFilter !== "all") {
      const task = tasks.find((t: Task) => t.id === entry.task_id);
      if (task?.project_id !== filters.projectFilter) {
        return false;
      }
    }

    // Time range filter
    if (filters.timeRange !== "all") {
      const entryDate = new Date(entry.created_at);
      const now = new Date();
      const daysDiff = Math.floor((now.getTime() - entryDate.getTime()) / (1000 * 60 * 60 * 24));

      if (filters.timeRange === "today" && daysDiff > 0) return false;
      if (filters.timeRange === "week" && daysDiff > 7) return false;
      if (filters.timeRange === "month" && daysDiff > 30) return false;
    }

    return true;
  });

  // Calculate total hours for filtered entries
  const totalMinutes = filteredEntries.reduce((sum, entry) => sum + entry.duration_minutes, 0);
  const totalHours = totalMinutes / 60;

  // Format duration
  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins.toString().padStart(2, "0")}m`;
    }
    return `${mins}m`;
  };

  // Handle log time button click
  const handleLogTimeClick = () => {
    setEditingEntryId(null);
    setSelectedTaskId("");
    setManualMinutes(0);
    setNote("");
    setEntryDate(new Date().toISOString().split("T")[0]);
    setShowLogModal(true);
  };

  // Handle submit time entry (create or update)
  const handleSubmitTimeEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTaskId || manualMinutes <= 0) {
      toast.error("Please select a task and enter a duration");
      return;
    }

    try {
      if (editingEntryId) {
        // Update existing entry
        await updateTimeEntry.mutateAsync({
          entryId: editingEntryId,
          duration_minutes: manualMinutes,
          note: note || undefined,
          entry_date: entryDate || undefined,
        });
        toast.success("Time entry updated successfully");
      } else {
        // Create new entry
        await createTimeEntry.mutateAsync({
          task_id: selectedTaskId,
          duration_minutes: manualMinutes,
          note: note || undefined,
          entry_date: entryDate || undefined,
        });
        toast.success("Time entry logged successfully");
      }
      setShowLogModal(false);
      setEditingEntryId(null);
      setSelectedTaskId("");
      setManualMinutes(0);
      setNote("");
    } catch {
      toast.error(editingEntryId ? "Failed to update time entry" : "Failed to log time entry");
    }
  };

  // Handle modal close
  const handleCloseModal = () => {
    setShowLogModal(false);
    setEditingEntryId(null);
    setSelectedTaskId("");
    setManualMinutes(0);
    setNote("");
  };

  // Filter tasks by active status (not archived)
  const activeTasks = tasks.filter(t => t.status !== 'ARCHIVED');

  return (
    <div className="p-3 md:p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* T612: Header with flex-wrap for mobile */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6 md:mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Time Entries</h1>
            <p className="text-muted-foreground">Track time across projects</p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            {/* Filter Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="default">
                  <Filter className="w-4 h-4 mr-2" />
                  Filters
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Filter by Time Range</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuCheckboxItem
                  checked={filters.timeRange === "all"}
                  onCheckedChange={() => setFilters({ ...filters, timeRange: "all" })}
                >
                  All Time
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={filters.timeRange === "today"}
                  onCheckedChange={() => setFilters({ ...filters, timeRange: "today" })}
                >
                  Today
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={filters.timeRange === "week"}
                  onCheckedChange={() => setFilters({ ...filters, timeRange: "week" })}
                >
                  This Week
                </DropdownMenuCheckboxItem>
                <DropdownMenuCheckboxItem
                  checked={filters.timeRange === "month"}
                  onCheckedChange={() => setFilters({ ...filters, timeRange: "month" })}
                >
                  This Month
                </DropdownMenuCheckboxItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button onClick={handleLogTimeClick}>
                <Plus className="w-4 h-4 mr-2" />
                Log Time
              </Button>
            </motion.div>
          </div>
        </div>

        {/* Total Hours Card - Mobile padding */}
        <div className="mb-6 bg-card rounded-lg border border-border p-3 md:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-muted-foreground mb-1">
                {filters.timeRange === "all" ? "Total Hours" : `Total Hours (${filters.timeRange})`}
              </h3>
              <p className="text-4xl font-bold text-primary">{totalHours.toFixed(1)}h</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">
                {filteredEntries.length} {filteredEntries.length === 1 ? "entry" : "entries"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {formatDuration(totalMinutes)} total
              </p>
            </div>
          </div>
        </div>

        {/* Time Entries Table */}
        {entriesLoading ? (
          <div className="bg-card rounded-lg border border-border p-12 text-center">
            <p className="text-muted-foreground">Loading time entries...</p>
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="bg-card rounded-lg border border-border p-12 text-center">
            <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground mb-2">No time entries found</p>
            <p className="text-sm text-muted-foreground">
              {filters.timeRange !== "all" ? "Try adjusting your filters or " : ""}
              Start tracking time by logging your first entry
            </p>
          </div>
        ) : (
          <div className="bg-card rounded-lg border border-border overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium">Task</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Project</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Duration</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Note</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredEntries
                  .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                  .map((entry, i) => (
                    <motion.tr
                      key={entry.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: i * 0.03 }}
                      className="border-t border-border hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-6 py-4 font-medium">{getTaskName(entry.task_id)}</td>
                      <td className="px-6 py-4 text-muted-foreground">{getProjectName(entry.task_id)}</td>
                      <td className="px-6 py-4 font-medium">{formatDuration(entry.duration_minutes)}</td>
                      <td className="px-6 py-4 text-muted-foreground text-sm max-w-xs truncate">
                        {entry.note || "-"}
                      </td>
                      <td className="px-6 py-4 text-muted-foreground text-sm">
                        {entry.entry_date
                          ? new Date(entry.entry_date).toLocaleDateString()
                          : formatDistanceToNow(new Date(entry.created_at))
                        }
                      </td>
                      <td className="px-6 py-4">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem
                              onClick={() => handleEditEntry(entry)}
                              className="cursor-pointer"
                            >
                              <Pencil className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => handleDeleteEntry(entry.id, getTaskName(entry.task_id))}
                              className="cursor-pointer text-destructive focus:text-destructive"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </td>
                    </motion.tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>

      {/* Log Time Modal */}
      <AnimatePresence>
        {showLogModal && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-50"
              onClick={handleCloseModal}
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div
                className="bg-card rounded-lg border border-border shadow-xl max-w-md w-full p-6"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">
                    {editingEntryId ? "Edit Time Entry" : "Log Time Entry"}
                  </h2>
                  <button
                    onClick={handleCloseModal}
                    className="p-1 hover:bg-muted rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <form onSubmit={handleSubmitTimeEntry} className="space-y-4">
                  {/* Task Selection */}
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-foreground">Select Task *</label>
                    <select
                      value={selectedTaskId}
                      onChange={(e) => setSelectedTaskId(e.target.value)}
                      className="w-full px-4 py-3 text-foreground border-2 rounded-xl bg-background focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent transition-all duration-200 appearance-none cursor-pointer border-input hover:border-input/80 bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 fill=%22none%22 viewBox=%220 0 20 20%22%3E%3Cpath stroke=%22currentColor%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22 stroke-width=%221.5%22 d=%22M6 8l4 4 4-4%22/%3E%3C/svg%3E')] bg-[length:1.5em_1.5em] bg-[right_0.5rem_center] bg-no-repeat pr-10"
                      required
                    >
                      <option value="">Choose a task...</option>
                      {activeTasks.map((task) => (
                        <option key={task.id} value={task.id}>
                          {task.title}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Quick Duration Buttons */}
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-foreground">Duration *</label>
                    <div className="grid grid-cols-6 gap-2 mb-2">
                      {QUICK_DURATIONS.map((duration) => (
                        <motion.button
                          key={duration}
                          type="button"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => setManualMinutes(duration)}
                          className={`px-2 py-2 text-sm rounded-lg border transition-colors ${
                            manualMinutes === duration
                              ? "bg-accent text-accent-foreground border-accent"
                              : "bg-card border-input hover:bg-muted"
                          }`}
                        >
                          {formatDuration(duration)}
                        </motion.button>
                      ))}
                    </div>
                    <input
                      type="number"
                      min="1"
                      value={manualMinutes || ""}
                      onChange={(e) => setManualMinutes(parseInt(e.target.value) || 0)}
                      placeholder="Enter minutes"
                      className="w-full px-4 py-3 text-foreground border-2 rounded-xl bg-background focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent transition-all duration-200 border-input hover:border-input/80"
                      required
                    />
                  </div>

                  {/* Date */}
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-foreground">Date</label>
                    <input
                      type="date"
                      value={entryDate}
                      onChange={(e) => setEntryDate(e.target.value)}
                      className="w-full px-4 py-3 text-foreground border-2 rounded-xl bg-background focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent transition-all duration-200 border-input hover:border-input/80"
                    />
                  </div>

                  {/* Note */}
                  <div>
                    <label className="block text-sm font-semibold mb-2 text-foreground">Note (optional)</label>
                    <textarea
                      value={note}
                      onChange={(e) => setNote(e.target.value)}
                      placeholder="What did you work on?"
                      rows={2}
                      className="w-full px-4 py-3 text-foreground border-2 rounded-xl bg-background focus:outline-none focus:ring-4 focus:ring-accent/10 focus:border-accent transition-all duration-200 border-input hover:border-input/80 resize-none"
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-2">
                    <motion.button
                      type="submit"
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      disabled={createTimeEntry.isPending || updateTimeEntry.isPending}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-accent text-accent-foreground rounded-lg hover:bg-accent-hover disabled:opacity-50 font-medium transition-colors"
                    >
                      <Save className="w-4 h-4" />
                      {createTimeEntry.isPending || updateTimeEntry.isPending
                        ? "Saving..."
                        : editingEntryId
                        ? "Update Entry"
                        : "Save Entry"}
                    </motion.button>
                    <motion.button
                      type="button"
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      onClick={handleCloseModal}
                      disabled={createTimeEntry.isPending || updateTimeEntry.isPending}
                      className="px-4 py-2 border border-input rounded-lg hover:bg-muted transition-colors"
                    >
                      Cancel
                    </motion.button>
                  </div>
                </form>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
