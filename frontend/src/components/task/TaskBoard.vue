<template>
  <div class="task-board">
    <div class="board-topbar">
      <div class="board-topbar-left">
        <font-awesome-icon :icon="['fas', 'table-columns']" class="board-icon" />
        <span class="board-label">Board</span>
        <span class="board-total">{{ taskStore.tasks.length }}</span>
      </div>
      <button class="new-task-btn" :style="{ background: btnBg, color: btnColor }" @click="showModal = true">
        <font-awesome-icon :icon="['fas', 'plus']" />
        New Task
      </button>
    </div>

    <div v-if="dropError" class="drop-error">
      <font-awesome-icon :icon="['fas', 'circle-exclamation']" />
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
            <span class="count">{{ grouped[col.key]?.length || 0 }}</span>
          </div>
        </div>
        <div class="column-body">
          <TaskCard
            v-for="task in grouped[col.key]"
            :key="task.id"
            :task="task"
            :can-drag="canDragTask(task)"
            @select="selectedTask = $event"
            @dragstart="onDragStart"
          />
        </div>
        <button class="col-add-btn" @click="showModal = true">
          <font-awesome-icon :icon="['fas', 'plus']" />
          New
        </button>
      </div>
    </div>
    <TaskModal
      v-if="showModal"
      :project-id="projectId"
      @close="showModal = false"
      @saved="onTaskCreated"
    />
    <TaskDrawer
      v-if="selectedTask"
      :task="selectedTask"
      :workspace-id="workspaceId ?? null"
      :project-id="projectId"
      @close="selectedTask = null"
      @deleted="selectedTask = null; loadTasks()"
      @updated="onTaskUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useTaskStore } from '../../stores/tasks'
import { useMembersStore } from '../../stores/members'
import { useAuthStore } from '../../stores/auth'
import { useTheme } from '../../composables/useTheme'
import type { Task, TaskStatus } from '../../types'
import { patch } from '../../stores/client'
import TaskCard from './TaskCard.vue'
import TaskModal from './TaskModal.vue'
import TaskDrawer from './TaskDrawer.vue'
import SkeletonBoard from '../common/SkeletonBoard.vue'

const props = defineProps<{ projectId: number; workspaceId?: string }>()

const taskStore = useTaskStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const { isDark } = useTheme()

const btnBg = computed(() => isDark.value ? '#F7F9F9' : '#1c1c1e')
const btnColor = computed(() => isDark.value ? '#15202B' : '#ffffff')

const showModal = ref(false)
const loading = ref(false)
const draggedId = ref<string | null>(null)
const dropError = ref<string | null>(null)
const selectedTask = ref<Task | null>(null)

const MEMBER_ALLOWED: Record<string, Set<TaskStatus>> = {
  todo:        new Set(['in_progress']),
  in_progress: new Set(['review']),
  blocked:     new Set(['todo', 'in_progress', 'review']),
}

interface Column { key: TaskStatus; label: string }

const columns: Column[] = [
  { key: 'todo',        label: 'Pending' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'review',      label: 'Review' },
  { key: 'blocked',     label: 'In Revision' },
  { key: 'completed',   label: 'Completed' },
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
  const task = taskStore.tasks.find((t) => t.uuid === draggedId.value)
  if (!task) return false
  if (task.assigned_to_id !== auth.user?.id) return false
  return MEMBER_ALLOWED[task.status]?.has(toStatus) ?? false
}

function onDragStart(id: string) {
  draggedId.value = id
  dropError.value = null
}

function showDropError(msg: string) {
  dropError.value = msg
  setTimeout(() => { dropError.value = null }, 3500)
}

async function onDrop(toStatus: TaskStatus) {
  if (!draggedId.value) return

  const task = taskStore.tasks.find((t) => t.uuid === draggedId.value)
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
      showDropError('You can only move: Pending → In Progress → Review, or In Revision back to any earlier stage.')
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

function onTaskUpdated(updated: Task) {
  const idx = taskStore.tasks.findIndex((t) => t.id === updated.id)
  if (idx !== -1) taskStore.tasks[idx] = updated
  selectedTask.value = updated
}
</script>

<style scoped>
.task-board { padding: 0; }

/* ── Board topbar ── */
.board-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.board-topbar-left { display: flex; align-items: center; gap: 8px; }
.board-icon { color: var(--text-muted); font-size: 13px; }
.board-label { font-size: 14px; font-weight: 700; color: var(--text); letter-spacing: -0.2px; }
.board-total {
  background: var(--bg);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 999px;
  line-height: 1.7;
}

.new-task-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 18px;
  background: #1c1c1e;
  color: #ffffff;
  border: none;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.15s, transform 0.1s;
  white-space: nowrap;
  flex-shrink: 0;
}
.new-task-btn:hover { opacity: 0.82; }
.new-task-btn:active { transform: scale(0.97); }

/* ── Drop error ── */
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
  background: rgba(190,18,60,0.15);
  border-color: rgba(254,205,211,0.3);
  color: #FDA4AF;
}

/* ── Board columns layout ── */
.board-columns {
  display: flex;
  gap: 14px;
  overflow-x: auto;
  padding-bottom: 20px;
  align-items: flex-start;
}

/* ── Column ── */
.board-column {
  flex: 1 1 0;
  min-width: 240px;
  background: var(--surface);
  border-radius: 10px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 260px);
  transition: border-color 0.15s, box-shadow 0.15s;
  overflow: hidden;
}

.col-drop-target {
  border-color: #3B82F6 !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
.col-drop-blocked { opacity: 0.4; }

/* ── Column header ── */
.column-header {
  padding: 14px 14px 10px;
  flex-shrink: 0;
}
.column-header-left {
  display: flex;
  align-items: center;
  gap: 7px;
}

/* Dot — filled circle, no ring/glow */
.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.col-todo        .col-dot { background: #94A3B8; }
.col-in_progress .col-dot { background: #3B82F6; }
.col-review      .col-dot { background: #F59E0B; }
.col-blocked     .col-dot { background: #EF4444; }
.col-completed   .col-dot { background: #10B981; }

/* Column name — colored to match dot, normal case, semi-bold */
.column-header h3 {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: none;
}
.col-todo        .column-header h3 { color: #64748B; }
.col-in_progress .column-header h3 { color: #3B82F6; }
.col-review      .column-header h3 { color: #F59E0B; }
.col-blocked     .column-header h3 { color: #EF4444; }
.col-completed   .column-header h3 { color: #10B981; }

/* Count — plain gray number, no badge */
.count {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-light);
  line-height: 1;
}

/* ── Column body ── */
.column-body {
  padding: 0 8px 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
  min-height: 40px;
}

/* ── + New button ── */
.col-add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 10px 14px;
  border: none;
  border-top: 1px solid var(--border);
  background: transparent;
  color: var(--text-light);
  font-size: 12.5px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: color 0.12s, background 0.12s;
  flex-shrink: 0;
}
.col-add-btn:hover {
  color: var(--text-muted);
  background: var(--bg);
}

/* ── Dark mode ── */
:global([data-theme="dark"]) .board-column {
  background: #1E2732;
  border-color: #2F3E4E;
}
:global([data-theme="dark"]) .col-add-btn {
  border-top-color: #2F3E4E;
  color: #536471;
}
:global([data-theme="dark"]) .col-add-btn:hover {
  background: rgba(255,255,255,0.04);
  color: #8B98A5;
}
:global([data-theme="dark"]) .count { color: #536471; }

:global([data-theme="dark"]) .col-todo        .column-header h3 { color: #8B98A5; }
:global([data-theme="dark"]) .col-in_progress .column-header h3 { color: #5B9BFF; }
:global([data-theme="dark"]) .col-in_progress .col-dot          { background: #5B9BFF; }
:global([data-theme="dark"]) .col-review      .column-header h3 { color: #FFB300; }
:global([data-theme="dark"]) .col-review      .col-dot          { background: #FFB300; }
:global([data-theme="dark"]) .col-blocked     .column-header h3 { color: #FF6B78; }
:global([data-theme="dark"]) .col-blocked     .col-dot          { background: #FF6B78; }
:global([data-theme="dark"]) .col-completed   .column-header h3 { color: #00BA7C; }
:global([data-theme="dark"]) .col-completed   .col-dot          { background: #00BA7C; }
:global([data-theme="dark"]) .col-todo        .col-dot          { background: #8B98A5; }
</style>
