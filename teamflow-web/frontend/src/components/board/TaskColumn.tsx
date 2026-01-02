"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { TaskCard } from "./TaskCard";
import type { Task } from "@/types";

interface TaskColumnProps {
  id: string;
  title: string;
  tasks: Task[];
  isDropTarget?: boolean;
}

const columnColors: Record<string, string> = {
  todo: "bg-slate-500/10 border-slate-500/20",
  doing: "bg-blue-500/10 border-blue-500/20",
  review: "bg-amber-500/10 border-amber-500/20",
  done: "bg-emerald-500/10 border-emerald-500/20",
};

const columnIcons: Record<string, string> = {
  todo: "○",
  doing: "◐",
  review: "◑",
  done: "●",
};

export function TaskColumn({ id, title, tasks }: TaskColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id,
    data: {
      type: "column",
      status: id,
    },
  });

  // T156: Generate accessible label
  const ariaLabel = `${title} column. Contains ${tasks.length} ${tasks.length === 1 ? 'task' : 'tasks'}. Drop zone for moving tasks.`;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`
        flex flex-col rounded-lg border-2 transition-all duration-200
        ${columnColors[id]}
        ${isOver ? "ring-2 ring-primary/50 scale-[1.02]" : ""}
      `}
      // T156: Accessibility attributes
      role="region"
      aria-label={ariaLabel}
      aria-dropeffect="move"
    >
      {/* Column Header */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-sm flex items-center gap-2">
            <span className="text-lg" aria-hidden="true">{columnIcons[id]}</span>
            <span>{title}</span>
          </h2>
          <span
            className={`
              text-sm font-medium px-2 py-0.5 rounded-full
              bg-background/50
            `}
            aria-label={`${tasks.length} ${tasks.length === 1 ? 'task' : 'tasks'} in ${title}`}
          >
            {tasks.length}
          </span>
        </div>
      </div>

      {/* T156: Task List with ARIA attributes */}
      <div
        ref={setNodeRef}
        className={`
          flex-1 p-3 space-y-3 min-h-[200px] max-h-[calc(100vh-300px)]
          overflow-y-auto transition-colors duration-200
          ${isOver ? "bg-primary/5" : ""}
        `}
        role="list"
        aria-label={`${title} tasks`}
      >
        <SortableContext
          items={tasks.map((t) => t.id)}
          strategy={verticalListSortingStrategy}
        >
          <AnimatePresence mode="popLayout">
            {tasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}

            {/* Empty state with ARIA */}
            {tasks.length === 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.5 }}
                exit={{ opacity: 0 }}
                className="text-center py-8 text-sm text-muted-foreground border-2 border-dashed border-border rounded-lg"
                role="status"
                aria-label={`No tasks in ${title}`}
              >
                Drop tasks here
              </motion.div>
            )}
          </AnimatePresence>
        </SortableContext>
      </div>
    </motion.div>
  );
}
