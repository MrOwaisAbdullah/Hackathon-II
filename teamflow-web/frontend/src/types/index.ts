/** Shared TypeScript type definitions. */

/** UUID string type */
export type UUID = string;

/** User roles */
export enum UserRole {
  ADMIN = "admin",
  MEMBER = "member",
  VIEWER = "viewer",
}

/** Task status - matches backend TaskStatus enum */
export enum TaskStatus {
  TODO = "TODO",
  DOING = "DOING",
  REVIEW = "REVIEW",
  DONE = "DONE",
}

/** Task priority */
export enum TaskPriority {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
}

/** Project status */
export enum ProjectStatus {
  ACTIVE = "active",
  ARCHIVED = "archived",
}

/** Agency entity */
export interface Agency {
  id: UUID;
  name: string;
  email: string;
  created_at: string;
  updated_at: string | null;
}

/** User entity */
export interface User {
  id: UUID;
  email: string;
  name: string;
  role: UserRole;
  agency_id: UUID;
  created_at: string;
  updated_at: string | null;
}

/** Project entity */
export interface Project {
  id: UUID;
  name: string;
  description?: string;
  agency_id: UUID;
  status: ProjectStatus;
  created_at: string;
  updated_at: string | null;
}

/** Task entity */
export interface Task {
  id: UUID;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  project_id: UUID;
  agency_id: UUID;
  assignee_id: UUID | null;
  created_at: string;
  updated_at: string | null;
  archived_at: string | null;
}

/** Time entry entity */
export interface TimeEntry {
  id: UUID;
  task_id: UUID;
  user_id: UUID;
  agency_id: UUID;
  minutes: number;
  note?: string;
  created_at: string;
}

/** API response wrapper */
export interface ApiResponse<T> {
  data: T;
  error?: {
    message: string;
    status_code: number;
    path: string;
  };
}

/** Login request */
export interface LoginRequest {
  email: string;
  password: string;
}

/** Login response */
export interface LoginResponse {
  user: User;
  token: string;
}

/** Statistics for dashboard */
export interface DashboardStats {
  total_tasks: number;
  completed_tasks: number;
  total_projects: number;
  total_members: number;
}
