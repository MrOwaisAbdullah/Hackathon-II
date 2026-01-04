"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { toast } from "sonner";

/** Hook for task actions (edit, delete, archive) */
export function useTaskActions() {
  const queryClient = useQueryClient();

  const deleteTask = useMutation({
    mutationFn: async (taskId: string) => {
      const response = await api.delete(`/api/v1/tasks/${taskId}`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task deleted successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to delete task");
    },
  });

  const archiveTask = useMutation({
    mutationFn: async (taskId: string) => {
      const response = await api.patch(`/api/v1/tasks/${taskId}`, {
        archived_at: new Date().toISOString(),
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast.success("Task archived successfully");
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || "Failed to archive task");
    },
  });

  return {
    deleteTask: deleteTask.mutateAsync,
    archiveTask: archiveTask.mutateAsync,
    isDeleting: deleteTask.isPending,
    isArchiving: archiveTask.isPending,
  };
}
