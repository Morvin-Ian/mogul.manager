<template>
  <div class="task-detail">
    <div v-if="taskStore.loading" class="loading">Loading...</div>

    <template v-if="task">
      <div class="page-head">
        <div>
          <h2>{{ task.title }}</h2>
        </div>
        <div class="page-actions">
          <button class="btn btn-sm" @click="editTask">Edit</button>
          <button class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
      </div>

      <div class="task-meta">
        <div class="meta-row">
          <span class="badge" :class="`badge-${task.status}`">{{ task.status }}</span>
          <span class="priority-badge" :class="`priority-${task.priority}`">{{ priorityLabel }}</span>
          <span v-if="task.assigned_agent">Agent: {{ task.assigned_agent }}</span>
        </div>
        <div class="meta-row">
          <span v-if="task.due_date">Due: {{ formatDate(task.due_date) }}</span>
          <span v-if="task.estimated_hours">Est: {{ task.estimated_hours }}h</span>
          <span v-if="task.actual_hours">Actual: {{ task.actual_hours }}h</span>
          <span v-if="task.completed_at">Completed: {{ formatDate(task.completed_at) }}</span>
        </div>
      </div>

      <div class="task-description" v-if="task.description">
        <h3>Description</h3>
        <p>{{ task.description }}</p>
      </div>

      <StatusUpdate :task="task" @updated="onStatusUpdated" />

      <div class="task-comments">
        <h3>Comments</h3>
        <div class="comment-form">
          <textarea v-model="newComment" rows="2" placeholder="Add a comment..."></textarea>
          <button class="btn btn-primary btn-sm" @click="addComment" :disabled="!newComment.trim()">
            Post
          </button>
        </div>
        <div v-if="comments.length === 0" class="empty">No comments yet.</div>
        <div v-for="comment in comments" :key="comment.id" class="comment">
          <div class="comment-body">
            <p>{{ comment.content }}</p>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
          </div>
          <button v-if="comment.user_id === auth.user?.id" class="btn btn-sm btn-danger" @click="handleDeleteComment(comment.id)">
            Delete
          </button>
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
  return new Date(d).toLocaleDateString()
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
