"use client";

/** Tasks page - Kanban board for task management.
 *
 * Features:
 * - Drag-and-drop task management using dnd-kit
 * - Three columns: To Do, In Progress, Done
 * - Task drawer for viewing/editing task details
 * - Mock data (will be replaced with API calls)
 */

import { useState } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { SortableContext, arrayMove } from "@dnd-kit/sortable";
import { motion } from "framer-motion";
import { TaskColumn } from "@/components/task/TaskColumn";
import { TaskDrawer } from "@/components/task/TaskDrawer";
import type { Task, TaskStatus } from "@/types";

// Mock data - will be replaced with API calls
const mockTasks: Task[] = [
  {
    id: "1",
    title: "Design new landing page",
    description: "Create wireframes and high-fidelity mockups for the new landing page",
    status: "todo" as TaskStatus,
    priority: "high" as any,
    project_id: "proj-1",
    agency_id: "agency-1",
    assignee_id: "user-1",
    created_at: new Date().toISOString(),
    updated_at: null,
    archived_at: null,
  },
  {
    id: "2",
    title: "Implement authentication flow",
    description: "Set up JWT authentication with login/signup pages",
    status: "in_progress" as TaskStatus,
    priority: "high" as any,
    project_id: "proj-1",
    agency_id: "agency-1",
    assignee_id: "user-2",
    created_at: new Date().toISOString(),
    updated_at: null,
    archived_at: null,
  },
  {
    id: "3",
    title: "Write API documentation",
    description: "Document all REST endpoints with examples",
    status: "todo" as TaskStatus,
    priority: "medium" as any,
    project_id: "proj-1",
    agency_id: "agency-1",
    assignee_id: null,
    created_at: new Date().toISOString(),
    updated_at: null,
    archived_at: null,
  },
  {
    id: "4",
    title: "Set up CI/CD pipeline",
    description: "Configure GitHub Actions for automated testing and deployment",
    status: "done" as TaskStatus,
    priority: "medium" as any,
    project_id: "proj-1",
    agency_id: "agency-1",
    assignee_id: "user-3",
    created_at: new Date().toISOString(),
    updated_at: null,
    archived_at: null,
  },
  {
    id: "5",
    title: "Database optimization",
    description: "Add indexes and optimize slow queries",
    status: "todo" as TaskStatus,
    priority: "low" as any,
    project_id: "proj-1",
    agency_id: "agency-1",
    assignee_id: null,
    created_at: new Date().toISOString(),
    updated_at: null,
    archived_at: null,
  },
  {
    id: "6",
    title: "Fix mobile responsive issues",
    description: "Address layout problems on mobile devices",
    status: "in_progress" as TaskStatus,
    priority: "medium" as any,
    project_id: "proj-1",
    agency_id: "agency-1",
    assignee_id: "user-1",
    created_at: new Date().toISOString(),
    updated_at: null,
    archived_at: null,
  },
];

const columnConfig = [
  { status: "todo" as TaskStatus, label: "To Do" },
  { status: "in_progress" as TaskStatus, label: "In Progress" },
  { status: "done" as TaskStatus, label: "Done" },
];

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks);
  const [activeId, setActiveId] = useState<string | null>(null);
  // Local state for drawer instead of Zustand store (SSR-safe)
  const [isTaskDrawerOpen, setIsTaskDrawerOpen] = useState(false);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);

  // Find active task for drag overlay
  const activeTask = activeId ? tasks.find((t) => t.id === activeId) : null;

  // Configure drag sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement before drag starts (prevents accidental drags)
      },
    })
  );

  // Group tasks by status
  const getTasksByStatus = (status: TaskStatus) => {
    return tasks.filter((task) => task.status === status);
  };

  // Handle drag start
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  // Handle drag end
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    const activeTask = tasks.find((t) => t.id === activeId);
    if (!activeTask) return;

    // Check if dropping on a column (status change)
    const isColumnDrop = columnConfig.some((col) => col.status === overId);

    if (isColumnDrop) {
      // Update task status
      setTasks((tasks) =>
        tasks.map((task) =>
          task.id === activeId ? { ...task, status: overId as TaskStatus } : task
        )
      );
    } else {
      // Reorder within the same column
      const activeIndex = tasks.findIndex((t) => t.id === activeId);
      const overIndex = tasks.findIndex((t) => t.id === overId);

      if (activeIndex !== overIndex) {
        setTasks(arrayMove(tasks, activeIndex, overIndex));
      }
    }
  };

  const handleTaskClick = (task: Task) => {
    setActiveTaskId(task.id);
    setIsTaskDrawerOpen(true);
  };

  const handleCloseDrawer = () => {
    setIsTaskDrawerOpen(false);
    setActiveTaskId(null);
  };

  return (
    <div className="p-8 h-full">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground">Tasks</h1>
        <p className="text-muted-foreground mt-1">
          Manage and track your team's tasks
        </p>
      </div>

      {/* Kanban Board */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex gap-6 overflow-x-auto pb-4">
          {columnConfig.map((column) => (
            <TaskColumn
              key={column.status}
              status={column.status}
              statusLabel={column.label}
              tasks={getTasksByStatus(column.status)}
              onTaskClick={handleTaskClick}
            />
          ))}
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeTask ? (
            <div className="bg-card rounded-lg p-4 shadow-lg border border-border opacity-80">
              <h3 className="font-medium text-foreground">{activeTask.title}</h3>
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Task Drawer */}
      <TaskDrawer
        isOpen={isTaskDrawerOpen}
        onClose={handleCloseDrawer}
        taskId={activeTaskId ?? undefined}
      />
    </div>
  );
}
