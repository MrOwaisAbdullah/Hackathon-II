"use client";

/** TaskColumn - Kanban board column with droppable area.
 *
 * Displays a column of tasks with a status header.
 * Tasks can be dropped into the column to change status.
 */

import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { motion } from "framer-motion";
import type { Task, TaskStatus } from "@/types";
import { TaskCard } from "./TaskCard";

interface TaskColumnProps {
  status: TaskStatus;
  tasks: Task[];
  statusLabel: string;
  onTaskClick: (task: Task) => void;
}

const statusColors: Record<TaskStatus, string> = {
  todo: "bg-primary",
  in_progress: "bg-accent",
  done: "bg-secondary",
};

const statusBgColors: Record<TaskStatus, string> = {
  todo: "bg-primary/5",
  in_progress: "bg-accent/5",
  done: "bg-secondary/5",
};

export function TaskColumn({
  status,
  tasks,
  statusLabel,
  onTaskClick,
}: TaskColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: status,
  });

  const taskIds = tasks.map((task) => task.id);

  return (
    <motion.div
      ref={setNodeRef}
      className={`flex-1 min-w-[300px] max-w-[400px] rounded-lg p-4 transition-colors ${
        isOver ? statusBgColors[status] : "bg-muted/30"
      }`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Column Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className={`w-3 h-3 rounded-full ${statusColors[status]}`} />
        <h2 className="font-semibold text-foreground">{statusLabel}</h2>
        <span className="text-sm text-muted-foreground ml-auto">
          {tasks.length}
        </span>
      </div>

      {/* Task List */}
      <SortableContext items={taskIds} strategy={verticalListSortingStrategy}>
        <div className="space-y-3">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onClick={() => onTaskClick(task)} />
          ))}
        </div>
      </SortableContext>

      {/* Empty State */}
      {tasks.length === 0 && (
        <div className="text-center py-8 text-muted-foreground text-sm">
          <p>No tasks yet</p>
        </div>
      )}
    </motion.div>
  );
}
