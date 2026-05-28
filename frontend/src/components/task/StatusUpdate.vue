<template>
  <div class="status-update">
    <h3>Update Status</h3>

    <div v-if="allowedStatuses.length === 0" class="status-locked">
      <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
        <rect x="4" y="7" width="8" height="7" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
        <path d="M6 7V5a2 2 0 014 0v2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
      </svg>
      Status changes for this task are managed by the project admin or owner.
    </div>

    <div v-else>
      <div class="current-status-row">
        <span class="current-label">Current:</span>
        <span class="badge" :class="`badge-${task.status}`">{{ statusLabel(task.status) }}</span>
      </div>
      <div class="status-buttons">
        <button
          v-for="s in allowedStatuses"
          :key="s.value"
          class="btn btn-sm"
          :class="{ 'btn-primary': task.status === s.value }"
          :disabled="updating || task.status === s.value"
          @click="updateStatus(s.value)"
        >
          {{ s.label }}
        </button>
      </div>
      <p v-if="isMemberView" class="member-hint">
        As an assignee you can move this task forward. Blocked/Done transitions require an admin.
      </p>
    </div>

    <p v-if="updating" class="updating-msg">Updating…</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Task, TaskStatus } from '../../types'
import { patch } from '../../stores/client'

const props = defineProps<{
  task: Task
  userRole?: string | null
  assignedToId?: number | null
  currentUserId?: number | null
}>()

const emit = defineEmits<{ updated: [] }>()

const updating = ref(false)

const MEMBER_ALLOWED: Record<string, TaskStatus[]> = {
  todo: ['in_progress'],
  in_progress: ['review'],
}

const allStatuses: { value: TaskStatus; label: string }[] = [
  { value: 'todo',        label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'review',      label: 'Review' },
  { value: 'blocked',     label: 'Blocked' },
  { value: 'completed',   label: 'Completed' },
]

function statusLabel(s: TaskStatus) {
  return allStatuses.find((x) => x.value === s)?.label ?? s
}

const isAdminOrOwner = computed(
  () => props.userRole === 'admin' || props.userRole === 'owner'
)

const isMyTask = computed(
  () => props.assignedToId != null && props.assignedToId === props.currentUserId
)

const isMemberView = computed(
  () => !!props.userRole && !isAdminOrOwner.value
)

const allowedStatuses = computed(() => {
  // No role context provided → show all (backwards compatible / solo workspace)
  if (!props.userRole) return allStatuses

  if (isAdminOrOwner.value) return allStatuses

  // Regular member
  if (!isMyTask.value) return []

  // Member can only advance along the allowed path
  const nextKeys = MEMBER_ALLOWED[props.task.status] ?? []
  return allStatuses.filter(
    (s) => s.value === props.task.status || nextKeys.includes(s.value)
  )
})

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
  margin-bottom: 0;
}

.status-update h3 {
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.7px;
  color: var(--text-light);
  margin-bottom: 14px;
}

.status-locked {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  padding: 11px 14px;
}

.current-status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.current-label {
  font-size: 12px;
  color: var(--text-light);
  font-weight: 500;
}

.badge {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
}

.badge-todo        { background: #F0F2F5; color: #374151; }
.badge-in_progress { background: #DBEAFE; color: #1E40AF; }
.badge-review      { background: #FEF3C7; color: #92400E; }
.badge-blocked     { background: #FEE2E2; color: #B91C1C; }
.badge-completed   { background: #D1FAE5; color: #065F46; }

.updating-msg {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 10px;
  font-style: italic;
}

.status-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.member-hint {
  margin-top: 10px;
  font-size: 11.5px;
  color: var(--text-light);
  font-style: italic;
  line-height: 1.5;
}
</style>
