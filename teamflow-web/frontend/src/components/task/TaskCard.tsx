"use client";

/** TaskCard - Draggable task card for Kanban board.
 *
 * Displays task title, priority indicator, and assignee avatar.
 * Clicking opens the TaskDrawer for details.
 */

import { useDraggable } from "@dnd-kit/core";
import { motion } from "framer-motion";
import type { Task, TaskPriority } from "@/types";

interface TaskCardProps {
  task: Task;
  onClick: () => void;
}

const priorityColors: Record<TaskPriority, string> = {
  low: "bg-muted text-muted-foreground",
  medium: "bg-primary/10 text-primary",
  high: "bg-destructive/10 text-destructive",
};

const priorityLabels: Record<TaskPriority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export function TaskCard({ task, onClick }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, isDragging, transform } = useDraggable({
    id: task.id,
  });

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined;

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`bg-card rounded-lg p-4 shadow-sm border border-border cursor-pointer hover:shadow-md transition-shadow ${
        isDragging ? "opacity-50" : ""
      }`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Task Title */}
      <h3 className="font-medium text-foreground mb-2 line-clamp-2">
        {task.title}
      </h3>

      {/* Task Description (truncated) */}
      {task.description && (
        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
          {task.description}
        </p>
      )}

      {/* Footer: Priority and Assignee */}
      <div className="flex items-center justify-between">
        {/* Priority Badge */}
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            priorityColors[task.priority]
          }`}
        >
          {priorityLabels[task.priority]}
        </span>

        {/* Assignee Avatar (placeholder for now) */}
        {task.assignee_id ? (
          <div className="w-6 h-6 rounded-full bg-accent flex items-center justify-center">
            <span className="text-xs text-accent-foreground font-medium">
              {String(task.assignee_id)[0].toUpperCase()}
            </span>
          </div>
        ) : (
          <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center">
            <svg
              className="w-3 h-3 text-muted-foreground"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
        )}
      </div>
    </motion.div>
  );
}
