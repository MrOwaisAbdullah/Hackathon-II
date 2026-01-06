
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { Task, User } from '@/types';

export interface DashboardStats {
  activeProjects: number;
  tasksCompleted: number;
  teamUtilization: number;
  revenue: number;
  trends: {
    activeProjects: number;
    tasksCompleted: number;
    teamUtilization: number;
    revenue: number;
  };
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await api.get('/api/v1/analytics/stats');
      return data as DashboardStats;
    },
    // Poll every 10 seconds for real-time updates (FR-025)
    refetchInterval: 10000,
  });
}

export function useTasksByStatus() {
  return useQuery({
    queryKey: ['tasks-by-status'],
    queryFn: async () => {
      const { data } = await api.get('/api/v1/analytics/tasks-by-status');
      return data as { label: string; value: number; color: string }[];
    },
    refetchInterval: 10000,
  });
}

export function useProjectProfitability() {
  return useQuery({
    queryKey: ['project-profitability'],
    queryFn: async () => {
      const { data } = await api.get('/api/v1/analytics/profitability');
      return data;
    },
    refetchInterval: 10000,
  });
}

// ============ TASK MANAGEMENT QUERIES ============

/**
 * Fetch all tasks for the current agency
 */
export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await api.get<{ tasks: Task[] }>('/api/v1/tasks');
      return response.data.tasks;
    },
    refetchInterval: 10000, // Poll every 10 seconds for real-time updates
    staleTime: 5000, // Consider data fresh for 5 seconds
  });
}

/**
 * Fetch archived tasks (with include=archived)
 */
export function useArchivedTasks() {
  return useQuery({
    queryKey: ['tasks', 'archived'],
    queryFn: async () => {
      const response = await api.get<{ tasks: Task[] }>('/api/v1/tasks?include=archived');
      return response.data.tasks.filter((t: Task) => t.status === 'ARCHIVED');
    },
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

/**
 * Fetch a single task by ID
 */
export function useTask(id: string) {
  return useQuery({
    queryKey: ['tasks', id],
    queryFn: async () => {
      const response = await api.get<Task>(`/api/v1/tasks/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Create a new task
 */
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Task>) => {
      const response = await api.post<Task>('/api/v1/tasks', data);
      return response.data;
    },
    onSuccess: (newTask) => {
      // Optimistically add to tasks cache
      queryClient.setQueryData<Task[]>(
        ['tasks'],
        (old = []) => [...old, newTask]
      );
      // Invalidate to refetch
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

/**
 * Update a task
 */
export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Task> }) => {
      const response = await api.patch<Task>(`/api/v1/tasks/${id}`, data);
      return response.data;
    },
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['tasks'] });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData<Task[]>(['tasks']);

      // Optimistically update cache
      queryClient.setQueryData<Task[]>(
        ['tasks'],
        (old = []) =>
          old.map((task) =>
            task.id === id ? { ...task, ...data, updated_at: new Date().toISOString() } : task
          )
      );

      // Return context with previous value for rollback
      return { previousTasks };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks'], context.previousTasks);
      }
    },
    onSettled: () => {
      // Refetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

/**
 * Delete a task (soft delete/archive)
 */
export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/tasks/${id}`);
      return id;
    },
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] });

      const previousTasks = queryClient.getQueryData<Task[]>(['tasks']);

      queryClient.setQueryData<Task[]>(
        ['tasks'],
        (old = []) => old.filter((task) => task.id !== id)
      );

      return { previousTasks };
    },
    onError: (_error, _id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks'], context.previousTasks);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

/**
 * Fetch all projects for the current agency
 */
export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await api.get('/api/v1/projects');
      return response.data;
    },
    refetchInterval: 10000, // Poll every 10 seconds
    staleTime: 5000,
  });
}

/**
 * Fetch a single project by ID
 */
export function useProject(id: string) {
  return useQuery({
    queryKey: ['projects', id],
    queryFn: async () => {
      const response = await api.get(`/api/v1/projects/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

/**
 * Create a new project
 */
export function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { name: string; description?: string; status?: string }) => {
      const response = await api.post('/api/v1/projects', data);
      return response.data;
    },
    onSuccess: (newProject) => {
      // Optimistically add to projects cache
      queryClient.setQueryData(
        ['projects'],
        (old: any[] = []) => [...(old || []), newProject]
      );
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * Update a project
 */
export function useUpdateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: { name?: string; description?: string; status?: string } }) => {
      const response = await api.patch(`/api/v1/projects/${id}`, data);
      return response.data;
    },
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['projects'] });
      const previousProjects = queryClient.getQueryData(['projects']);

      queryClient.setQueryData(
        ['projects'],
        (old: any[] = []) => old.map((p) => p.id === id ? { ...p, ...data, updated_at: new Date().toISOString() } : p)
      );

      return { previousProjects };
    },
    onError: (_error, _variables, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(['projects'], context.previousProjects);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * Delete a project (soft delete/archive)
 */
export function useDeleteProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/projects/${id}`);
      return id;
    },
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['projects'] });
      const previousProjects = queryClient.getQueryData(['projects']);

      queryClient.setQueryData(
        ['projects'],
        (old: any[] = []) => old.filter((p) => p.id !== id)
      );

      return { previousProjects };
    },
    onError: (_error, _id, context) => {
      if (context?.previousProjects) {
        queryClient.setQueryData(['projects'], context.previousProjects);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

/**
 * Assign task to a user
 */
export function useAssignTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ taskId, assigneeId }: { taskId: string; assigneeId: string }) => {
      const response = await api.post<Task>(`/api/v1/tasks/${taskId}/assign`, {
        assignee_id: assigneeId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

/**
 * Archive a task
 */
export function useArchiveTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (taskId: string) => {
      const response = await api.post<Task>(`/api/v1/tasks/${taskId}/archive`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

/**
 * Restore an archived task
 */
export function useRestoreTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (taskId: string) => {
      const response = await api.post<Task>(`/api/v1/tasks/${taskId}/restore`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

/**
 * Fetch all users (team members) in the current agency
 */
export function useUsers() {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await api.get<User[]>('/api/v1/users');
      return response.data;
    },
    staleTime: 60000, // Consider users data fresh for 1 minute (less frequent than tasks)
  });
}

/**
 * Create a new user
 */
export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { name: string; email: string; role: string; is_project_manager?: boolean }) => {
      const response = await api.post('/api/v1/users', data);
      return response.data;
    },
    onSuccess: (newUser) => {
      queryClient.setQueryData(
        ['users'],
        (old: any[] = []) => [...(old || []), newUser]
      );
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

/**
 * Update a user
 */
export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: { name?: string; email?: string; role?: string; is_project_manager?: boolean } }) => {
      const response = await api.patch(`/api/v1/users/${id}`, data);
      return response.data;
    },
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['users'] });
      const previousUsers = queryClient.getQueryData(['users']);

      queryClient.setQueryData(
        ['users'],
        (old: any[] = []) => old.map((u) => u.id === id ? { ...u, ...data, updated_at: new Date().toISOString() } : u)
      );

      return { previousUsers };
    },
    onError: (_error, _variables, context) => {
      if (context?.previousUsers) {
        queryClient.setQueryData(['users'], context.previousUsers);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

/**
 * Delete a user (soft delete)
 */
export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/users/${id}`);
      return id;
    },
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['users'] });
      const previousUsers = queryClient.getQueryData(['users']);

      queryClient.setQueryData(
        ['users'],
        (old: any[] = []) => old.filter((u) => u.id !== id)
      );

      return { previousUsers };
    },
    onError: (_error, _id, context) => {
      if (context?.previousUsers) {
        queryClient.setQueryData(['users'], context.previousUsers);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

// ============ TIME ENTRY QUERIES (US5) ============

export interface TimeEntry {
  id: string;
  task_id: string;
  user_id: string;
  agency_id: string;
  duration_minutes: number;
  note?: string;
  entry_date?: string;
  created_at: string;
}

/**
 * Fetch time entries for a task (or all if no taskId provided)
 */
export function useTimeEntries(taskId?: string) {
  return useQuery({
    queryKey: ['time-entries', taskId],
    queryFn: async () => {
      const url = taskId
        ? `/api/v1/time-entries?task_id=${taskId}`
        : '/api/v1/time-entries';
      const response = await api.get<{ time_entries: TimeEntry[] }>(url);
      return response.data.time_entries;
    },
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

/**
 * Get total time for a task
 */
export function useTaskTotalTime(taskId?: string) {
  return useQuery({
    queryKey: ['time-entries', 'total', taskId],
    queryFn: async () => {
      if (!taskId) return { total_minutes: 0 };
      const response = await api.get<{ total_minutes: number }>(
        `/api/v1/time-entries/task/${taskId}/total`
      );
      return response.data;
    },
    enabled: !!taskId,
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

/**
 * Create a time entry
 */
export function useCreateTimeEntry() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      task_id: string;
      duration_minutes: number;
      note?: string;
      entry_date?: string;
    }) => {
      const response = await api.post<{ time_entry: TimeEntry }>(
        '/api/v1/time-entries',
        data
      );
      return response.data.time_entry;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['time-entries'] });
    },
  });
}

// ============ ACCOUNT MANAGEMENT QUERIES ============

/**
 * Delete current user's account
 */
export function useDeleteMyAccount() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      await api.delete('/api/v1/auth/me');
    },
    onSuccess: () => {
      // Clear all cache and redirect to login will be handled by caller
      queryClient.clear();
    },
  });
}

/**
 * Export current user's data
 */
export function useExportMyData() {
  return useMutation({
    mutationFn: async () => {
      const response = await api.get('/api/v1/auth/me/export', {
        responseType: 'blob',
      });
      return response.data;
    },
  });
}

