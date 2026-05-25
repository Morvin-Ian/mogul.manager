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
  assigned_to_id: number | null
  assignee_name: string | null
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
  assigned_to_id?: number | null
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
  assigned_to_id?: number | null
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

export interface Conversation {
  id: number
  user_id: number
  title: string | null
  is_archived: boolean
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  conversation_id: number
  role: string
  content: string
  created_at: string
}

export interface ConversationDetail extends Conversation {
  messages: Message[]
}

// ── Plans ──────────────────────────────────────────────────────
export type PlanStatus = 'draft' | 'active' | 'completed' | 'cancelled'
export type StepStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
export type StepPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface PlanStep {
  id: number
  plan_id: number
  title: string
  description: string | null
  priority: StepPriority
  status: StepStatus
  step_order: number
  dependencies: number[]
  linked_task_id: number | null
  agent_notes: string | null
  created_at: string
  updated_at: string
}

export interface Plan {
  id: number
  user_id: number
  workspace_id: number | null
  title: string
  description: string | null
  status: PlanStatus
  steps: PlanStep[]
  created_at: string
  updated_at: string
}

export interface PlanCreate {
  title: string
  description?: string | null
  workspace_id?: number | null
}

// ── Documents ──────────────────────────────────────────────────
export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'failed'
export type DocumentFileType = 'pdf' | 'docx' | 'txt' | 'csv'

export interface Document {
  id: number
  user_id: number
  title: string
  original_filename: string
  file_type: DocumentFileType
  file_size: number
  status: DocumentStatus
  summary: string | null
  page_count: number | null
  word_count: number | null
  chunk_count: number | null
  error_message: string | null
  url: string | null
  created_at: string
  processed_at: string | null
}

export interface SearchHit {
  document_id: number
  document_title: string
  chunk_index: number
  content: string
  similarity: number
}

// ── Members & Invitations ──────────────────────────────────────
export type MemberRole = 'owner' | 'admin' | 'member'
export type InvitationStatus = 'pending' | 'accepted' | 'expired' | 'revoked'

export interface WorkspaceMember {
  id: number
  workspace_id: number
  user_id: number
  role: MemberRole
  joined_at: string
  last_seen_at: string | null
  user: { id: number; username: string; email: string; profile_path: string | null }
}

export interface Invitation {
  id: number
  workspace_id: number
  email: string
  role: MemberRole
  token: string
  invited_by_id: number
  created_at: string
  expires_at: string
  status: InvitationStatus
  workspace_title?: string
}
