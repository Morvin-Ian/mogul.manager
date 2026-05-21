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
              <button class="btn btn-sm" @click="editTask">
                <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                  <path d="M9.5 2.5l2 2L5 11H3v-2l6.5-6.5zM8.5 3.5l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Edit
              </button>
              <button class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
            </div>
          </div>

          <div class="task-chips">
            <span class="badge" :class="`badge-${task.status}`">{{ task.status.replace('_', ' ') }}</span>
            <span class="priority-chip" :class="`priority-chip-${task.priority}`">
              {{ priorityLabel }} priority
            </span>
            <span v-if="task.assigned_agent" class="agent-chip">
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
        <StatusUpdate :task="task" @updated="onStatusUpdated" />
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
import type { Task, Comment } from '../types'
import TaskModal from '../components/task/TaskModal.vue'
import StatusUpdate from '../components/task/StatusUpdate.vue'
import Loading from '../components/common/Loading.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const auth = useAuthStore()

const showForm = ref(false)
const editingTask = ref<Task | null>(null)
const comments = ref<Comment[]>([])
const newComment = ref('')

const taskId = computed(() => Number(route.params.id))
const task = computed(() => taskStore.current)

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
      comments.value = await taskStore.fetchComments(id)
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
  if (!confirm('Delete this task?')) return
  const pid = task.value.project_id
  await taskStore.remove(taskId.value)
  router.push(`/projects/${pid}`)
}

async function addComment() {
  if (!newComment.value.trim()) return
  const c = await taskStore.createComment({ task_id: taskId.value, content: newComment.value })
  comments.value.push(c)
  newComment.value = ''
}

async function handleDeleteComment(id: number) {
  if (!confirm('Delete this comment?')) return
  await taskStore.deleteComment(id)
  comments.value = comments.value.filter((c) => c.id !== id)
}

function onStatusUpdated() {
  taskStore.fetchOne(taskId.value)
}
</script>

<style scoped>
.task-detail {
  padding: 28px 32px;
  max-width: 760px;
}

.task-header {
  margin-bottom: 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
  transition: color 0.1s;
  align-self: flex-start;
}

.back-btn:hover { color: var(--text); }

.task-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
}

.task-title-row h2 {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
  line-height: 1.3;
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
  font-weight: 700;
}

.priority-chip-1 { background: #E6F9F1; color: #027A48; }
.priority-chip-2 { background: #FFFBEB; color: #92400E; }
.priority-chip-3 { background: #FFF7ED; color: #C2410C; }
.priority-chip-4 { background: #FFF1F2; color: #BE123C; }

.agent-chip, .date-chip, .time-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 3px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

/* Sections */
.task-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 22px;
  margin-bottom: 16px;
}

.section-label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-muted);
  margin-bottom: 14px;
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
  line-height: 1.7;
  color: var(--text);
  white-space: pre-wrap;
}

/* Comments */
.comment-input-wrap {
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 20px;
  transition: border-color 0.15s;
}

.comment-input-wrap:focus-within {
  border-color: var(--primary);
}

.comment-textarea {
  width: 100%;
  padding: 12px 14px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  color: var(--text);
  display: block;
}

.comment-textarea:focus { outline: none; }
.comment-textarea::placeholder { color: var(--text-light); }

.comment-input-footer {
  padding: 10px 12px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border);
  background: var(--surface);
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
  gap: 10px;
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
  background: var(--primary);
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
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.comment-author {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

.comment-date {
  font-size: 11.5px;
  color: var(--text-light);
}

.comment-text {
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--text);
}

.comment-delete {
  flex-shrink: 0;
  align-self: flex-start;
  margin-top: 4px;
}
</style>
