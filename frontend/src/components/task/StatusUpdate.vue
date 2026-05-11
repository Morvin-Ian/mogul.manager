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
    <p v-if="updating" class="form-error">Updating...</p>
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
