<template>
  <div
    class="task-card"
    :class="{ 'task-card--no-drag': !canDrag }"
    :draggable="canDrag !== false"
    @dragstart="canDrag !== false ? onDragStart() : undefined"
    @click="emit('select', task)"
  >
    <!-- Top row: priority badge + est. hours -->
    <div class="card-top-row">
      <span class="priority-badge" :class="`pb-${task.priority}`">{{ priorityLabel }}</span>
      <span v-if="task.estimated_hours" class="est-hours">
        <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
          <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M6 3.5V6l1.5 1.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        {{ task.estimated_hours }}h
      </span>
    </div>

    <!-- Title -->
    <p class="task-title">{{ task.title }}</p>

    <!-- Description snippet -->
    <p v-if="task.description" class="card-desc">{{ task.description }}</p>

    <div class="card-divider" />

    <!-- Footer: comments + date + avatars -->
    <div class="card-footer">
      <div class="card-footer-left">
        <span class="comment-count">
          <font-awesome-icon :icon="['far', 'comment']" />
          0
        </span>
        <span v-if="task.due_date" class="card-due">
          <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
            <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          {{ formatDate(task.due_date) }}
        </span>
      </div>
      <div v-if="task.assignee_name" class="avatar-stack">
        <div class="avatar-chip" :style="{ background: gradient(task.assignee_name) }">
          {{ task.assignee_name.charAt(0).toUpperCase() }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '../../types'

const props = defineProps<{ task: Task; canDrag?: boolean }>()
const emit = defineEmits<{
  dragstart: [id: string]
  select: [task: Task]
}>()

const priorityLabel = computed(() => {
  const labels: Record<number, string> = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' }
  return labels[props.task.priority] || ''
})

const GRADIENTS = [
  'linear-gradient(135deg,#6366F1,#8B5CF6)',
  'linear-gradient(135deg,#0EA5E9,#2563EB)',
  'linear-gradient(135deg,#10B981,#059669)',
  'linear-gradient(135deg,#F59E0B,#D97706)',
  'linear-gradient(135deg,#EF4444,#DC2626)',
  'linear-gradient(135deg,#EC4899,#DB2777)',
]
function gradient(name: string): string {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) & 0xffffffff
  return GRADIENTS[Math.abs(h) % GRADIENTS.length]
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function onDragStart() {
  if (props.canDrag === false) return
  emit('dragstart', props.task.uuid)
}
</script>

<style scoped>
.task-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px 12px;
  cursor: grab;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  transition: box-shadow 0.16s, transform 0.16s;
  user-select: none;
}
.task-card--no-drag { cursor: pointer; }
.task-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.1), 0 1px 4px rgba(0,0,0,0.06);
  transform: translateY(-1px);
}
.task-card:active {
  cursor: grabbing;
  transform: translateY(0) scale(0.99);
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* Top row: priority + est hours */
.card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

/* Priority badge */
.priority-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.1px;
  flex-shrink: 0;
}
.pb-1 { background: #DCFCE7; color: #16A34A; }
.pb-2 { background: #FEF3C7; color: #D97706; }
.pb-3 { background: #FEE2E2; color: #DC2626; }
.pb-4 { background: #FEE2E2; color: #991B1B; }

/* Estimated hours */
.est-hours {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-light);
  flex-shrink: 0;
}

/* Title */
.task-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.5;
  letter-spacing: -0.1px;
}

/* Description snippet */
.card-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Divider */
.card-divider {
  height: 1px;
  background: var(--border);
  margin: 2px 0;
  opacity: 0.6;
}

/* Footer */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.card-footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.comment-count {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--text-light);
  font-weight: 500;
  flex-shrink: 0;
}

.card-due {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-light);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.avatar-stack {
  display: flex;
  flex-direction: row-reverse;
  flex-shrink: 0;
}

.avatar-chip {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 800;
  border: 2px solid var(--card-bg);
  margin-left: -6px;
  flex-shrink: 0;
}
.avatar-chip:last-child { margin-left: 0; }

/* ── Dark mode ── */
:global([data-theme="dark"]) .task-card {
  background: #1A2D42;
  border-color: rgba(91, 155, 255, 0.20);
  box-shadow: 0 2px 10px rgba(0,0,0,0.5), 0 1px 4px rgba(0,0,0,0.3),
              inset 0 1px 0 rgba(255,255,255,0.06);
}
:global([data-theme="dark"]) .task-card:hover {
  background: #234060;
  border-color: rgba(91, 155, 255, 0.32);
  box-shadow: 0 6px 20px rgba(0,0,0,0.55), 0 2px 8px rgba(0,0,0,0.4),
              inset 0 1px 0 rgba(255,255,255,0.08);
}
:global([data-theme="dark"]) .task-card:active {
  box-shadow: 0 1px 4px rgba(0,0,0,0.45);
}
:global([data-theme="dark"]) .task-title   { color: #CBE0F5; }
:global([data-theme="dark"]) .card-desc    { color: #7A99B8; }
:global([data-theme="dark"]) .comment-count { color: #8BAFC8; }
:global([data-theme="dark"]) .card-due     { color: #8BAFC8; }
:global([data-theme="dark"]) .est-hours    { color: #8BAFC8; }
:global([data-theme="dark"]) .card-divider { background: rgba(91,155,255,0.12); }
:global([data-theme="dark"]) .avatar-chip  { border-color: #1A2D42; }

:global([data-theme="dark"]) .pb-1 { background: rgba(22,163,74,0.22);  color: #4ADE80; }
:global([data-theme="dark"]) .pb-2 { background: rgba(217,119,6,0.22);  color: #FBB040; }
:global([data-theme="dark"]) .pb-3 { background: rgba(220,38,38,0.22);  color: #F87171; }
:global([data-theme="dark"]) .pb-4 { background: rgba(153,27,27,0.22);  color: #FCA5A5; }
</style>
