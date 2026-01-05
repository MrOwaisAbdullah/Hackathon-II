"use client";

import { useState, useCallback } from "react";
import type { Project } from "@/types";

interface UseProjectDrawerReturn {
  isDrawerOpen: boolean;
  selectedProject: Project | undefined;
  openDrawer: (project: Project) => void;
  closeDrawer: () => void;
}

export function useProjectDrawer(): UseProjectDrawerReturn {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | undefined>();

  const openDrawer = useCallback((project: Project) => {
    setSelectedProject(project);
    setIsDrawerOpen(true);
  }, []);

  const closeDrawer = useCallback(() => {
    setIsDrawerOpen(false);
    setSelectedProject(undefined);
  }, []);

  return {
    isDrawerOpen,
    selectedProject,
    openDrawer,
    closeDrawer,
  };
}
