<template>
  <div class="task-detail">
    <!-- Skeleton while loading -->
    <template v-if="taskStore.loading">
      <div class="sk-page">
        <!-- Top bar -->
        <div class="sk-topbar">
          <div class="sk sk-back"></div>
          <div class="sk sk-btn-sm"></div>
        </div>
        <!-- Hero -->
        <div class="sk-hero">
          <div class="sk sk-title"></div>
          <div class="sk sk-title sk-title-short"></div>
          <div class="sk-chips">
            <div class="sk sk-chip"></div>
            <div class="sk sk-chip"></div>
            <div class="sk sk-chip"></div>
          </div>
        </div>
        <!-- Two-column layout -->
        <div class="sk-layout">
          <div class="sk-main">
            <div class="sk-section">
              <div class="sk sk-section-label"></div>
              <div class="sk sk-body-line"></div>
              <div class="sk sk-body-line"></div>
              <div class="sk sk-body-line sk-body-short"></div>
            </div>
            <div class="sk-section">
              <div class="sk sk-section-label"></div>
              <div v-for="n in 3" :key="n" class="sk-checklist-row">
                <div class="sk sk-checkbox"></div>
                <div class="sk sk-check-text"></div>
              </div>
            </div>
          </div>
          <aside class="sk-sidebar">
            <div class="sk-props">
              <div class="sk sk-props-title"></div>
              <div v-for="n in 5" :key="n" class="sk-prop-row">
                <div class="sk sk-prop-label"></div>
                <div class="sk sk-prop-val"></div>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </template>

    <template v-if="task">
      <!-- Page head -->
      <div class="page-head">
        <button class="back-pill" @click="$router.back()">
          <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
            <path d="M8 2L4 6l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Back
        </button>
        <div class="page-actions">
          <button v-if="canEditTask" class="btn btn-sm" @click="editTask">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M9.5 2.5l2 2L5 11H3v-2l6.5-6.5zM8.5 3.5l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
          <button v-if="isAdmin" class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
      </div>

      <!-- Title + status row -->
      <div class="task-hero">
        <h1 class="task-title">{{ task.title }}</h1>
        <div class="task-meta-row">
          <span class="status-pill" :class="`sp-${task.status}`">
            <span class="sp-dot"></span>
            {{ STATUS_LABELS[task.status] ?? task.status }}
          </span>
          <span class="priority-pill" :class="`pp-${task.priority}`">
            {{ PRIORITY_LABELS[task.priority] ?? task.priority }}
          </span>
          <span v-if="task.due_date" class="meta-chip" :class="{ 'meta-chip--overdue': isOverdue }">
            <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
              <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
              <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            {{ isOverdue ? 'Overdue · ' : '' }}Due {{ formatDate(task.due_date) }}
          </span>
        </div>
      </div>

      <!-- Two-column layout -->
      <div class="task-layout">

        <!-- ── Main content ── -->
        <div class="task-main">

          <!-- Description -->
          <section v-if="task.description" class="task-section">
            <h3 class="section-title">Description</h3>
            <p class="task-desc">{{ task.description }}</p>
          </section>

          <!-- Status update -->
          <section class="task-section">
            <h3 class="section-title">Update status</h3>
            <StatusUpdate
              :task="task"
              :user-role="membership?.role ?? null"
              :assigned-to-id="task.assigned_to_id"
              :current-user-id="auth.user?.id ?? null"
              @updated="onStatusUpdated"
            />
          </section>

          <!-- Comments -->
          <section class="task-section">
            <h3 class="section-title">
              Comments
              <span class="count-badge">{{ comments.length }}</span>
            </h3>

            <div class="comment-composer">
              <div class="composer-avatar">
                <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" :alt="auth.user?.username" />
                <span v-else>{{ (auth.user?.username ?? 'U').charAt(0).toUpperCase() }}</span>
              </div>
              <div class="composer-box">
                <textarea
                  v-model="newComment"
                  rows="3"
                  placeholder="Add a comment…"
                  class="composer-textarea"
                />
                <div class="composer-footer">
                  <button class="btn btn-sm" :disabled="!newComment.trim()" @click="addComment">
                    Post comment
                  </button>
                </div>
              </div>
            </div>

            <div v-if="comments.length === 0" class="empty-comments">
              No comments yet.
            </div>
            <div v-else class="comments-list">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-avatar">
                  <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" :alt="auth.user?.username" />
                  <span v-else>{{ (auth.user?.username ?? 'U').charAt(0).toUpperCase() }}</span>
                </div>
                <div class="comment-body">
                  <div class="comment-header">
                    <span class="comment-author">{{ auth.user?.username }}</span>
                    <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                  </div>
                  <p class="comment-text">{{ comment.content }}</p>
                </div>
                <button
                  v-if="comment.user_id === auth.user?.id"
                  class="comment-delete-btn"
                  title="Delete comment"
                  @click="handleDeleteComment(comment.id)"
                >
                  <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
                    <path d="M2 3h8M5 3V1.5h2V3M4 3v6.5h4V3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </section>
        </div>

        <!-- ── Sidebar ── -->
        <aside class="task-sidebar">
          <div class="props-card">
            <h4 class="props-title">Properties</h4>

            <div class="props-list">
              <div class="prop-row">
                <span class="prop-label">Status</span>
                <span class="status-pill status-pill--sm" :class="`sp-${task.status}`">
                  <span class="sp-dot"></span>
                  {{ STATUS_LABELS[task.status] ?? task.status }}
                </span>
              </div>

              <div class="prop-row">
                <span class="prop-label">Priority</span>
                <span class="priority-pill priority-pill--sm" :class="`pp-${task.priority}`">
                  {{ PRIORITY_LABELS[task.priority] }}
                </span>
              </div>

              <div v-if="task.assignee_name || task.assigned_agent" class="prop-row">
                <span class="prop-label">Assignee</span>
                <div class="assignee-value">
                  <div class="assignee-avatar-sm">
                    <img v-if="task.assignee_avatar_url" :src="task.assignee_avatar_url" :alt="task.assignee_name ?? ''" />
                    <span v-else>{{ (task.assignee_name ?? task.assigned_agent ?? 'A').charAt(0).toUpperCase() }}</span>
                  </div>
                  <span class="prop-text">{{ task.assignee_name ?? task.assigned_agent }}</span>
                </div>
              </div>

              <div v-if="!task.assignee_name && !task.assigned_agent" class="prop-row">
                <span class="prop-label">Assignee</span>
                <span class="prop-empty">Unassigned</span>
              </div>

              <div class="prop-row">
                <span class="prop-label">Due date</span>
                <span v-if="task.due_date" class="prop-text" :class="{ 'prop-text--overdue': isOverdue }">
                  {{ formatDate(task.due_date) }}
                </span>
                <span v-else class="prop-empty">Not set</span>
              </div>

              <div v-if="task.estimated_hours" class="prop-row">
                <span class="prop-label">Est. hours</span>
                <span class="prop-text">{{ task.estimated_hours }}h</span>
              </div>

              <div v-if="task.actual_hours" class="prop-row">
                <span class="prop-label">Actual hrs</span>
                <span class="prop-text">{{ task.actual_hours }}h</span>
              </div>

              <div class="prop-row prop-row--last">
                <span class="prop-label">Created</span>
                <span class="prop-text">{{ formatDate(task.created_at) }}</span>
              </div>
            </div>
          </div>
        </aside>
      </div>

      <TaskModal
        v-if="showForm"
        :task="editingTask"
        @close="closeForm"
        @saved="onSave"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore } from '../stores/tasks'
import { useAuthStore } from '../stores/auth'
import { useMembersStore } from '../stores/members'
import { useConfirm } from '../composables/useConfirm'
import type { Task, Comment } from '../types'
import { get } from '../stores/client'
import TaskModal from '../components/task/TaskModal.vue'
import StatusUpdate from '../components/task/StatusUpdate.vue'

const STATUS_LABELS: Record<string, string> = {
  todo: 'To Do',
  in_progress: 'In Progress',
  review: 'In Review',
  blocked: 'Blocked',
  completed: 'Completed',
}

const PRIORITY_LABELS: Record<number, string> = {
  1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent',
}

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const auth = useAuthStore()
const membersStore = useMembersStore()
const { confirm } = useConfirm()

const showForm = ref(false)
const editingTask = ref<Task | null>(null)
const comments = ref<Comment[]>([])
const newComment = ref('')

const taskId = computed(() => route.params.id as string)
const task = computed(() => taskStore.current)
const membership = computed(() => membersStore.myMembership)
const isAdmin = computed(() => membership.value?.role === 'admin' || membership.value?.role === 'owner')
const canEditTask = computed(() => isAdmin.value || task.value?.assigned_to_id === auth.user?.id)

const isOverdue = computed(() => {
  if (!task.value?.due_date) return false
  if (task.value.status === 'completed') return false
  return new Date(task.value.due_date) < new Date()
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

watch(taskId, async (id) => {
  if (id) {
    try {
      await taskStore.fetchOne(id)
      const loadedTask = taskStore.current
      if (loadedTask) {
        comments.value = await taskStore.fetchComments(loadedTask.id)
        const wsUuid = loadedTask.project_uuid
          ? await get<{ workspace_uuid: string | null }>(`/projects/${loadedTask.project_uuid}`)
              .then(p => p.workspace_uuid)
          : null
        if (wsUuid) await membersStore.fetchMyMembership(wsUuid)
      }
    } catch {
      router.push('/')
    }
  }
}, { immediate: true })

function editTask() {
  if (task.value) { editingTask.value = { ...task.value }; showForm.value = true }
}
function closeForm() { showForm.value = false; editingTask.value = null }

async function onSave(data: Record<string, any>) {
  if (editingTask.value) await taskStore.update(taskId.value, data)
  closeForm()
}

async function handleDelete() {
  if (!task.value) return
  const ok = await confirm({
    title: 'Delete task?',
    message: `"${task.value.title}" will be permanently removed along with all its comments.`,
    confirmLabel: 'Yes, delete task',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  const pUuid = task.value.project_uuid ?? task.value.project_id
  await taskStore.remove(taskId.value)
  router.push(`/projects/${pUuid}`)
}

async function addComment() {
  if (!newComment.value.trim()) return
  const c = await taskStore.createComment({ task_id: task.value!.id, content: newComment.value })
  comments.value.push(c)
  newComment.value = ''
}

async function handleDeleteComment(id: number) {
  const ok = await confirm({
    title: 'Delete comment?',
    message: 'This comment will be permanently deleted.',
    confirmLabel: 'Delete comment',
    danger: true,
  })
  if (!ok) return
  await taskStore.deleteComment(id)
  comments.value = comments.value.filter((c) => c.id !== id)
}

function onStatusUpdated() {
  taskStore.fetchOne(taskId.value)
}
</script>

<style scoped>
.task-detail {
  padding: 36px 40px 80px;
}

/* ── Page head ── */
.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.back-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.back-pill:hover { background: var(--bg); color: var(--text); border-color: var(--border-strong); }

.page-actions { display: flex; gap: 8px; }

/* ── Hero ── */
.task-hero {
  margin-bottom: 28px;
}

.task-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.8px;
  line-height: 1.2;
  margin-bottom: 12px;
}

.task-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* ── Status pill ── */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 11px;
  border-radius: var(--radius-full);
}
.status-pill--sm { font-size: 11px; padding: 3px 9px; }

.sp-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

.sp-todo        { background: rgba(100,116,139,0.12); color: #475569; }
.sp-todo .sp-dot { background: #94A3B8; }
.sp-in_progress { background: rgba(245,158,11,0.12);  color: #A87800; }
.sp-in_progress .sp-dot { background: #F59E0B; }
.sp-review      { background: rgba(99,102,241,0.12);  color: #4338CA; }
.sp-review .sp-dot { background: #6366F1; }
.sp-blocked     { background: rgba(207,32,47,0.10);   color: var(--danger); }
.sp-blocked .sp-dot { background: var(--danger); }
.sp-completed   { background: rgba(0,186,124,0.14);   color: #00845A; }
.sp-completed .sp-dot { background: #00BA7C; }

:global([data-theme="dark"]) .sp-todo        { background: rgba(148,163,184,0.12); color: #94A3B8; }
:global([data-theme="dark"]) .sp-in_progress { background: rgba(255,179,0,0.14);   color: #FFB300; }
:global([data-theme="dark"]) .sp-review      { background: rgba(129,140,248,0.14); color: #818CF8; }
:global([data-theme="dark"]) .sp-blocked     { background: rgba(255,107,120,0.14); color: #FF6B78; }
:global([data-theme="dark"]) .sp-completed   { background: rgba(0,186,124,0.18);   color: #00BA7C; }

/* ── Priority pill ── */
.priority-pill {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 11px;
  border-radius: var(--radius-full);
}
.priority-pill--sm { font-size: 11px; padding: 3px 9px; }

.pp-1 { background: #ECFDF5; color: #047857; }
.pp-2 { background: #FFFBEB; color: #92400E; }
.pp-3 { background: #FFF7ED; color: #C2410C; }
.pp-4 { background: #FFF1F2; color: #BE123C; }

:global([data-theme="dark"]) .pp-1 { background: rgba(0,186,124,0.14);   color: #00BA7C; }
:global([data-theme="dark"]) .pp-2 { background: rgba(255,179,0,0.14);   color: #FFB300; }
:global([data-theme="dark"]) .pp-3 { background: rgba(239,68,68,0.14);   color: #F87171; }
:global([data-theme="dark"]) .pp-4 { background: rgba(255,107,120,0.16); color: #FF6B78; }

/* ── Meta chip ── */
.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg);
  border: 1.5px solid var(--border);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}
.meta-chip--overdue {
  background: var(--danger-bg);
  border-color: var(--danger-border);
  color: var(--danger);
}

/* ── Two-column layout ── */
.task-layout {
  display: flex;
  align-items: flex-start;
  gap: 28px;
}

.task-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* ── Sections ── */
.task-section {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px 24px;
}

.section-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-light);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-badge {
  font-size: 11px;
  font-weight: 700;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  padding: 1px 7px;
  color: var(--text-muted);
  text-transform: none;
  letter-spacing: 0;
}

.task-desc {
  font-size: 14px;
  line-height: 1.75;
  color: var(--text);
  white-space: pre-wrap;
}

/* ── Comment composer ── */
.comment-composer {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.composer-avatar,
.comment-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #1c1c1e;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
  overflow: hidden;
}
:global([data-theme="dark"]) .composer-avatar,
:global([data-theme="dark"]) .comment-avatar { background: #38444D; }

.composer-avatar img,
.comment-avatar img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.composer-box {
  flex: 1;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: border-color 0.14s, box-shadow 0.14s;
}
.composer-box:focus-within {
  border-color: var(--border-strong);
  box-shadow: 0 0 0 3px rgba(10,11,13,0.06);
}
:global([data-theme="dark"]) .composer-box:focus-within {
  box-shadow: 0 0 0 3px rgba(255,255,255,0.05);
}

.composer-textarea {
  width: 100%;
  padding: 12px 14px;
  border: none;
  background: transparent;
  font-size: 13.5px;
  font-family: inherit;
  resize: none;
  color: var(--text);
  display: block;
  line-height: 1.6;
  outline: none;
}
.composer-textarea::placeholder { color: var(--text-light); }

.composer-footer {
  padding: 8px 12px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border);
}

/* ── Comments list ── */
.empty-comments {
  font-size: 13px;
  color: var(--text-light);
  text-align: center;
  padding: 20px 0 6px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.comment-body {
  flex: 1;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 11px 14px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.comment-author { font-size: 13px; font-weight: 700; color: var(--text); }
.comment-date   { font-size: 11.5px; color: var(--text-light); }
.comment-text   { font-size: 13.5px; line-height: 1.65; color: var(--text); }

.comment-delete-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: transparent;
  border: 1.5px solid transparent;
  color: var(--text-light);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  margin-top: 2px;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.comment-delete-btn:hover {
  background: var(--danger-bg);
  color: var(--danger);
  border-color: var(--danger-border);
}

/* ── Sidebar ── */
.task-sidebar {
  width: 252px;
  flex-shrink: 0;
  position: sticky;
  top: 24px;
}

.props-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.props-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-light);
  padding: 16px 18px 12px;
  border-bottom: 1px solid var(--border);
}

.props-list {
  padding: 4px 0;
}

.prop-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 18px;
  border-bottom: 1px solid var(--border);
}
.prop-row--last { border-bottom: none; }

.prop-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-light);
  flex-shrink: 0;
  white-space: nowrap;
}

.prop-text {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text);
  text-align: right;
}
.prop-text--overdue { color: var(--danger); }

.prop-empty {
  font-size: 12px;
  color: var(--text-light);
  font-style: italic;
}

.assignee-value {
  display: flex;
  align-items: center;
  gap: 7px;
}

.assignee-avatar-sm {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #1c1c1e;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 800;
  flex-shrink: 0;
  overflow: hidden;
}
:global([data-theme="dark"]) .assignee-avatar-sm { background: #38444D; }
.assignee-avatar-sm img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

/* ── Skeleton ── */
@keyframes sk-shimmer { 0%{background-position:-600px 0} 100%{background-position:600px 0} }
.sk {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 600px 100%;
  animation: sk-shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
}
.sk-page    { padding: 36px 40px 80px; display: flex; flex-direction: column; gap: 20px; }
.sk-topbar  { display: flex; align-items: center; justify-content: space-between; }
.sk-back    { height: 26px; width: 70px; border-radius: 99px; }
.sk-btn-sm  { height: 28px; width: 52px; border-radius: 8px; }
.sk-hero    { display: flex; flex-direction: column; gap: 10px; padding: 20px 0 4px; }
.sk-title   { height: 30px; width: 75%; }
.sk-title-short { width: 50%; height: 30px; }
.sk-chips   { display: flex; gap: 8px; }
.sk-chip    { height: 22px; width: 80px; border-radius: 99px; }
.sk-layout  { display: grid; grid-template-columns: 1fr 280px; gap: 28px; }
.sk-main    { display: flex; flex-direction: column; gap: 24px; }
.sk-section { display: flex; flex-direction: column; gap: 8px; }
.sk-section-label { height: 11px; width: 90px; margin-bottom: 4px; }
.sk-body-line  { height: 13px; width: 100%; }
.sk-body-short { width: 70%; }
.sk-checklist-row { display: flex; align-items: center; gap: 10px; }
.sk-checkbox   { width: 16px; height: 16px; border-radius: 4px; flex-shrink: 0; }
.sk-check-text { height: 13px; flex: 1; }
.sk-sidebar { }
.sk-props   { background: var(--surface); border: 1.5px solid var(--border); border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
.sk-props-title { height: 13px; width: 80px; margin-bottom: 4px; }
.sk-prop-row { display: flex; align-items: center; justify-content: space-between; }
.sk-prop-label { height: 12px; width: 60px; }
.sk-prop-val   { height: 20px; width: 90px; border-radius: 99px; }
</style>
