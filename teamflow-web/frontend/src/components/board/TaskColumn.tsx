"use client";

import { useDroppable } from "@dnd-kit/core";
import { TaskCard } from "./TaskCard";
import { TaskForm } from "@/components/task/TaskForm";
import type { Task } from "@/types";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Sparkles } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface TaskColumnProps {
  id: string;
  title: string;
  tasks: Task[];
  onEditTask?: (taskId: string) => void;
}

export function TaskColumn({ id, title, tasks, onEditTask }: TaskColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id,
  });

  const [showForm, setShowForm] = useState(false);

  // Dynamic background colors based on column ID
  const getColumnColor = (id: string) => {
    switch (id) {
      case "TODO":
        return "bg-slate-50/50 dark:bg-slate-900/20 border-slate-200/50 dark:border-slate-800/50";
      case "DOING":
        return "bg-blue-50/50 dark:bg-blue-900/10 border-blue-200/50 dark:border-blue-800/30";
      case "REVIEW":
        return "bg-amber-50/50 dark:bg-amber-900/10 border-amber-200/50 dark:border-amber-800/30";
      case "DONE":
        return "bg-emerald-50/50 dark:bg-emerald-900/10 border-emerald-200/50 dark:border-emerald-800/30";
      default:
        return "bg-zinc-50/50 dark:bg-zinc-900/20";
    }
  };

  const getHeaderColor = (id: string) => {
    switch (id) {
      case "TODO":
        return "text-slate-700 dark:text-slate-300";
      case "DOING":
        return "text-blue-700 dark:text-blue-300";
      case "REVIEW":
        return "text-amber-700 dark:text-amber-300";
      case "DONE":
        return "text-emerald-700 dark:text-emerald-300";
      default:
        return "text-muted-foreground";
    }
  };

  const getIndicatorColor = (id: string) => {
    switch (id) {
      case "TODO":
        return "bg-slate-500";
      case "DOING":
        return "bg-blue-500";
      case "REVIEW":
        return "bg-amber-500";
      case "DONE":
        return "bg-emerald-500";
      default:
        return "bg-zinc-500";
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-2">
          {/* Animated indicator */}
          <motion.div
            className={cn("w-2.5 h-2.5 rounded-full", getIndicatorColor(id))}
            animate={id === "DOING" ? { scale: [1, 1.3, 1], opacity: [1, 0.7, 1] } : {}}
            transition={id === "DOING" ? { duration: 2, repeat: Infinity, ease: "easeInOut" } : {}}
          />
          <h3 className={cn("font-bold text-sm uppercase tracking-wider", getHeaderColor(id))}>
            {title}
          </h3>
        </div>

        {/* Task count badge */}
        <motion.span
          key={tasks.length}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className={cn(
            "text-xs font-bold px-2.5 py-1 rounded-full border-2",
            "bg-background/50 backdrop-blur-sm",
            getHeaderColor(id).replace("text-", "border-").replace("-700", "-300").replace("-300", "-400")
          )}
        >
          {tasks.length}
        </motion.span>
      </div>

      {/* Column content */}
      <div
        ref={setNodeRef}
        className={cn(
          "flex-1 p-3 rounded-2xl border backdrop-blur-sm transition-all duration-300 h-full relative overflow-hidden",
          getColumnColor(id),
          isOver && "ring-2 ring-lime-500/50 bg-lime-500/5 !border-lime-500/30 scale-[1.02]"
        )}
      >
        {/* Add Task Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setShowForm(true)}
          className={cn(
            "w-full mb-3 px-4 py-2.5 rounded-xl border-2 border-dashed",
            "flex items-center justify-center gap-2 text-sm font-semibold",
            "transition-all duration-200",
            "bg-background",
            "border-border",
            "text-foreground",
            "hover:border-accent hover:bg-accent/10",
            "hover:text-accent"
          )}
        >
          <motion.div
            whileHover={{ rotate: 90 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <Plus className="w-4 h-4" />
          </motion.div>
          <span>Add Task</span>
        </motion.button>

        {/* Task list */}
        <div className="flex flex-col gap-3 min-h-[100px]">
          <AnimatePresence mode="sync">
            {tasks.map((task) => (
              <TaskCard key={task.id} task={task} onEdit={onEditTask} />
            ))}
          </AnimatePresence>

          {/* Empty state */}
          {tasks.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className={cn(
                "h-full flex flex-col items-center justify-center py-12",
                "text-muted-foreground/40",
                "border-2 border-dashed border-transparent rounded-xl",
                "transition-all hover:border-border/50 hover:bg-background/30"
              )}
            >
              <Sparkles className="w-8 h-8 mb-2 opacity-30" />
              <span className="text-xs font-medium uppercase tracking-wide">
                No tasks yet
              </span>
            </motion.div>
          )}
        </div>

        {/* Drag overlay indicator */}
        <AnimatePresence>
          {isOver && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-lime-500/5 pointer-events-none rounded-2xl"
            />
          )}
        </AnimatePresence>
      </div>

      {/* Task Form Modal */}
      <AnimatePresence>
        {showForm && <TaskForm columnId={id} onClose={() => setShowForm(false)} />}
      </AnimatePresence>
    </div>
  );
}
