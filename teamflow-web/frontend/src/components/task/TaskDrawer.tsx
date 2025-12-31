"use client";

/** TaskDrawer - Side panel for viewing/editing task details.
 *
 * This component follows the incremental enhancement pattern:
 * - T033a (Foundational): Basic shell with slide-in animation
 * - T103 (US3): Add assignee dropdown
 * - T134 (US5): Add time entries section
 * - T147 (US6): Add archive button
 */

import { AnimatePresence, motion } from "framer-motion";

interface TaskDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  taskId?: string;
}

export function TaskDrawer({ isOpen, onClose, taskId }: TaskDrawerProps) {
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
            className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-xl z-50"
          >
            <div className="flex h-full flex-col">
              {/* Header */}
              <div className="flex items-center justify-between border-b p-4">
                <h2 className="text-lg font-semibold">Task Details</h2>
                <button
                  onClick={onClose}
                  className="rounded p-2 hover:bg-gray-100"
                  aria-label="Close drawer"
                >
                  <svg
                    className="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              {/* Content - Will be enhanced in later phases */}
              <div className="flex-1 overflow-y-auto p-4">
                {taskId ? (
                  <div className="space-y-4">
                    <p className="text-sm text-gray-500">
                      Task details will be displayed here.
                    </p>
                    <p className="text-xs text-gray-400">
                      Task ID: {taskId}
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">
                    Select a task to view details
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
