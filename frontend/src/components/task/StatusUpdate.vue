<template>
  <div class="status-update">
    <h3>Update Status</h3>
    <div class="status-buttons">
      <button
        v-for="s in statuses"
        :key="s.value"
        class="btn btn-sm"
        :class="{ 'btn-primary': task.status === s.value }"
        :disabled="updating || task.status === s.value"
        @click="updateStatus(s.value)"
      >
        {{ s.label }}
      </button>
    </div>
    <p v-if="updating" class="updating-msg">Updating…</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Task, TaskStatus } from '../../types'
import { patch } from '../../stores/client'

const props = defineProps<{
  task: Task
}>()

const emit = defineEmits<{
  updated: []
}>()

const updating = ref(false)

const statuses: { value: TaskStatus; label: string }[] = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'review', label: 'Review' },
  { value: 'blocked', label: 'Blocked' },
  { value: 'completed', label: 'Completed' },
]

async function updateStatus(status: TaskStatus) {
  updating.value = true
  try {
    await patch(`/tasks/${props.task.id}`, { status })
    emit('updated')
  } catch (e) {
    console.error(e)
  } finally {
    updating.value = false
  }
}
</script>

<style scoped>
.status-update {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 24px;
}

.status-update h3 {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.updating-msg {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 8px;
}

.status-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
