<template>
  <div class="task-card" draggable="true" @dragstart="onDragStart" @click="$router.push(`/tasks/${task.id}`)">
    <div class="task-card-header">
      <span class="priority-indicator" :class="`priority-${task.priority}`"></span>
      <span v-if="task.assigned_agent" class="task-agent">{{ task.assigned_agent }}</span>
    </div>
    <p class="task-card-title">{{ task.title }}</p>
    <div class="task-card-footer">
      <span v-if="task.due_date" class="date">{{ formatDate(task.due_date) }}</span>
      <span v-if="task.estimated_hours" class="hours">{{ task.estimated_hours }}h</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Task } from '../../types'

const props = defineProps<{
  task: Task
}>()

const emit = defineEmits<{
  dragstart: [id: number]
}>()

function formatDate(d: string) {
  return new Date(d).toLocaleDateString()
}

function onDragStart() {
  emit('dragstart', props.task.id)
}
</script>
