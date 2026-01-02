"use client";

import { useState, useCallback } from "react";

interface UseTaskDrawerReturn {
  isDrawerOpen: boolean;
  selectedTaskId: string | undefined;
  openDrawer: (taskId: string) => void;
  closeDrawer: () => void;
}

export function useTaskDrawer(): UseTaskDrawerReturn {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState<string | undefined>();

  const openDrawer = useCallback((taskId: string) => {
    setSelectedTaskId(taskId);
    setIsDrawerOpen(true);
  }, []);

  const closeDrawer = useCallback(() => {
    setIsDrawerOpen(false);
    setSelectedTaskId(undefined);
  }, []);

  return {
    isDrawerOpen,
    selectedTaskId,
    openDrawer,
    closeDrawer,
  };
}
