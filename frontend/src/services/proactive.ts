/**
 * Proactive features API client - reminders, goals, suggestions
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const defaultFetchOptions: RequestInit = {
  credentials: 'include',
};

export interface Reminder {
  memory_id: string;
  task_text: string;
  due_date: string;
  is_overdue: boolean;
  hours_until_due: number;
}

export interface Goal {
  memory_id: string;
  goal_text: string;
  progress: number;
  last_referenced: string;
  created_at: string;
}

export interface Task {
  memory_id: string;
  task_text: string;
  due_date: string | null;
  created_at: string;
  source: string;
}

export interface RemindersResponse {
  reminders: Reminder[];
  count: number;
}

export interface GoalsResponse {
  goals: Goal[];
  count: number;
}

export interface TasksResponse {
  tasks: Task[];
  count: number;
}

/**
 * Get pending task reminders
 */
export async function getReminders(): Promise<RemindersResponse> {
  const response = await fetch(`${API_BASE_URL}/proactive/reminders`, defaultFetchOptions);
  if (!response.ok) {
    throw new Error('Failed to fetch reminders');
  }
  return response.json();
}

/**
 * Mark a task as completed
 */
export async function markTaskCompleted(memoryId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/proactive/tasks/complete`, {
    ...defaultFetchOptions,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ memory_id: memoryId }),
  });
  if (!response.ok) {
    throw new Error('Failed to mark task as completed');
  }
}

/**
 * Get active goals with progress
 */
export async function getActiveGoals(): Promise<GoalsResponse> {
  const response = await fetch(`${API_BASE_URL}/proactive/goals`, defaultFetchOptions);
  if (!response.ok) {
    throw new Error('Failed to fetch goals');
  }
  return response.json();
}

/**
 * Get all pending tasks (regardless of due date)
 */
export async function getPendingTasks(): Promise<TasksResponse> {
  const response = await fetch(`${API_BASE_URL}/proactive/tasks`, defaultFetchOptions);
  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }
  return response.json();
}

/**
 * Sync tasks from vault daily notes
 */
export async function syncVaultTasks(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/proactive/sync-vault-tasks`, {
    ...defaultFetchOptions,
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to sync vault tasks');
  }
}

/**
 * Update a goal's progress percentage
 */
export async function updateGoalProgress(goalId: string, progress: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/proactive/goals/${goalId}/progress`, {
    ...defaultFetchOptions,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ progress }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to update goal progress');
  }
}
