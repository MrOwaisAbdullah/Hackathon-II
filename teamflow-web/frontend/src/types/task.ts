/**
 * Task type definitions
 */

export type TaskStatus = 'TODO' | 'DOING' | 'REVIEW' | 'DONE' | 'ARCHIVED';

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  assignee_id?: string;
  project_id?: string;
  agency_id: string;
  created_at: string;
  updated_at: string;
  assignee?: {
    id: string;
    name: string;
    email: string;
    avatar_url?: string;
  };
  // Time tracking fields (US5)
  total_time?: number; // Total minutes logged for this task
  time_entries?: TimeEntry[];
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  assignee_id?: string;
  project_id?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  assignee_id?: string;
  project_id?: string;
}

export interface TaskStats {
  total: number;
  by_status: Record<TaskStatus, number>;
  by_priority: Record<TaskPriority, number>;
  completed_this_week: number;
  overdue: number;
}

// ============ TIME ENTRY TYPES (US5) ============

export interface TimeEntry {
  id: string;
  task_id: string;
  user_id: string;
  agency_id: string;
  duration_minutes: number;
  note?: string;
  entry_date?: string; // YYYY-MM-DD format
  created_at: string;
  user?: {
    id: string;
    name: string;
    email: string;
  };
}

export interface TimeEntryCreate {
  task_id: string;
  duration_minutes: number;
  note?: string;
  entry_date?: string; // YYYY-MM-DD format
}

export interface TimeEntryUpdate {
  duration_minutes?: number;
  note?: string;
  entry_date?: string;
}

export type TimeEntryRead = TimeEntry;

// ============ PROFITABILITY TYPES (US5) ============

export interface ProjectProfitability {
  project_id: string;
  project_name: string;
  total_tasks: number;
  completed_tasks: number;
  completion_percentage: number;
  total_hours: number;
  total_cost: number;
  total_revenue: number;
  profit: number;
  profit_margin: number;
}

// ============ TIMER STATE (US5 T132) ============

export interface TimerState {
  isRunning: boolean;
  elapsedSeconds: number;
  taskId?: string;
  startTime?: number;
}
