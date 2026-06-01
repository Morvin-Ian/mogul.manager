<template>
  <div class="task-detail">
    <Loading v-if="taskStore.loading" label="Loading task…" />

    <template v-if="task">
      <div class="task-header">
        <button class="back-btn" @click="$router.back()">
          <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
            <path d="M10 13L5 8l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Back
        </button>
        <div class="task-header-main">
          <div class="task-title-row">
            <h2>{{ task.title }}</h2>
            <div class="header-actions">
              <button v-if="canEditTask" class="btn btn-sm" @click="editTask">
                <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                  <path d="M9.5 2.5l2 2L5 11H3v-2l6.5-6.5zM8.5 3.5l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Edit
              </button>
              <button v-if="isAdmin" class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
            </div>
          </div>

          <div class="task-chips">
            <span class="badge" :class="`badge-${task.status}`">{{ task.status.replace('_', ' ') }}</span>
            <span class="priority-chip" :class="`priority-chip-${task.priority}`">
              {{ priorityLabel }} priority
            </span>
            <span v-if="task.assignee_name" class="assignee-chip">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                <circle cx="6" cy="4" r="2.5" stroke="currentColor" stroke-width="1.2"/>
                <path d="M1.5 10.5c0-2.5 2-4 4.5-4s4.5 1.5 4.5 4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              {{ task.assignee_name }}
            </span>
            <span v-else-if="task.assigned_agent" class="agent-chip">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                <circle cx="6" cy="4" r="2.5" stroke="currentColor" stroke-width="1.2"/>
                <path d="M1.5 10.5c0-2.5 2-4 4.5-4s4.5 1.5 4.5 4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              {{ task.assigned_agent }}
            </span>
            <span v-if="task.due_date" class="date-chip">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              Due {{ formatDate(task.due_date) }}
            </span>
            <span v-if="task.estimated_hours" class="time-chip">Est. {{ task.estimated_hours }}h</span>
            <span v-if="task.actual_hours" class="time-chip">Actual {{ task.actual_hours }}h</span>
          </div>
        </div>
      </div>

      <!-- Description -->
      <div v-if="task.description" class="task-section">
        <h3 class="section-label">Description</h3>
        <p class="task-desc">{{ task.description }}</p>
      </div>

      <!-- Status update -->
      <div class="task-section">
        <h3 class="section-label">Status</h3>
        <StatusUpdate
          :task="task"
          :user-role="membership?.role ?? null"
          :assigned-to-id="task.assigned_to_id"
          :current-user-id="auth.user?.id ?? null"
          @updated="onStatusUpdated"
        />
      </div>

      <!-- Comments -->
      <div class="task-section">
        <h3 class="section-label">
          Comments
          <span class="comment-count">{{ comments.length }}</span>
        </h3>

        <div class="comment-input-wrap">
          <textarea
            v-model="newComment"
            rows="3"
            placeholder="Add a comment…"
            class="comment-textarea"
          ></textarea>
          <div class="comment-input-footer">
            <button
              class="btn btn-primary btn-sm"
              @click="addComment"
              :disabled="!newComment.trim()"
            >
              Post comment
            </button>
          </div>
        </div>

        <div v-if="comments.length === 0" class="empty-comments">No comments yet. Be the first to comment.</div>
        <div v-else class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-avatar">{{ (auth.user?.username ?? 'U').charAt(0).toUpperCase() }}</div>
            <div class="comment-body">
              <div class="comment-header">
                <span class="comment-author">{{ auth.user?.username }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>
              <p class="comment-text">{{ comment.content }}</p>
            </div>
            <button
              v-if="comment.user_id === auth.user?.id"
              class="btn btn-sm btn-danger comment-delete"
              @click="handleDeleteComment(comment.id)"
            >
              Delete
            </button>
          </div>
        </div>
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
import Loading from '../components/common/Loading.vue'

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

const priorityLabel = computed(() => {
  const labels: Record<number, string> = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' }
  return task.value ? labels[task.value.priority] || '' : ''
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
  if (task.value) {
    editingTask.value = { ...task.value }
    showForm.value = true
  }
}

function closeForm() {
  showForm.value = false
  editingTask.value = null
}

async function onSave(data: Record<string, any>) {
  if (editingTask.value) {
    await taskStore.update(taskId.value, data)
  }
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
  padding: 36px 32px;
  max-width: 780px;
}

.task-header {
  margin-bottom: 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  font-family: inherit;
  transition: all 0.12s;
  align-self: flex-start;
}

.back-btn:hover { background: var(--surface); color: var(--text); border-color: var(--border-strong); }

.task-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.task-title-row h2 {
  font-size: 24px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.7px;
  line-height: 1.25;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.task-chips {
  display: flex;
  align-items: center;
  gap: 7px;
  flex-wrap: wrap;
}

.priority-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  border: 1px solid transparent;
}

.priority-chip-1 { background: #ECFDF5; color: #047857; border-color: #A7F3D0; }
.priority-chip-2 { background: #FFFBEB; color: #92400E; border-color: #FDE68A; }
.priority-chip-3 { background: #FFF7ED; color: #C2410C; border-color: #FED7AA; }
.priority-chip-4 { background: #FFF1F2; color: #BE123C; border-color: #FECDD3; }

.assignee-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--primary);
  background: var(--primary-light);
  border: 1.5px solid var(--primary-border);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-weight: 600;
}

.agent-chip, .date-chip, .time-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg);
  border: 1.5px solid var(--border);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

/* Sections */
.task-section {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 22px 24px;
  margin-bottom: 14px;
}

.section-label {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: var(--text-light);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-count {
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text-muted);
  border-radius: var(--radius-full);
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: none;
}

.task-desc {
  font-size: 14px;
  line-height: 1.75;
  color: var(--text);
  white-space: pre-wrap;
}

/* Comments */
.comment-input-wrap {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 22px;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.comment-input-wrap:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.comment-textarea {
  width: 100%;
  padding: 14px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  color: var(--text);
  display: block;
  line-height: 1.6;
}

.comment-textarea:focus { outline: none; }
.comment-textarea::placeholder { color: var(--text-light); }

.comment-input-footer {
  padding: 10px 14px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border);
  background: var(--bg);
}

.empty-comments {
  font-size: 13.5px;
  color: var(--text-muted);
  padding: 16px 0;
  text-align: center;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.comment-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
}

.comment-body {
  flex: 1;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 7px;
}

.comment-author {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.1px;
}

.comment-date {
  font-size: 11.5px;
  color: var(--text-light);
}

.comment-text {
  font-size: 13.5px;
  line-height: 1.65;
  color: var(--text);
}

.comment-delete {
  flex-shrink: 0;
  align-self: flex-start;
  margin-top: 4px;
}
</style>
