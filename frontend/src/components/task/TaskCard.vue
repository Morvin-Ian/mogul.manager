<template>
  <div
    class="task-card"
    :class="`priority-border-${task.priority}`"
    draggable="true"
    @dragstart="onDragStart"
    @click="$router.push(`/tasks/${task.id}`)"
  >
    <p class="task-title">{{ task.title }}</p>
    <div class="task-meta">
      <span class="priority-pill" :class="`priority-${task.priority}`">{{ priorityLabel }}</span>
      <span v-if="task.assigned_agent" class="agent-tag">{{ task.assigned_agent }}</span>
    </div>
    <div v-if="task.due_date || task.estimated_hours" class="task-footer">
      <span v-if="task.due_date" class="due-chip">
        <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
          <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        {{ formatDate(task.due_date) }}
      </span>
      <span v-if="task.estimated_hours" class="hours-chip">{{ task.estimated_hours }}h</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '../../types'

const props = defineProps<{ task: Task }>()
const emit = defineEmits<{ dragstart: [id: number] }>()

const priorityLabel = computed(() => {
  const labels: Record<number, string> = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' }
  return labels[props.task.priority] || ''
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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
  padding: 12px 14px;
  cursor: pointer;
  transition: box-shadow 0.15s ease, transform 0.15s ease;
  user-select: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-card:hover {
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.task-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  line-height: 1.45;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.priority-pill {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.priority-1 { background: #E6F9F1; color: #027A48; }
.priority-2 { background: #FFFBEB; color: #92400E; }
.priority-3 { background: #FFF7ED; color: #C2410C; }
.priority-4 { background: #FFF1F2; color: #BE123C; }

.agent-tag {
  font-size: 10.5px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 110px;
  white-space: nowrap;
}

.task-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-top: 4px;
  border-top: 1px solid var(--border);
}

.due-chip, .hours-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-light);
  font-weight: 500;
}

/* Priority left-border colors */
.priority-border-1 { border-left-color: #10B981; }
.priority-border-2 { border-left-color: #F59E0B; }
.priority-border-3 { border-left-color: #F97316; }
.priority-border-4 { border-left-color: #EF4444; }
</style>
