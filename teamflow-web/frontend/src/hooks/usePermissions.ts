"use client";

import { useMemo } from "react";
import { useAuth } from "./useAuth";
import type { UserRole } from "@/types";

/**
 * Permission check hook for role-based UI control.
 *
 * Provides helper methods to check if the current user has specific permissions
 * based on their role. Used to conditionally render admin-only UI elements.
 */
export function usePermissions() {
  const { user } = useAuth();

  const isAdmin = useMemo(() => {
    return user?.role === UserRole.ADMIN;
  }, [user?.role]);

  const isProjectManager = useMemo(() => {
    return user?.is_project_manager === true || user?.role === UserRole.ADMIN;
  }, [user?.is_project_manager, user?.role]);

  const canManageUsers = useMemo(() => {
    return user?.role === UserRole.ADMIN;
  }, [user?.role]);

  const canManageProjects = useMemo(() => {
    return user?.is_project_manager === true || user?.role === UserRole.ADMIN;
  }, [user?.is_project_manager, user?.role]);

  const canEditTask = useMemo(() => {
    // Both admins and project managers can edit tasks
    // Regular members can only edit their own assigned tasks
    return user?.role === UserRole.ADMIN || user?.is_project_manager === true;
  }, [user?.role, user?.is_project_manager]);

  const canDeleteUser = useMemo(() => {
    return user?.role === UserRole.ADMIN;
  }, [user?.role]);

  const canAssignProjectManager = useMemo(() => {
    return user?.role === UserRole.ADMIN;
  }, [user?.role]);

  return {
    isAdmin,
    isProjectManager,
    canManageUsers,
    canManageProjects,
    canEditTask,
    canDeleteUser,
    canAssignProjectManager,
    // Convenience methods
    isMember: user?.role === UserRole.MEMBER,
  };
}
