"use client";

import { useDraggable } from "@dnd-kit/core";
import { motion } from "framer-motion";
import { Flag, MoreHorizontal, Clock, User } from "lucide-react";
import type { Task } from "@/types";
import { CSS } from "@dnd-kit/utilities";

interface TaskCardProps {
  task: Task;
  isDragging?: boolean;
}

export function TaskCard({ task, isDragging = false }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging: isDndDragging } = useDraggable({
    id: task.id,
    data: {
      type: "Task",
      task,
    },
  });

  const style = transform
    ? {
        transform: CSS.Translate.toString(transform),
      }
    : undefined;

  // Priority Badge Colors - High Contrast for Readability
  const priorityColors = {
    LOW: "bg-zinc-100 text-zinc-700 border-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700",
    MEDIUM: "bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-800",
    HIGH: "bg-rose-100 text-rose-800 border-rose-200 dark:bg-rose-900/30 dark:text-rose-300 dark:border-rose-800",
  };

  const priorityColor = task.priority ? priorityColors[task.priority] : priorityColors.LOW;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`
        group relative p-4 rounded-xl border bg-card transition-all duration-200
        ${isDragging || isDndDragging ? "opacity-50 ring-2 ring-lime-500 rotate-2 shadow-xl z-50 cursor-grabbing" : "opacity-100 border-border shadow-sm hover:shadow-md hover:border-lime-500/50 cursor-grab"}
      `}
    >
      <div className="flex justify-between items-start mb-2">
        <div className={`
          px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border
          ${priorityColor}
        `}>
          {task.priority || "LOW"}
        </div>
        <button className="text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity">
          <MoreHorizontal size={16} />
        </button>
      </div>

      <h4 className="font-semibold text-sm mb-1 text-foreground leading-tight">
        {task.title}
      </h4>
      
      {task.description && (
        <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
          {task.description}
        </p>
      )}

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/50">
        <div className="flex items-center gap-2">
          {task.due_date && (
            <div className="flex items-center gap-1 text-[10px] text-muted-foreground font-medium">
              <Clock size={12} />
              <span>{new Date(task.due_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>
            </div>
          )}
        </div>

        <div className="flex items-center">
          {task.assignee_id ? (
            <div className="w-6 h-6 rounded-full bg-lime-400 flex items-center justify-center text-[10px] font-bold text-black border border-white dark:border-zinc-900">
              U
            </div>
          ) : (
            <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center text-muted-foreground border border-background">
              <User size={12} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}