<template>
  <div
    class="task-card"
    :class="{ 'task-card--no-drag': !canDrag }"
    :draggable="canDrag !== false"
    @dragstart="canDrag !== false ? onDragStart() : undefined"
    @click="emit('select', task)"
  >
    <!-- Priority badge -->
    <span class="priority-badge" :class="`pb-${task.priority}`">{{ priorityLabel }}</span>

    <!-- Title -->
    <p class="task-title">{{ task.title }}</p>

    <!-- Footer row 1: comments + avatars -->
    <div class="card-row">
      <span class="comment-count">
        <font-awesome-icon :icon="['far', 'comment']" />
        0
      </span>
      <div v-if="task.assignee_name" class="avatar-stack">
        <div class="avatar-chip" :style="{ background: gradient(task.assignee_name) }">
          {{ task.assignee_name.charAt(0).toUpperCase() }}
        </div>
      </div>
    </div>

    <!-- Footer row 2: date range -->
    <div v-if="task.due_date" class="card-dates">
      {{ formatDate(task.created_at) }} → {{ formatDate(task.due_date) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '../../types'

const props = defineProps<{ task: Task; canDrag?: boolean }>()
const emit = defineEmits<{
  dragstart: [id: number]
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
  emit('dragstart', props.task.id)
}
</script>

<style scoped>
.task-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.07);
  border-radius: 8px;
  padding: 14px 16px 12px;
  cursor: grab;
  display: flex;
  flex-direction: column;
  gap: 9px;
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

/* Priority badge */
.priority-badge {
  display: inline-block;
  align-self: flex-start;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 4px;
  letter-spacing: 0.1px;
}
.pb-1 { background: #DCFCE7; color: #16A34A; }
.pb-2 { background: #FEF3C7; color: #D97706; }
.pb-3 { background: #FEE2E2; color: #DC2626; }
.pb-4 { background: #FEE2E2; color: #991B1B; }

/* Title */
.task-title {
  font-size: 13.5px;
  font-weight: 500;
  color: #111827;
  line-height: 1.55;
  letter-spacing: -0.1px;
}

/* Footer row 1 */
.card-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.comment-count {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  color: #9CA3AF;
  font-weight: 500;
}

.avatar-stack {
  display: flex;
  flex-direction: row-reverse;
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
  border: 2px solid #fff;
  margin-left: -6px;
  flex-shrink: 0;
}
.avatar-chip:last-child { margin-left: 0; }

/* Footer row 2: date */
.card-dates {
  font-size: 11.5px;
  color: #9CA3AF;
  font-weight: 500;
}

/* ── Dark mode ── */
:global([data-theme="dark"]) .task-card {
  background: #253341;
  border-color: rgba(255,255,255,0.07);
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
:global([data-theme="dark"]) .task-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
:global([data-theme="dark"]) .task-title { color: #F7F9F9; }
:global([data-theme="dark"]) .avatar-chip { border-color: #253341; }

:global([data-theme="dark"]) .pb-1 { background: rgba(22,163,74,0.2); color: #4ADE80; }
:global([data-theme="dark"]) .pb-2 { background: rgba(217,119,6,0.2); color: #FBB040; }
:global([data-theme="dark"]) .pb-3 { background: rgba(220,38,38,0.2); color: #F87171; }
:global([data-theme="dark"]) .pb-4 { background: rgba(153,27,27,0.2); color: #FCA5A5; }
</style>
