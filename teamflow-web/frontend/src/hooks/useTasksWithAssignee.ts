"use client";

import { useMemo } from "react";
import { useTasks, useUsers } from "@/lib/query";
import type { Task } from "@/types";

/**
 * Hook that enriches tasks with assignee user data.
 *
 * This hook fetches both tasks and users, then maps assignee_id to the
 * corresponding user object, providing a fully populated task list with
 * assignee information ready for rendering.
 */
export function useTasksWithAssignee() {
  const { data: tasks = [], isLoading: isLoadingTasks } = useTasks();
  const { data: users = [], isLoading: isLoadingUsers } = useUsers();

  // Create a map of users by ID for quick lookup
  const usersById = useMemo(() => {
    const map = new Map<string, (typeof users)[0]>();
    users.forEach((user) => map.set(user.id, user));
    return map;
  }, [users]);

  // Enrich tasks with assignee data
  const enrichedTasks = useMemo(() => {
    return tasks.map((task) => {
      const assignee = task.assignee_id
        ? (usersById.get(task.assignee_id) || undefined)
        : undefined;

      return {
        ...task,
        assignee,
      };
    });
  }, [tasks, usersById]);

  return {
    tasks: enrichedTasks,
    isLoading: isLoadingTasks || isLoadingUsers,
  };
}
