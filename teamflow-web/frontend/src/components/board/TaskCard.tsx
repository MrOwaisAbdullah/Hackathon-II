"use client";

import { motion } from "framer-motion";
import { useDraggable } from "@dnd-kit/core";
import { AssigneeAvatar } from "../task/AssigneeAvatar";
import type { Task } from "@/types";

interface TaskCardProps {
  task: Task;
  isDragging?: boolean;
}

const priorityColors: Record<string, string> = {
  LOW: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  MEDIUM: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300",
  HIGH: "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-300",
};

export function TaskCard({ task, isDragging = false }: TaskCardProps) {
  const {
    setNodeRef,
    attributes,
    listeners,
    isDragging: isDraggingKit,
  } = useDraggable({
    id: task.id,
    data: {
      type: "task",
      task,
    },
  });

  // T156: Generate accessible label
  const priorityLabel = task.priority?.toLowerCase() || "no priority";
  const assigneeLabel = task.assignee?.name || "Unassigned";
  const ariaLabel = `Task: ${task.title}. Priority: ${priorityLabel}. Assigned to: ${assigneeLabel}. Status: ${task.status?.toLowerCase()}. Drag to move to another column.`;

  return (
    <motion.div
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{
        opacity: isDragging ? 0.5 : 1,
        scale: isDragging ? 1.05 : 1,
        rotate: isDragging ? 3 : 0,
      }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{
        type: "spring",
        stiffness: 300,
        damping: 20,
      }}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ cursor: "grabbing" }}
      className={`
        draggable bg-card rounded-lg p-4 border border-border
        shadow-sm hover:shadow-md cursor-grab active:cursor-grabbing
        transition-all duration-200 focus-within:ring-2 focus-within:ring-primary/50
        ${isDraggingKit ? "shadow-xl ring-2 ring-primary/50" : ""}
      `}
      // T156: Accessibility attributes
      role="button"
      tabIndex={0}
      aria-label={ariaLabel}
      aria-pressed={isDragging}
      aria-describedby={`task-${task.id}-details`}
      draggable="true"
    >
      {/* Priority Badge */}
      <div className="flex items-start justify-between mb-2">
        <span
          className={`
            inline-block px-2 py-0.5 rounded text-xs font-medium capitalize
            ${priorityColors[task.priority]}
          `}
        >
          {task.priority}
        </span>
      </div>

      {/* Title */}
      <h3 className="font-medium text-sm text-card-foreground mb-2 leading-tight">
        {task.title}
      </h3>

      {/* Description (truncated) */}
      {task.description && (
        <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Footer: Due Date & Assignee */}
      <div className="flex items-center justify-between mt-auto">
        {/* Due Date */}
        {task.due_date && (
          <div className="text-xs text-muted-foreground">
            {new Date(task.due_date).toLocaleDateString()}
          </div>
        )}

        {/* Assignee Avatar */}
        <AssigneeAvatar
          name={task.assignee?.name}
          email={task.assignee?.email}
          size="sm"
        />
      </div>
    </motion.div>
  );
}
