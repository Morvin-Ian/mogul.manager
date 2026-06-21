export type TaskStatus =
  | "todo"
  | "in_progress"
  | "review"
  | "blocked"
  | "completed";
export type TaskPriority = 1 | 2 | 3 | 4;
export type ProjectStatus =
  | "planning"
  | "active"
  | "on_hold"
  | "completed"
  | "archived";

export interface User {
  id: number;
  uuid: string;
  username: string;
  email: string;
  profile_path: string | null;
  google_id: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Workspace {
  id: number;
  uuid: string;
  title: string;
  description: string | null;
  settings: Record<string, unknown> | null;
  user_id: number;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceCreate {
  title: string;
  description?: string | null;
  settings?: Record<string, unknown> | null;
}

export interface WorkspaceUpdate {
  title?: string;
  description?: string | null;
  settings?: Record<string, unknown> | null;
  is_archived?: boolean;
}

export interface Project {
  id: number;
  uuid: string;
  workspace_uuid: string | null;
  workspace_id: number;
  workspace_title: string | null;
  created_by_id: number | null;
  title: string;
  description: string | null;
  status: ProjectStatus;
  ai_summary: string | null;
  metadata_json: Record<string, unknown> | null;
  start_date: string | null;
  due_date: string | null;
  completed_at: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  task_count: number;
  completed_count: number;
}

export interface ProjectCreate {
  workspace_id: number;
  title: string;
  description?: string | null;
  status?: ProjectStatus;
  metadata_json?: Record<string, unknown> | null;
  start_date?: string | null;
  due_date?: string | null;
}

export interface ProjectUpdate {
  title?: string;
  description?: string | null;
  status?: ProjectStatus;
  metadata_json?: Record<string, unknown> | null;
  start_date?: string | null;
  due_date?: string | null;
  is_archived?: boolean;
}

export interface Task {
  id: number;
  uuid: string;
  project_uuid: string | null;
  project_id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assigned_agent: string | null;
  assigned_to_id: number | null;
  assignee_name: string | null;
  assignee_email: string | null;
  assignee_avatar_url: string | null;
  position: number | null;
  parent_task_id: number | null;
  metadata_json: Record<string, unknown> | null;
  tags: Tag[];
  estimated_hours: number | null;
  actual_hours: number | null;
  due_date: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  comment_count?: number;
}

export interface TaskCreate {
  project_id: number;
  title: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigned_agent?: string | null;
  assigned_to_id?: number | null;
  parent_task_id?: number | null;
  metadata_json?: Record<string, unknown> | null;
  estimated_hours?: number | null;
  actual_hours?: number | null;
  due_date?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
  assigned_agent?: string | null;
  assigned_to_id?: number | null;
  parent_task_id?: number | null;
  metadata_json?: Record<string, unknown> | null;
  estimated_hours?: number | null;
  actual_hours?: number | null;
  due_date?: string | null;
}

export interface CommentUser {
  id: number;
  username: string;
  profile_path: string | null;
}

export interface Comment {
  id: number;
  uuid: string;
  user_id: number;
  task_id: number;
  parent_id: number | null;
  content: string;
  user: CommentUser | null;
  created_at: string;
  updated_at: string;
}

export interface CommentCreate {
  task_id: number;
  content: string;
  parent_id?: number | null;
}

export interface Conversation {
  id: number;
  uuid: string;
  user_id: number;
  title: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  uuid: string;
  conversation_id: number;
  role: string;
  content: string;
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface DocumentUpdate {
  project_id: number | null;
}

// ── Documents ──────────────────────────────────────────────────
export type DocumentStatus = "pending" | "processing" | "ready" | "failed";
export type DocumentFileType = "pdf" | "docx" | "txt" | "csv";

export interface Document {
  id: number;
  uuid: string;
  project_id: number | null;
  user_id: number;
  title: string;
  original_filename: string;
  file_type: DocumentFileType;
  file_size: number;
  status: DocumentStatus;
  summary: string | null;
  page_count: number | null;
  word_count: number | null;
  chunk_count: number | null;
  error_message: string | null;
  url: string | null;
  created_at: string;
  processed_at: string | null;
  workspace_id?: number | null;
  workspace_title?: string | null;
  project_title?: string | null;
}

export interface SearchHit {
  document_id: number;
  document_title: string;
  chunk_index: number;
  content: string;
  similarity: number;
}

// ── Members & Invitations ──────────────────────────────────────
export type MemberRole = "owner" | "admin" | "member";
export type InvitationStatus = "pending" | "accepted" | "expired" | "revoked";

export interface WorkspaceMember {
  id: number;
  uuid: string;
  workspace_id: number;
  user_id: number;
  role: MemberRole;
  joined_at: string;
  last_seen_at: string | null;
  user: {
    id: number;
    username: string;
    email: string;
    profile_path: string | null;
  };
}

export interface Invitation {
  id: number;
  uuid: string;
  workspace_id: number;
  email: string;
  role: MemberRole;
  token: string;
  invited_by_id: number;
  created_at: string;
  expires_at: string;
  status: InvitationStatus;
  workspace_title?: string;
}

export interface MyMembershipResponse {
  workspace_id: number;
  user_id: number;
  role: MemberRole;
  joined_at: string;
}

export interface AcceptInviteResponse {
  id: number;
  workspace_id: number;
  user_id: number;
  role: MemberRole;
  joined_at: string;
}

// ── Plans ────────────────────────────────────────────────────────────────────

export type PlanStatus = "draft" | "active" | "completed" | "cancelled";
export type StepStatus = "pending" | "in_progress" | "completed" | "skipped";
export type StepPriority = "low" | "medium" | "high" | "urgent";

export interface PlanStep {
  id: number;
  uuid: string;
  plan_id: number;
  title: string;
  description: string | null;
  step_order: number;
  priority: StepPriority;
  status: StepStatus;
  dependencies: number[] | null;
  linked_task_id: number | null;
  linked_task_uuid: string | null;
  linked_task_title: string | null;
  agent_notes: string | null;
  warning?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Plan {
  id: number;
  uuid: string;
  project_id: number;
  project_title: string | null;
  user_id: number;
  title: string;
  description: string | null;
  status: PlanStatus;
  steps: PlanStep[];
  created_at: string;
  updated_at: string;
}

export interface PlanCreate {
  title: string;
  description?: string | null;
  project_id: number;
}

export interface PlanUpdate {
  title?: string;
  description?: string | null;
  status?: PlanStatus;
}

export interface StepUpdate {
  title?: string;
  description?: string | null;
  status?: StepStatus;
  priority?: StepPriority;
  linked_task_id?: number | null;
  agent_notes?: string | null;
}

export interface StepCreate {
  title: string;
  description?: string | null;
  priority?: StepPriority;
  step_order?: number;
}

export interface Notification {
  id: number;
  uuid: string;
  user_id: number;
  notification_type: string;
  title: string;
  message: string | null;
  link: string | null;
  is_read: boolean;
  metadata_json: Record<string, unknown> | null;
  read_at: string | null;
  created_at: string;
}

export interface UnreadCount {
  count: number;
}

export type MilestoneStatus = "pending" | "achieved" | "cancelled";

export interface Milestone {
  id: number;
  uuid: string;
  project_id: number;
  name: string;
  description: string | null;
  status: MilestoneStatus;
  due_date: string | null;
  achieved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MilestoneCreate {
  name: string;
  description?: string | null;
  due_date?: string | null;
}

export interface MilestoneUpdate {
  name?: string;
  description?: string | null;
  status?: MilestoneStatus;
  due_date?: string | null;
}

export interface TaskAttachment {
  id: number;
  uuid: string;
  task_id: number;
  user_id: number;
  original_filename: string;
  file_size: number;
  mime_type: string;
  url: string;
  uploader_name: string | null;
  created_at: string;
}

export interface AttachmentList {
  items: TaskAttachment[];
  total: number;
}

export interface Tag {
  id: number;
  uuid: string;
  project_id: number;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface InvitationInfo {
  id: number;
  email: string;
  role: string;
  status: string;
  expires_at: string;
  workspace: { id: number | null; title: string | null };
}

export interface StatusCount {
  status: string;
  count: number;
}

export interface PriorityCount {
  priority: number;
  count: number;
}

export interface ProjectReport {
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  completion_pct: number;
  by_status: StatusCount[];
  by_priority: PriorityCount[];
}

export interface WorkspaceReport {
  total_projects: number;
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  completion_pct: number;
  by_status: StatusCount[];
  member_count: number;
}

export interface ActivityUser {
  id: number;
  username: string;
  profile_path: string | null;
}

export interface ActivityLog {
  id: number;
  uuid: string;
  workspace_id: number | null;
  project_id: number | null;
  task_id: number | null;
  user_id: number;
  entity_type: string;
  entity_id: number;
  action: string;
  summary: string | null;
  changes: Record<string, unknown> | null;
  created_at: string;
  user: ActivityUser | null;
}

export interface TaskDependencyRead {
  id: number;
  uuid: string;
  title: string;
  status: string;
  priority: number;
  assignee_name: string | null;
}

export interface TaskDependencyList {
  depends_on: TaskDependencyRead[];
  blocked_by: TaskDependencyRead[];
}
