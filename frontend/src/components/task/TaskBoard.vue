<template>
  <div class="task-board">
    <div class="section-header">
      <h2>Board</h2>
      <button class="btn btn-sm btn-primary" @click="showModal = true">
        <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        New Task
      </button>
    </div>

    <div v-if="dropError" class="drop-error">
      <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
        <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.4"/>
        <path d="M8 5v4M8 11v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
      </svg>
      {{ dropError }}
    </div>

    <SkeletonBoard v-if="loading" />
    <div v-else class="board-columns">
      <div
        v-for="col in columns"
        :key="col.key"
        class="board-column"
        :class="[`col-${col.key}`, { 'col-drop-target': draggedId && canDropToCol(col.key), 'col-drop-blocked': draggedId && !canDropToCol(col.key) }]"
        @dragover.prevent
        @drop="onDrop(col.key)"
      >
        <div class="column-header">
          <div class="column-header-left">
            <span class="col-dot"></span>
            <h3>{{ col.label }}</h3>
          </div>
          <span class="count">{{ grouped[col.key]?.length || 0 }}</span>
        </div>
        <div class="column-body">
          <TaskCard
            v-for="task in grouped[col.key]"
            :key="task.id"
            :task="task"
            :can-drag="canDragTask(task)"
            @dragstart="onDragStart"
          />
          <div v-if="!grouped[col.key]?.length" class="empty-col">
            <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
              <path d="M10 5v10M5 10h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>Drop tasks here</span>
          </div>
        </div>
      </div>
    </div>
    <TaskModal
      v-if="showModal"
      :project-id="projectId"
      @close="showModal = false"
      @saved="onTaskCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useTaskStore } from '../../stores/tasks'
import { useMembersStore } from '../../stores/members'
import { useAuthStore } from '../../stores/auth'
import type { Task, TaskStatus } from '../../types'
import { patch } from '../../stores/client'
import TaskCard from './TaskCard.vue'
import TaskModal from './TaskModal.vue'
import SkeletonBoard from '../common/SkeletonBoard.vue'

const props = defineProps<{ projectId: number; workspaceId?: number }>()

const taskStore = useTaskStore()
const membersStore = useMembersStore()
const auth = useAuthStore()

const showModal = ref(false)
const loading = ref(false)
const draggedId = ref<number | null>(null)
const dropError = ref<string | null>(null)

// Member-allowed forward transitions
const MEMBER_ALLOWED: Record<string, Set<TaskStatus>> = {
  todo: new Set(['in_progress']),
  in_progress: new Set(['review']),
}

interface Column { key: TaskStatus; label: string }

const columns: Column[] = [
  { key: 'todo',        label: 'To Do' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'review',      label: 'Review' },
  { key: 'blocked',     label: 'Blocked' },
  { key: 'completed',   label: 'Done' },
]

const grouped = computed(() => {
  const map: Record<string, Task[]> = {}
  for (const col of columns) {
    map[col.key] = taskStore.tasks.filter((t) => t.status === col.key)
  }
  return map
})

const myRole = computed(() => membersStore.myMembership?.role ?? null)
const isAdminOrOwner = computed(() => myRole.value === 'admin' || myRole.value === 'owner')

async function loadTasks() {
  loading.value = true
  await taskStore.fetchByProject(props.projectId)
  loading.value = false
}

onMounted(async () => {
  await loadTasks()
  if (props.workspaceId) {
    await membersStore.fetchMyMembership(props.workspaceId)
  }
})

watch(() => props.projectId, loadTasks)
watch(() => props.workspaceId, async (id) => {
  if (id) await membersStore.fetchMyMembership(id)
})

function canDragTask(task: Task): boolean {
  if (isAdminOrOwner.value) return true
  return task.assigned_to_id === auth.user?.id
}

function canDropToCol(toStatus: TaskStatus): boolean {
  if (!draggedId.value) return false
  if (isAdminOrOwner.value) return true
  const task = taskStore.tasks.find((t) => t.id === draggedId.value)
  if (!task) return false
  if (task.assigned_to_id !== auth.user?.id) return false
  return MEMBER_ALLOWED[task.status]?.has(toStatus) ?? false
}

function onDragStart(id: number) {
  draggedId.value = id
  dropError.value = null
}

function showDropError(msg: string) {
  dropError.value = msg
  setTimeout(() => { dropError.value = null }, 3500)
}

async function onDrop(toStatus: TaskStatus) {
  if (!draggedId.value) return

  const task = taskStore.tasks.find((t) => t.id === draggedId.value)
  if (!task) { draggedId.value = null; return }

  // Same column — nothing to do
  if (task.status === toStatus) { draggedId.value = null; return }

  if (!isAdminOrOwner.value) {
    if (task.assigned_to_id !== auth.user?.id) {
      showDropError('You can only move tasks assigned to you.')
      draggedId.value = null
      return
    }
    const allowed = MEMBER_ALLOWED[task.status]
    if (!allowed?.has(toStatus)) {
      showDropError('You can only move: To Do → In Progress → Review.')
      draggedId.value = null
      return
    }
  }

  try {
    await patch(`/tasks/${draggedId.value}`, { status: toStatus })
    await taskStore.fetchByProject(props.projectId)
  } catch (e) {
    console.error(e)
  }
  draggedId.value = null
}

async function onTaskCreated(data: Record<string, any>) {
  await taskStore.create(data as any)
  showModal.value = false
}
</script>

<style scoped>
.task-board { padding: 0; }

.drop-error {
  display: flex;
  align-items: center;
  gap: 7px;
  background: #FFF1F2;
  border: 1.5px solid #FECDD3;
  color: #BE123C;
  border-radius: 8px;
  padding: 9px 14px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 12px;
}

:global([data-theme="dark"]) .drop-error {
  background: rgba(190, 18, 60, 0.15);
  border-color: rgba(254, 205, 211, 0.3);
  color: #FDA4AF;
}

.board-columns {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 16px;
  align-items: flex-start;
}

.board-column {
  flex: 0 0 268px;
  background: #F0F2F5;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 280px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.col-drop-target {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 2px var(--primary-muted), inset 0 1px 0 rgba(255,255,255,0.6) !important;
}

.col-drop-blocked {
  opacity: 0.5;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 11px 12px 10px;
  border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,0.7);
  border-radius: var(--radius) var(--radius) 0 0;
  backdrop-filter: blur(4px);
}

.column-header-left {
  display: flex;
  align-items: center;
  gap: 7px;
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.col-todo        .col-dot { background: #94A3B8; box-shadow: 0 0 0 2px #E2E8F0; }
.col-in_progress .col-dot { background: #0052FF; box-shadow: 0 0 0 2px #DBEAFE; }
.col-review      .col-dot { background: #F59E0B; box-shadow: 0 0 0 2px #FEF3C7; }
.col-blocked     .col-dot { background: #EF4444; box-shadow: 0 0 0 2px #FEE2E2; }
.col-completed   .col-dot { background: #10B981; box-shadow: 0 0 0 2px #D1FAE5; }

.column-header h3 {
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.4px;
  text-transform: uppercase;
}

.col-todo        .column-header h3 { color: #64748B; }
.col-in_progress .column-header h3 { color: #1D4ED8; }
.col-review      .column-header h3 { color: #92400E; }
.col-blocked     .column-header h3 { color: #B91C1C; }
.col-completed   .column-header h3 { color: #065F46; }

.count {
  background: rgba(255,255,255,0.9);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
  min-width: 22px;
  text-align: center;
  line-height: 1.7;
}

.column-body {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  flex: 1;
  min-height: 80px;
}

.empty-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 28px 0;
  color: var(--text-light);
  opacity: 0.6;
}

.empty-col span {
  font-size: 11.5px;
}
</style>
