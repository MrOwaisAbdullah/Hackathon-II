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
  ON_HOLD = "on_hold",
  COMPLETED = "completed",
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
  // Phase 10: User management fields
  active: boolean;
  is_project_manager: boolean;
  password_expires_at: string | null;
  must_change_password: boolean;
  temp_password?: string; // Only shown on create for admins
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
  due_date?: string;
  created_at: string;
  updated_at: string | null;
  archived_at: string | null;
  // Populated relations (from API includes)
  assignee?: User;
  project?: Project;
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

// ============ PHASE 10: USER CRUD TYPES (T235-T237) ============

/** User creation request */
export interface UserCreate {
  name: string;
  email: string;
  role: UserRole;
  is_project_manager?: boolean; // Optional: admin-only checkbox
}

/** User update request */
export interface UserUpdate {
  name?: string;
  email?: string;
  role?: UserRole;
  is_project_manager?: boolean;
}

/** User read response with temp password (shown only on create) */
export interface UserReadWithTempPassword extends User {
  temp_password?: string; // Only populated on create
}

// ============ PHASE 10: PROJECT CRUD TYPES (T238-T239) ============

/** Project creation request */
export interface ProjectCreate {
  name: string;
  description?: string;
  status?: ProjectStatus;
}

/** Project update request */
export interface ProjectUpdate {
  name?: string;
  description?: string;
  status?: ProjectStatus;
}

