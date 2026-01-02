import { useDroppable } from "@dnd-kit/core";
import { TaskCard } from "./TaskCard";
import type { Task } from "@/types";
import { motion } from "framer-motion";

interface TaskColumnProps {
  id: string;
  title: string;
  tasks: Task[];
}

export function TaskColumn({ id, title, tasks }: TaskColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id,
  });

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="font-bold text-sm text-foreground uppercase tracking-wider">{title}</h3>
        <span className="text-xs font-medium text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">
          {tasks.length}
        </span>
      </div>

      <div
        ref={setNodeRef}
        className={`
          flex-1 p-2 rounded-xl border-2 border-dashed transition-colors
          ${isOver ? "border-lime-500 bg-lime-500/5" : "border-transparent bg-zinc-100/50 dark:bg-zinc-900/50"}
        `}
      >
        <div className="flex flex-col gap-3 min-h-[150px]">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
          
          {tasks.length === 0 && (
            <div className="h-full flex items-center justify-center py-8 text-xs font-medium text-muted-foreground/60 border-2 border-dashed border-border/50 rounded-lg">
              Drop tasks here
            </div>
          )}
        </div>
      </div>
    </div>
  );
}