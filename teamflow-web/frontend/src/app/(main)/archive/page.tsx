"use client";

/** Archive Page - View and restore archived tasks.
 *
 * Task T148 (US6): Archive page with:
 * - List of archived tasks
 * - Restore functionality
 * - Search/filter
 * - Empty state
 */

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useArchivedTasks, useRestoreTask } from "@/lib/query";
import { Search, RotateCcw, Archive, Loader2 } from "lucide-react";

export default function ArchivePage() {
  const { data: archivedTasks = [], isLoading } = useArchivedTasks();
  const restoreTask = useRestoreTask();
  const [searchQuery, setSearchQuery] = useState("");
  const [restoringId, setRestoringId] = useState<string | null>(null);

  const filteredTasks = archivedTasks.filter((task) =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRestore = async (taskId: string) => {
    setRestoringId(taskId);
    try {
      await restoreTask.mutateAsync(taskId);
    } finally {
      setRestoringId(null);
    }
  };

  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Archived Tasks</h1>
            <p className="text-muted-foreground">
              View and restore archived tasks ({archivedTasks.length} total)
            </p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search archived tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-card focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : filteredTasks.length > 0 ? (
          /* Archived Tasks List */
          <div className="space-y-4">
            <AnimatePresence>
              {filteredTasks.map((task, i) => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: Math.min(i * 0.05, 0.3) }}
                  className="bg-card rounded-lg border border-border p-6 hover:shadow-md transition-shadow"
                  data-testid="archived-task-card"
                >
                  <div className="flex items-center justify-between gap-4">
                    {/* Task Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-lg truncate">{task.title}</h3>
                        {task.priority && (
                          <span className={`px-2 py-0.5 text-xs rounded-full ${
                            task.priority === 'HIGH'
                              ? 'bg-red-500/10 text-red-500'
                              : task.priority === 'MEDIUM'
                              ? 'bg-yellow-500/10 text-yellow-500'
                              : 'bg-blue-500/10 text-blue-500'
                          }`}>
                            {task.priority}
                          </span>
                        )}
                      </div>
                      {task.description && (
                        <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                          {task.description}
                        </p>
                      )}
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span>Archived: {new Date(task.updated_at || new Date()).toLocaleDateString()}</span>
                        {(task as any).due_date && (
                          <span>Due: {new Date((task as any).due_date).toLocaleDateString()}</span>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 shrink-0">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleRestore(task.id)}
                        disabled={restoringId === task.id || restoreTask.isPending}
                        className="flex items-center gap-2 px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
                        data-testid="restore-button"
                      >
                        {restoringId === task.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <RotateCcw className="w-4 h-4" />
                            Restore
                          </>
                        )}
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        ) : (
          /* Empty State */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
            data-testid="empty-archive"
          >
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-muted mx-auto mb-4">
              <Archive className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">
              {searchQuery ? "No archived tasks found" : "No archived tasks"}
            </h3>
            <p className="text-sm text-muted-foreground">
              {searchQuery
                ? "Try a different search term"
                : "Archived tasks will appear here for you to restore."}
            </p>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
