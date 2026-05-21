<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ task ? 'Edit Task' : 'New Task' }}</h2>
        <button type="button" class="modal-close" @click="$emit('close')">
          <svg viewBox="0 0 16 16" fill="none" width="16" height="16"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </button>
      </div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="t-title">Title</label>
          <input id="t-title" v-model="form.title" required maxlength="255" />
        </div>
        <div class="form-group">
          <label for="t-desc">Description</label>
          <textarea id="t-desc" v-model="form.description" rows="3"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="t-status">Status</label>
            <select id="t-status" v-model="form.status">
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="review">Review</option>
              <option value="blocked">Blocked</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="form-group">
            <label for="t-priority">Priority</label>
            <select id="t-priority" v-model.number="form.priority">
              <option :value="1">Low</option>
              <option :value="2">Medium</option>
              <option :value="3">High</option>
              <option :value="4">Urgent</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="t-agent">Assigned Agent</label>
            <input id="t-agent" v-model="form.assigned_agent" placeholder="agent name" />
          </div>
          <div class="form-group">
            <label for="t-est">Est. Hours</label>
            <input id="t-est" v-model.number="form.estimated_hours" type="number" min="0" />
          </div>
        </div>
        <div class="form-group">
          <label for="t-due">Due Date</label>
          <input id="t-due" v-model="form.due_date" type="date" />
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <div class="form-actions">
          <button type="button" class="btn" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : task ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { Task, TaskPriority, TaskStatus } from '../../types'

const props = defineProps<{
  task?: Task | null
  projectId?: number | null
}>()

const emit = defineEmits<{
  close: []
  saved: [data: Record<string, any>]
}>()

interface TaskForm {
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority | number
  assigned_agent: string
  estimated_hours: number | null
  due_date: string
}

const form = reactive<TaskForm>({
  title: '',
  description: '',
  status: 'todo',
  priority: 2,
  assigned_agent: '',
  estimated_hours: null,
  due_date: '',
})
const saving = ref(false)
const error = ref<string | null>(null)

watch(() => props.task, (t) => {
  if (t) {
    form.title = t.title
    form.description = t.description || ''
    form.status = t.status
    form.priority = t.priority
    form.assigned_agent = t.assigned_agent || ''
    form.estimated_hours = t.estimated_hours
    form.due_date = t.due_date ? t.due_date.slice(0, 10) : ''
  } else {
    form.title = ''
    form.description = ''
    form.status = 'todo'
    form.priority = 2
    form.assigned_agent = ''
    form.estimated_hours = null
    form.due_date = ''
  }
}, { immediate: true })

async function handleSubmit() {
  saving.value = true
  error.value = null
  const payload: Record<string, any> = { ...form }
  if (!payload.due_date) delete payload.due_date
  if (!payload.estimated_hours) delete payload.estimated_hours
  if (!payload.assigned_agent) delete payload.assigned_agent
  if (props.projectId && !props.task) {
    payload.project_id = props.projectId
  }
  emit('saved', payload)
  saving.value = false
}
</script>
