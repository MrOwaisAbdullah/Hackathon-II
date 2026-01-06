"use client";

import { useDraggable } from "@dnd-kit/core";
import { motion, AnimatePresence } from "framer-motion";
import { Flag, MoreHorizontal, Clock, Edit2, Trash2, Archive, CheckCircle, Eye, Circle } from "lucide-react";
import type { Task } from "@/types";
import { CSS } from "@dnd-kit/utilities";
import React, { useState, useEffect } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu";
import { useArchiveTask, useDeleteTask, useUpdateTask } from "@/lib/query";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { renderMarkdown } from "@/lib/markdown";
import { AssigneeAvatar } from "../task/AssigneeAvatar";

interface TaskCardProps {
  task: Task;
  isDragging?: boolean;
  onEdit?: (taskId: string) => void;
}

export function TaskCard({ task, isDragging = false, onEdit }: TaskCardProps) {
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

  const archiveTask = useArchiveTask();
  const deleteTask = useDeleteTask();
  const updateTask = useUpdateTask();

  // Status options for "Move to" submenu
  const statusOptions = [
    { value: 'TODO', label: 'To Do', icon: 'circle' },
    { value: 'DOING', label: 'In Progress', icon: 'spinner' },
    { value: 'REVIEW', label: 'In Review', icon: 'eye' },
    { value: 'DONE', label: 'Done', icon: CheckCircle },
  ].filter(option => option.value !== task.status);

  const handleMoveToStatus = async (newStatus: string) => {
    try {
      await updateTask.mutateAsync({
        id: task.id,
        data: { status: newStatus as any },
      });
      toast.success(`Task moved to ${statusOptions.find(s => s.value === newStatus)?.label || newStatus}`);
    } catch (error) {
      toast.error('Failed to move task');
    }
  };
  const [showMenu, setShowMenu] = useState(false);
  const [isDark, setIsDark] = useState(false);

  // Detect dark mode
  useEffect(() => {
    const checkDark = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    checkDark();
    window.addEventListener('class-change', checkDark);
    // Observer for class changes
    const observer = new MutationObserver(checkDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    return () => {
      window.removeEventListener('class-change', checkDark);
      observer.disconnect();
    };
  }, []);

  // Priority Badge Styles - Theme-aware
  const getPriorityStyle = (priority: string) => {
    const styles = {
      LOW: {
        light: { backgroundColor: '#dcfce7', color: '#14532d' },
        dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
        dot: '#22c55e',
      },
      MEDIUM: {
        light: { backgroundColor: '#fef9c3', color: '#713f12' },
        dark: { backgroundColor: 'rgba(113, 63, 18, 0.3)', color: '#facc15' },
        dot: '#eab308',
      },
      HIGH: {
        light: { backgroundColor: '#fee2e2', color: '#7f1d1d' },
        dark: { backgroundColor: 'rgba(127, 29, 29, 0.3)', color: '#f87171' },
        dot: '#ef4444',
      },
    };
    return styles[priority as keyof typeof styles] || styles.LOW;
  };

  const priority = getPriorityStyle(task.priority);
  const priorityStyle = isDark ? priority.dark : priority.light;

  // Status Badge Styles - Theme-aware
  const getStatusStyle = (status: string) => {
    const styles = {
      TODO: {
        label: "To Do",
        light: { backgroundColor: '#f3f4f6', color: '#111827' },
        dark: { backgroundColor: 'rgba(31, 41, 55, 0.5)', color: '#d1d5db' },
      },
      DOING: {
        label: "In Progress",
        light: { backgroundColor: '#dbeafe', color: '#1e3a8a' },
        dark: { backgroundColor: 'rgba(30, 58, 138, 0.3)', color: '#60a5fa' },
      },
      REVIEW: {
        label: "In Review",
        light: { backgroundColor: '#f3e8ff', color: '#5b21b6' },
        dark: { backgroundColor: 'rgba(91, 33, 182, 0.3)', color: '#a78bfa' },
      },
      DONE: {
        label: "Done",
        light: { backgroundColor: '#dcfce7', color: '#14532d' },
        dark: { backgroundColor: 'rgba(20, 83, 45, 0.3)', color: '#4ade80' },
      },
    };
    return styles[status as keyof typeof styles] || styles.TODO;
  };

  const status = getStatusStyle(task.status);
  const statusStyle = isDark ? status.dark : status.light;

  // Status icons
  const statusIcons = {
    TODO: null,
    DOING: "spinner",
    REVIEW: "eye",
    DONE: CheckCircle,
  };
  const statusIcon = statusIcons[task.status as keyof typeof statusIcons];

  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete this task?")) {
      try {
        await deleteTask.mutateAsync(task.id);
        toast.success("Task deleted successfully");
      } catch (error) {
        toast.error("Failed to delete task");
      }
    }
  };

  const handleArchive = async () => {
    try {
      await archiveTask.mutateAsync(task.id);
      toast.success("Task archived successfully");
    } catch (error) {
      toast.error("Failed to archive task");
    }
  };

  const handleEdit = () => {
    onEdit?.(task.id);
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2, boxShadow: "0 8px 25px -5px rgba(0, 0, 0, 0.1)" }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={cn(
        "group relative overflow-hidden rounded-xl border bg-card p-3 md:p-4 shadow-sm w-full min-w-0",
        "transition-all duration-200 ease-out",
        "hover:shadow-lg hover:border-lime-500/30",
        (isDragging || isDndDragging) && "opacity-50 shadow-2xl ring-2 ring-lime-500 scale-105 z-50"
      )}
    >
      {/* Decorative gradient accent on hover */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-lime-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        initial={false}
      />

      {/* Header: Priority + Status + Menu */}
      <div className="flex items-center justify-between mb-3 relative">
        <div className="flex items-center gap-2">
          {/* Priority Badge */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-1.5 px-2 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider"
            style={priorityStyle}
          >
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: priority.dot }} />
            {task.priority}
          </motion.div>

          {/* Status Badge */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="flex items-center gap-1.5 px-2 py-1 rounded-lg text-[10px] font-semibold uppercase tracking-wide"
            style={statusStyle}
          >
            {statusIcon && typeof statusIcon !== "string" && React.createElement(statusIcon, { className: "w-3 h-3" })}
            {status.label}
          </motion.div>
        </div>

        {/* Action Menu - Always visible */}
        <DropdownMenu open={showMenu} onOpenChange={setShowMenu}>
          <DropdownMenuTrigger asChild>
            <motion.button
              whileHover={{ rotate: 90, scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="flex items-center justify-center w-10 h-10 lg:w-8 lg:h-8 rounded-lg transition-all duration-200 text-muted-foreground hover:text-foreground hover:bg-muted"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreHorizontal size={18} strokeWidth={2.5} />
            </motion.button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            align="end"
            className="w-48"
            sideOffset={5}
            onClick={(e) => e.stopPropagation()}
          >
            <DropdownMenuLabel className="text-xs font-semibold text-muted-foreground">
              Task Actions
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            {/* Move to submenu - for easy status change on mobile */}
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>
                <Flag className="w-4 h-4 mr-2 text-lime-600" />
                <span>Move to</span>
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent>
                {statusOptions.map((option) => (
                  <DropdownMenuItem
                    key={option.value}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMoveToStatus(option.value);
                    }}
                    className="cursor-pointer"
                  >
                    {option.icon === CheckCircle ? (
                      <CheckCircle className="w-4 h-4 mr-2 text-emerald-600" />
                    ) : option.icon === 'spinner' ? (
                      <div className="w-4 h-4 mr-2 text-blue-600 flex items-center justify-center">
                        <div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      </div>
                    ) : option.icon === 'eye' ? (
                      <Eye className="w-4 h-4 mr-2 text-purple-600" />
                    ) : option.icon === 'circle' ? (
                      <Circle className="w-4 h-4 mr-2 text-zinc-500" />
                    ) : (
                      <div className="w-4 h-4 mr-2" />
                    )}
                    <span>{option.label}</span>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                handleEdit();
              }}
              className="cursor-pointer"
            >
              <Eye className="w-4 h-4 mr-2 text-blue-600" />
              <span>View Details</span>
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                handleEdit();
              }}
              className="cursor-pointer"
            >
              <Edit2 className="w-4 h-4 mr-2 text-lime-600" />
              <span>Edit Task</span>
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                handleArchive();
              }}
              className="cursor-pointer"
            >
              <Archive className="w-4 h-4 mr-2 text-blue-600" />
              <span>Archive Task</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation();
                handleDelete();
              }}
              className="cursor-pointer text-rose-600 focus:text-rose-600 focus:bg-rose-50 dark:focus:bg-rose-950/20"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              <span>Delete Task</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Title - T622: Mobile line-clamp-2, w-full for overflow prevention */}
      <h4 className="font-semibold text-sm mb-2 text-foreground leading-snug line-clamp-2 min-h-[2.5rem] w-full">
        {task.title}
      </h4>

      {/* Description - T622: Mobile line-clamp-2, w-full for overflow prevention */}
      {task.description && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-muted-foreground line-clamp-2 mb-3 leading-relaxed prose prose-sm dark:prose-invert max-w-none w-full"
          dangerouslySetInnerHTML={{
            __html: renderMarkdown(task.description),
          }}
        />
      )}

      {/* Footer: Due Date + Assignee */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border/60">
        {/* Due Date */}
        <AnimatePresence>
          {task.due_date && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="flex items-center gap-1.5 text-[11px] text-muted-foreground font-medium"
            >
              <Clock size={13} strokeWidth={2} className="text-lime-500" />
              <span>{new Date(task.due_date).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Assignee Avatar */}
        <AssigneeAvatar
          name={task.assignee?.name}
          email={task.assignee?.email}
          size="sm"
        />
      </div>

      {/* Drag handle indicator (visible on drag) */}
      <AnimatePresence>
        {(isDragging || isDndDragging) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 border-2 border-dashed border-lime-500 rounded-xl pointer-events-none"
          />
        )}
      </AnimatePresence>
    </motion.div>
  );
}
