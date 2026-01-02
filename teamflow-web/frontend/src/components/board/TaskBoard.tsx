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
import { useTasks, useUpdateTask, useAssignTask, useUsers } from "@/lib/query";
import type { Task } from "@/types";
import { Plus, RefreshCw } from "lucide-react";
import { TaskForm } from "../task/TaskForm";
import { TaskDrawer } from "../task/TaskDrawer";
import { triggerConfetti } from "@/lib/confetti";
import { useQueryClient } from "@tanstack/react-query";

const COLUMNS: { id: string; title: string }[] = [
  { id: "TODO", title: "To Do" },
  { id: "DOING", title: "In Progress" },
  { id: "REVIEW", title: "In Review" },
  { id: "DONE", title: "Done" },
];

export function TaskBoard() {
  const queryClient = useQueryClient();
  const { data: tasks = [], isLoading, error, isRefetching } = useTasks();
  const updateTask = useUpdateTask();
  const assignTask = useAssignTask();

  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [formColumnId, setFormColumnId] = useState<string>("TODO");
  const [userFilter, setUserFilter] = useState<UserFilterValue>("all");
  const [drawerTaskId, setDrawerTaskId] = useState<string | undefined>();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

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
    }
  };

  // Handle drag over (for visual feedback)
  const handleDragOver = (_event: DragOverEvent) => {
    // Placeholder for future sortable implementation
  };

  // Handle drag end
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const taskId = active.id as string;
    const overId = over.id as string;
    const overData = over.data.current;

    // Find the task
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    // Check if dropped on a team member (assignment)
    if (overData?.type === "team-members" || overData?.action === "assign") {
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

      // Update task status
      updateTask.mutate({
        id: taskId,
        data: { status: overId as any },
      });
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
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => queryClient.invalidateQueries({ queryKey: ['tasks'] })}
              className="flex items-center gap-2 px-3 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors"
              aria-label="Refresh tasks"
              title="Refresh tasks"
            >
              <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin' : ''}`} />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setFormColumnId("TODO");
                setShowTaskForm(true);
              }}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Task
            </motion.button>
          </div>
        </div>

        {/* Board */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <AnimatePresence>
            {COLUMNS.map((column, index) => (
              <motion.div
                key={column.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <TaskColumn
                  id={column.id}
                  title={column.title}
                  tasks={tasksByStatus[column.id]}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeTask ? (
            <div className="rotate-3 scale-105">
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
