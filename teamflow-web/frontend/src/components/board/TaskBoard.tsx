"use client";

import { useState, useMemo } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverEvent,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay,
  closestCorners,
} from "@dnd-kit/core";
import { motion, AnimatePresence } from "framer-motion";
import { TaskColumn } from "./TaskColumn";
import { TaskCard } from "./TaskCard";
import { UserFilter, UserFilterValue } from "./UserFilter";
import { useUpdateTask, useAssignTask } from "@/lib/query";
import { useTasksWithAssignee } from "@/hooks/useTasksWithAssignee";
import type { Task } from "@/types";
import { Plus, RefreshCw, WifiOff, AlertCircle } from "lucide-react";
import { TaskForm } from "../task/TaskForm";
import { TaskDrawer } from "../task/TaskDrawer";
import { triggerConfetti } from "@/lib/confetti";
import { useQueryClient } from "@tanstack/react-query";
import { useOnline } from "@/hooks/useOnline";
import { Button } from "@/components/ui/button";

const COLUMNS: { id: string; title: string }[] = [
  { id: "TODO", title: "To Do" },
  { id: "DOING", title: "In Progress" },
  { id: "REVIEW", title: "In Review" },
  { id: "DONE", title: "Done" },
];

export function TaskBoard() {
  const queryClient = useQueryClient();
  const { tasks = [], isLoading, error, isRefetching } = useTasksWithAssignee();
  const updateTask = useUpdateTask();
  const assignTask = useAssignTask();
  const isOnline = useOnline(); // T230a: Track network status

  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [formColumnId, setFormColumnId] = useState<string>("TODO");
  const [userFilter, setUserFilter] = useState<UserFilterValue>("all");
  const [drawerTaskId, setDrawerTaskId] = useState<string | undefined>();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [dragStartPosition, setDragStartPosition] = useState<{ x: number; y: number } | null>(null);

  // Filter tasks based on user selection
  const filteredTasks = useMemo(() => {
    if (userFilter === "all") return tasks;
    if (userFilter === "unassigned") {
      return tasks.filter((task) => !task.assignee_id);
    }
    if (userFilter === "my-tasks") {
      // This would use the current user's ID from auth context
      // For now, we'll use a placeholder
      return tasks;
    }
    // Filter by specific user ID
    return tasks.filter((task) => task.assignee_id === userFilter);
  }, [tasks, userFilter]);

  // Configure drag sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement required to start drag
      },
    })
  );

  // Group tasks by status (using filtered tasks)
  const tasksByStatus = filteredTasks.reduce<Record<string, Task[]>>(
    (acc, task) => {
      const status = task.status as string;
      if (!acc[status]) acc[status] = [];
      acc[status].push(task);
      return acc;
    },
    { TODO: [], DOING: [], REVIEW: [], DONE: [] }
  );

  // Handle drag start
  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const task = tasks.find((t) => t.id === active.id);
    if (task) {
      setActiveTask(task);
      // T230a: Store initial position for snap-back animation on network loss
      setDragStartPosition({ x: 0, y: 0 }); // Simplified - dnd-kit handles visual position
    }
  };

  // Handle drag over (for visual feedback)
  const handleDragOver = (_event: DragOverEvent) => {
    // Placeholder for future sortable implementation
  };

  // Handle drag end
  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    // T230a: Check if offline - cancel drag with snap-back
    if (!isOnline) {
      setActiveTask(null);
      setDragStartPosition(null);
      // dnd-kit automatically handles snap-back to original position
      return;
    }

    if (!over) {
      setActiveTask(null);
      setDragStartPosition(null);
      return;
    }

    const taskId = active.id as string;
    const overId = over.id as string;
    const overData = over.data.current;

    // Find the task
    const task = tasks.find((t) => t.id === taskId);
    if (!task) {
      setActiveTask(null);
      setDragStartPosition(null);
      return;
    }

    // Check if dropped on a team member (assignment)
    if (overData?.type === "team-members" || overData?.action === "assign") {
      setActiveTask(null);
      setDragStartPosition(null);
      // Assign to user - the userId should be in the over data or clicked separately
      // For now, the team member list handles click-to-assign
      return;
    }

    // Check if dropped on a column (status change)
    if (task.status !== overId && COLUMNS.some((col) => col.id === overId)) {
      // Check if moved to "Done" - trigger celebration
      if (overId === "DONE" && task.status !== "DONE") {
        triggerConfetti();
      }

      // Manually update cache FIRST (synchronous optimistic update)
      queryClient.setQueryData<Task[]>(
        ['tasks'],
        (old = []) =>
          old.map((t) =>
            t.id === taskId
              ? { ...t, status: overId as any, updated_at: new Date().toISOString() }
              : t
          )
      );

      // Now clear activeTask - the UI will show the task in the new column
      setActiveTask(null);
      setDragStartPosition(null);

      // Then call the mutation in the background
      updateTask.mutate({
        id: taskId,
        data: { status: overId as any },
      });
    } else {
      // No change needed - clear immediately
      setActiveTask(null);
      setDragStartPosition(null);
    }
  };

  // Handle task assignment
  const handleAssignTask = (userId: string | null) => {
    if (activeTask) {
      const taskId = activeTask.id;
      if (userId) {
        assignTask.mutate({
          taskId,
          assigneeId: userId,
        });
      } else {
        // Unassign - update with null assignee_id
        updateTask.mutate({
          id: taskId,
          data: { assignee_id: null },
        });
      }
      setActiveTask(null);
    }
  };

  // Handle task edit - open drawer
  const handleEditTask = (taskId: string) => {
    setDrawerTaskId(taskId);
    setIsDrawerOpen(true);
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {COLUMNS.map((column) => (
          <div
            key={column.id}
            className="bg-muted/30 rounded-lg p-4 animate-pulse"
          >
            <div className="h-6 bg-muted rounded mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 bg-muted rounded"></div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive mb-2">Failed to load tasks</p>
        <p className="text-sm text-muted-foreground">
          Please check your connection and try again
        </p>
      </div>
    );
  }

  return (
    <>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">Task Board</h1>
            <p className="text-muted-foreground">
              Drag and drop tasks to update status
            </p>
          </div>
          <div className="flex items-center gap-3">
            <UserFilter
              value={userFilter}
              onChange={setUserFilter}
            />
            {/* T151: Manual refresh button */}
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => queryClient.invalidateQueries({ queryKey: ['tasks'] })}
                aria-label="Refresh tasks"
                title="Refresh tasks"
              >
                <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                onClick={() => {
                  setFormColumnId("TODO");
                  setShowTaskForm(true);
                }}
              >
                <Plus className="w-4 h-4" />
                New Task
              </Button>
            </motion.div>
          </div>
        </div>

        {/* T230a: Network status warning */}
        <AnimatePresence>
          {!isOnline && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg flex items-center gap-3"
            >
              <WifiOff className="text-amber-600 dark:text-amber-400 flex-shrink-0" size={20} />
              <div className="flex-1">
                <p className="text-sm font-medium text-amber-800 dark:text-amber-400">
                  You're offline
                </p>
                <p className="text-xs text-amber-600 dark:text-amber-500">
                  Drag and drop is disabled. Changes will be saved when you reconnect.
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Board */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-full min-h-[calc(100vh-12rem)]">
          <AnimatePresence>
            {COLUMNS.map((column, index) => (
              <motion.div
                key={column.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="h-full"
              >
                <TaskColumn
                  id={column.id}
                  title={column.title}
                  tasks={tasksByStatus[column.id]}
                  onEditTask={handleEditTask}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeTask ? (
            <div className="transform scale-105 shadow-2xl">
              <TaskCard task={activeTask} isDragging />
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Task Form Modal */}
      <AnimatePresence>
        {showTaskForm && (
          <TaskForm
            columnId={formColumnId}
            onClose={() => setShowTaskForm(false)}
          />
        )}
      </AnimatePresence>

      {/* Task Drawer */}
      <TaskDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        taskId={drawerTaskId}
      />
    </>
  );
}
