<template>
  <div
    class="task-card"
    :class="{ 'task-card--no-drag': !canDrag }"
    :data-task-uuid="task.uuid"
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

    <div v-if="task.tags?.length" class="card-tags">
      <TagChip v-for="t in task.tags" :key="t.id" :tag="t" />
    </div>

    <div class="card-divider" />

    <!-- Footer: comments + date + avatars -->
    <div class="card-footer">
      <div class="card-footer-left">
        <span class="comment-count">
          <font-awesome-icon :icon="['far', 'comment']" />
          {{ task.comment_count ?? 0 }}
        </span>
        <span v-if="task.due_date" class="card-due">
          <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
            <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
            <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          {{ formatDate(task.due_date) }}
        </span>
      </div>
      <template v-if="isTeam">
        <div v-if="task.assignee_name" class="assignee-pill" :class="{ 'assignee-pill--me': isMe }">
          <div
            class="avatar-chip"
            :style="task.assignee_avatar_url ? {} : { background: gradient(task.assignee_name) }"
          >
            <img
              v-if="task.assignee_avatar_url"
              :src="task.assignee_avatar_url"
              :alt="task.assignee_name"
              class="avatar-img"
            />
            <span v-else>{{ isMe ? 'Me' : initials(task.assignee_name) }}</span>
          </div>
          <span class="assignee-name">{{ isMe ? 'You' : task.assignee_name }}</span>
        </div>
        <div v-else class="assignee-pill assignee-pill--empty">
          <div class="avatar-chip avatar-chip--empty">
            <svg viewBox="0 0 12 12" fill="none" width="9" height="9">
              <circle cx="6" cy="4" r="2" stroke="currentColor" stroke-width="1.2"/>
              <path d="M1.5 10.5c0-2.21 2.015-4 4.5-4s4.5 1.79 4.5 4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
          </div>
          <span class="assignee-name">Unassigned</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '../../types'
import { useAuthStore } from '../../stores/auth'
import TagChip from './TagChip.vue'

const props = defineProps<{ task: Task; canDrag?: boolean; isTeam?: boolean }>()
const auth = useAuthStore()
const isMe = computed(() => props.task.assigned_to_id === auth.user?.id)
const emit = defineEmits<{ select: [task: Task] }>()

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
  'linear-gradient(135deg,#0D9488,#0891B2)',
]
function gradient(name: string): string {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) & 0xffffffff
  return GRADIENTS[Math.abs(h) % GRADIENTS.length]
}

function initials(name: string): string {
  const parts = name.trim().split(/[\s._-]+/).filter(Boolean)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name.slice(0, 2).toUpperCase()
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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
.pb-1 { background: var(--priority-1-bg); color: var(--priority-1-text); }
.pb-2 { background: var(--priority-2-bg); color: var(--priority-2-text); }
.pb-3 { background: var(--priority-3-bg); color: var(--priority-3-text); }
.pb-4 { background: var(--priority-4-bg); color: var(--priority-4-text); }

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

.assignee-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  padding: 2px 8px 2px 3px;
  flex-shrink: 0;
  max-width: 140px;
}

.avatar-chip {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8px;
  font-weight: 800;
  flex-shrink: 0;
  overflow: hidden;
}

.assignee-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.assignee-pill--me {
  background: var(--primary-light);
  border-color: var(--primary-border);
}
.assignee-pill--me .assignee-name { color: var(--primary); }

.assignee-pill--empty {
  opacity: 0.55;
  border-style: dashed;
}

.avatar-chip--empty {
  background: var(--border);
  color: var(--text-light);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

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
:global([data-theme="dark"]) .assignee-pill { background: rgba(255,255,255,0.05); border-color: rgba(91,155,255,0.2); }
:global([data-theme="dark"]) .assignee-name { color: #8BAFC8; }
/* Priority badge dark values come from --priority-* tokens */
</style>
