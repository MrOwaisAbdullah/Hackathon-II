"use client";

/**
 * useTimeTracking - Hook for managing timer state and time entry operations (US5 T132).
 *
 * Provides:
 * - Timer state (running, elapsed time)
 * - Start/stop/reset timer controls
 * - Time entry CRUD operations via React Query
 */

import { useState, useCallback, useRef, useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { TimeEntry, TimeEntryCreate, TimerState } from "@/types/task";

/**
 * Hook for managing timer state
 */
export function useTimer() {
  const [timer, setTimer] = useState<TimerState>({
    isRunning: false,
    elapsedSeconds: 0,
  });
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Start timer
  const start = useCallback((taskId?: string) => {
    setTimer((prev) => ({
      ...prev,
      isRunning: true,
      taskId,
      startTime: Date.now() - (prev.elapsedSeconds * 1000),
    }));
  }, []);

  // Stop timer
  const stop = useCallback(() => {
    setTimer((prev) => ({
      ...prev,
      isRunning: false,
    }));
  }, []);

  // Reset timer
  const reset = useCallback(() => {
    setTimer({
      isRunning: false,
      elapsedSeconds: 0,
      taskId: undefined,
      startTime: undefined,
    });
  }, []);

  // Update elapsed time while running
  useEffect(() => {
    if (timer.isRunning) {
      intervalRef.current = setInterval(() => {
        setTimer((prev) => {
          if (!prev.isRunning || !prev.startTime) return prev;
          const elapsed = Math.floor((Date.now() - prev.startTime) / 1000);
          return { ...prev, elapsedSeconds: elapsed };
        });
      }, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [timer.isRunning, timer.startTime]);

  return {
    timer,
    start,
    stop,
    reset,
  };
}

/**
 * Hook for time entry operations
 */
export function useTimeEntries(taskId?: string) {
  const queryClient = useQueryClient();

  // Fetch time entries for a task
  const {
    data: timeEntries = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["time-entries", taskId],
    queryFn: async () => {
      if (!taskId) return [];
      const response = await api.get<{ time_entries: TimeEntry[] }>(
        `/api/v1/time-entries?task_id=${taskId}`
      );
      return response.data.time_entries;
    },
    enabled: !!taskId,
    refetchInterval: 10000, // Poll every 10 seconds
  });

  // Create time entry
  const createTimeEntry = useMutation({
    mutationFn: async (data: TimeEntryCreate) => {
      const response = await api.post<TimeEntry>("/api/v1/time-entries", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["time-entries"] });
      queryClient.invalidateQueries({ queryKey: ["project-profitability"] });
    },
  });

  // Update time entry
  const updateTimeEntry = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<TimeEntry> }) => {
      const response = await api.patch<TimeEntry>(
        `/api/v1/time-entries/${id}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["time-entries"] });
      queryClient.invalidateQueries({ queryKey: ["project-profitability"] });
    },
  });

  // Delete time entry
  const deleteTimeEntry = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/time-entries/${id}`);
      return id;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["time-entries"] });
      queryClient.invalidateQueries({ queryKey: ["project-profitability"] });
    },
  });

  // Calculate total time from the time entries array (more reliable than separate API call)
  const totalTime = timeEntries?.reduce(
    (sum, entry) => sum + (entry.duration_minutes || 0),
    0
  ) || 0;

  // Calculate total hours and format time
  const totalHours = totalTime / 60;
  const formattedTime = formatDuration(totalTime);

  // Refetch function for data updates
  const refetchTotalTime = () => {
    queryClient.invalidateQueries({ queryKey: ["time-entries", taskId] });
  };

  return {
    timeEntries,
    isLoading,
    error,
    createTimeEntry: createTimeEntry.mutateAsync,
    updateTimeEntry: updateTimeEntry.mutateAsync,
    deleteTimeEntry: deleteTimeEntry.mutateAsync,
    totalTime: totalTime,
    totalHours,
    formattedTime,
    refetchTotalTime,
    isCreating: createTimeEntry.isPending,
    isUpdating: updateTimeEntry.isPending,
    isDeleting: deleteTimeEntry.isPending,
  };
}

/**
 * Format duration in minutes to human-readable format
 */
export function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) {
    return `${mins}m`;
  } else if (mins === 0) {
    return `${hours}h`;
  } else {
    return `${hours}h ${mins}m`;
  }
}

/**
 * Format seconds to HH:MM:SS
 */
export function formatTimer(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const pad = (n: number) => n.toString().padStart(2, "0");

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`;
  }
  return `${pad(minutes)}:${pad(secs)}`;
}

/**
 * Combined hook for both timer and time entry operations
 */
export function useTimeTracking(taskId?: string) {
  const timer = useTimer();
  const timeEntries = useTimeEntries(taskId);

  // Submit timer as time entry
  const submitTimerEntry = useCallback(
    async (note?: string) => {
      const timerState = timer.timer;
      if (!timerState.taskId || timerState.elapsedSeconds === 0) {
        throw new Error("No timer running or elapsed time is zero");
      }

      const durationMinutes = Math.ceil(timerState.elapsedSeconds / 60);

      await timeEntries.createTimeEntry({
        task_id: timerState.taskId,
        duration_minutes: durationMinutes,
        note,
      });

      timer.reset();
    },
    [timer, timeEntries]
  );

  return {
    ...timer,
    ...timeEntries,
    submitTimerEntry,
  };
}
