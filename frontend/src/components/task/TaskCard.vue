<template>
  <div
    class="task-card"
    :class="`priority-border-${task.priority}`"
    draggable="true"
    @dragstart="onDragStart"
    @click="$router.push(`/tasks/${task.id}`)"
  >
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

const props = defineProps<{ task: Task }>()
const emit = defineEmits<{ dragstart: [id: number] }>()

function formatDate(d: string) {
  return new Date(d).toLocaleDateString()
}

function onDragStart() {
  emit('dragstart', props.task.id)
}
</script>

<style scoped>
.task-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid transparent;
  border-radius: var(--radius-sm);
  padding: 11px 12px;
  cursor: pointer;
  transition: box-shadow 0.12s, transform 0.12s, border-color 0.12s;
  user-select: none;
}

.task-card:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
  border-color: var(--border-strong);
}

.task-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.task-card-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  line-height: 1.4;
  margin-bottom: 8px;
}

.task-card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.priority-indicator {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
}

.task-agent {
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg);
  padding: 2px 7px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 120px;
  white-space: nowrap;
}

.hours {
  font-size: 11px;
  color: var(--text-light);
}

/* Priority indicator dot colors */
.priority-1, .priority-low      { background: #86efac; }
.priority-2, .priority-medium   { background: #fbbf24; }
.priority-3, .priority-high     { background: #f97316; }
.priority-4, .priority-urgent   { background: #ef4444; animation: pulse 1.4s ease-in-out infinite; }

/* Priority left-border colors */
.priority-border-1,
.priority-border-low    { border-left-color: #86efac; }
.priority-border-2,
.priority-border-medium { border-left-color: #fbbf24; }
.priority-border-3,
.priority-border-high   { border-left-color: #f97316; }
.priority-border-4,
.priority-border-urgent { border-left-color: #ef4444; }

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.6; transform: scale(1.25); }
}
</style>
