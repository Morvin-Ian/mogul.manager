export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'blocked' | 'completed'
export type TaskPriority = 1 | 2 | 3 | 4
export type ProjectStatus = 'planning' | 'active' | 'on_hold' | 'completed' | 'archived'

export interface User {
  id: number
  username: string
  email: string
  profile_path: string | null
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface Workspace {
  id: number
  title: string
  description: string | null
  settings: Record<string, unknown> | null
  user_id: number
  is_archived: boolean
  created_at: string
  updated_at: string
}

export interface WorkspaceCreate {
  title: string
  description?: string | null
  settings?: Record<string, unknown> | null
}

export interface WorkspaceUpdate {
  title?: string
  description?: string | null
  settings?: Record<string, unknown> | null
  is_archived?: boolean
}

export interface Project {
  id: number
  workspace_id: number
  title: string
  description: string | null
  status: ProjectStatus
  ai_summary: string | null
  metadata_json: Record<string, unknown> | null
  start_date: string | null
  due_date: string | null
  completed_at: string | null
  is_archived: boolean
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  workspace_id: number
  title: string
  description?: string | null
  status?: ProjectStatus
  metadata_json?: Record<string, unknown> | null
  start_date?: string | null
  due_date?: string | null
}

export interface ProjectUpdate {
  title?: string
  description?: string | null
  status?: ProjectStatus
  metadata_json?: Record<string, unknown> | null
  start_date?: string | null
  due_date?: string | null
  is_archived?: boolean
}

export interface Task {
  id: number
  project_id: number
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  assigned_agent: string | null
  parent_task_id: number | null
  metadata_json: Record<string, unknown> | null
  estimated_hours: number | null
  actual_hours: number | null
  due_date: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  project_id: number
  title: string
  description?: string | null
  status?: TaskStatus
  priority?: TaskPriority
  assigned_agent?: string | null
  parent_task_id?: number | null
  metadata_json?: Record<string, unknown> | null
  estimated_hours?: number | null
  actual_hours?: number | null
  due_date?: string | null
}

export interface TaskUpdate {
  title?: string
  description?: string | null
  status?: TaskStatus
  priority?: TaskPriority
  assigned_agent?: string | null
  parent_task_id?: number | null
  metadata_json?: Record<string, unknown> | null
  estimated_hours?: number | null
  actual_hours?: number | null
  due_date?: string | null
}

export interface Comment {
  id: number
  user_id: number
  task_id: number
  content: string
  created_at: string
  updated_at: string
}

export interface CommentCreate {
  task_id: number
  content: string
}
