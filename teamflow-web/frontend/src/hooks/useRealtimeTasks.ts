/**
 * T119: useRealtimeTasks Hook
 *
 * React hook for auto-updating task list via WebSocket.
 * Integrates with React Query for seamless cache updates.
 */

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useTaskEvents } from './useTaskEvents';
import type { Task } from '@/types';

export interface UseRealtimeTasksOptions {
  url: string;
  token: string;
  enabled?: boolean;
}

export function useRealtimeTasks(options: UseRealtimeTasksOptions) {
  const queryClient = useQueryClient();
  const { ...eventState } = useTaskEvents(options);

  useEffect(() => {
    if (!eventState.isConnected) {
      return;
    }

    // Get the stream instance
    const stream = (window as any).__taskEventStream;
    if (!stream) {
      return;
    }

    // T121: Handle task_created events
    const handleTaskCreated = (data: any) => {
      queryClient.setQueryData<Task[]>(
        ['tasks'],
        (old = []) => [...old, data as Task]
      );
    };

    // T121: Handle task_updated events
    const handleTaskUpdated = (data: any) => {
      queryClient.setQueryData<Task[]>(
        ['tasks'],
        (old = []) =>
          old.map((task) =>
            task.id === data.task_id ? { ...task, ...data.changes, updated_at: new Date().toISOString() } : task
          )
      );
    };

    // Handle task_deleted events
    const handleTaskDeleted = (data: any) => {
      queryClient.setQueryData<Task[]>(
        ['tasks'],
        (old = []) => old.filter((task) => task.id !== data.task_id)
      );
    };

    // Register event handlers
    stream.on('task_created', handleTaskCreated);
    stream.on('task_updated', handleTaskUpdated);
    stream.on('task_deleted', handleTaskDeleted);

    // Cleanup
    return () => {
      stream.off('task_created', handleTaskCreated);
      stream.off('task_updated', handleTaskUpdated);
      stream.off('task_deleted', handleTaskDeleted);
    };
  }, [eventState.isConnected, queryClient]);

  return {
    ...eventState,
  };
}
