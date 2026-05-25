<template>
  <div
    class="task-card"
    :class="`priority-border-${task.priority}`"
    draggable="true"
    @dragstart="onDragStart"
    @click="$router.push(`/tasks/${task.id}`)"
  >
    <div class="task-header">
      <p class="task-title">{{ task.title }}</p>
      <span class="priority-dot" :class="`pdot-${task.priority}`" :title="priorityLabel + ' priority'"></span>
    </div>
    <div class="task-meta">
      <span class="priority-pill" :class="`priority-${task.priority}`">{{ priorityLabel }}</span>
      <span v-if="task.assignee_name" class="assignee-tag">
        <svg viewBox="0 0 10 10" fill="none" width="9" height="9">
          <circle cx="5" cy="3.5" r="2" stroke="currentColor" stroke-width="1.1"/>
          <path d="M1.5 9c0-1.93 1.57-3.5 3.5-3.5S8.5 7.07 8.5 9" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>
        </svg>
        {{ task.assignee_name }}
      </span>
      <span v-else-if="task.assigned_agent" class="agent-tag">
        <svg viewBox="0 0 10 10" fill="none" width="9" height="9">
          <circle cx="5" cy="3.5" r="2" stroke="currentColor" stroke-width="1.1"/>
          <path d="M1.5 9c0-1.93 1.57-3.5 3.5-3.5S8.5 7.07 8.5 9" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/>
        </svg>
        {{ task.assigned_agent }}
      </span>
    </div>
    <div v-if="task.due_date || task.estimated_hours" class="task-footer">
      <span v-if="task.due_date" class="due-chip">
        <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
          <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        {{ formatDate(task.due_date) }}
      </span>
      <span v-if="task.estimated_hours" class="hours-chip">
        <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
          <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M6 3.5V6l1.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ task.estimated_hours }}h
      </span>
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
  border-left: 4px solid transparent;
  border-radius: 10px;
  padding: 13px 13px 11px;
  cursor: grab;
  transition: box-shadow 0.18s ease, transform 0.18s ease, border-color 0.15s;
  user-select: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 1px 3px rgba(10,11,13,0.05), 0 0 0 0.5px rgba(10,11,13,0.03);
}

.task-card:hover {
  box-shadow: 0 6px 20px rgba(10,11,13,0.11), 0 2px 6px rgba(10,11,13,0.07);
  transform: translateY(-2px);
  border-color: var(--border-strong);
}

.task-card:active {
  cursor: grabbing;
  transform: translateY(-1px) scale(0.99);
  box-shadow: 0 3px 10px rgba(10,11,13,0.09);
}

/* ── Header row ── */
.task-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.task-title {
  flex: 1;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.45;
  letter-spacing: -0.2px;
}

/* Small colored dot top-right matching priority */
.priority-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}
.pdot-1 { background: #10B981; box-shadow: 0 0 0 2px #D1FAE5; }
.pdot-2 { background: #F59E0B; box-shadow: 0 0 0 2px #FEF3C7; }
.pdot-3 { background: #F97316; box-shadow: 0 0 0 2px #FFEDD5; }
.pdot-4 { background: #EF4444; box-shadow: 0 0 0 2px #FEE2E2; }

/* ── Meta row ── */
.task-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}

.priority-pill {
  display: inline-flex;
  align-items: center;
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: var(--radius-full);
  border: 1px solid transparent;
  letter-spacing: 0.1px;
}

.priority-1 { background: #ECFDF5; color: #065F46; border-color: #6EE7B7; }
.priority-2 { background: #FFFBEB; color: #78350F; border-color: #FCD34D; }
.priority-3 { background: #FFF7ED; color: #9A3412; border-color: #FDBA74; }
.priority-4 { background: #FFF1F2; color: #9F1239; border-color: #FCA5A5; }

.assignee-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10.5px;
  font-weight: 600;
  color: var(--primary);
  background: var(--primary-light);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid var(--primary-border);
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 120px;
  white-space: nowrap;
}

.agent-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10.5px;
  font-weight: 500;
  color: var(--text-muted);
  background: var(--bg);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 120px;
  white-space: nowrap;
}

/* ── Footer row ── */
.task-footer {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 1px;
}

.due-chip, .hours-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
  background: var(--bg);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
}

/* ── Priority accent border ── */
.priority-border-1 { border-left-color: #10B981; }
.priority-border-2 { border-left-color: #F59E0B; }
.priority-border-3 { border-left-color: #F97316; }
.priority-border-4 { border-left-color: #EF4444; }
</style>
