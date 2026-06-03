<template>
  <div class="task-board">
    <div class="board-topbar">
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
        :class="`col-${col.key}`"
      >
        <div class="column-header">
          <div class="column-header-left">
            <span class="col-dot"></span>
            <h3>{{ col.label }}</h3>
            <span class="count">{{ localTasks[col.key]?.length || 0 }}</span>
          </div>
        </div>

        <draggable
          v-model="localTasks[col.key]"
          class="column-body"
          item-key="uuid"
          group="tasks"
          :animation="180"
          ghost-class="task-ghost"
          chosen-class="task-chosen"
          drag-class="task-dragging"
          :data-status="col.key"
          :disabled="!canDragAny"
          @start="onDragStart"
          @end="onDragEnd"
        >
          <template #item="{ element }">
            <TaskCard
              :task="element"
              :can-drag="canDragTask(element)"
              :is-team="isTeam"
              @select="openTask($event)"
            />
          </template>
        </draggable>

        <button class="col-add-btn" @click="showModal = true">
          <font-awesome-icon :icon="['fas', 'plus']" />
          New
        </button>
      </div>
    </div>

    <!-- Empty board nudge -->
    <div v-if="!loading && totalTasks === 0" class="board-empty-nudge">
      <span class="nudge-spark">✦</span>
      <div class="nudge-text">
        <strong>No tasks yet.</strong>
        Let AI break this project into steps and create tasks automatically.
      </div>
      <button class="btn btn-sm nudge-plan-btn" @click="showPlanModal = true">Generate a plan</button>
      <button class="btn btn-sm btn-ghost" @click="showModal = true">Add task manually</button>
    </div>

    <TaskModal
      v-if="showModal"
      :project-id="projectId"
      @close="showModal = false"
      @saved="onTaskCreated"
    />

    <CreatePlanModal
      v-if="showPlanModal"
      :project-id="projectId"
      @close="showPlanModal = false"
      @created="showPlanModal = false"
    />
    <TaskDrawer
      v-if="selectedTask"
      :task="selectedTask"
      :workspace-id="workspaceId ?? null"
      :project-id="projectId"
      @close="closeTask"
      @deleted="closeTask(); loadTasks()"
      @updated="onTaskUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import draggable from 'vuedraggable'
import { useTaskStore } from '../../stores/tasks'
import { usePlanStore } from '../../stores/plans'
import { useMembersStore } from '../../stores/members'
import { useAuthStore } from '../../stores/auth'
import { useTheme } from '../../composables/useTheme'
import type { Task, TaskStatus } from '../../types'
import TaskCard from './TaskCard.vue'
import TaskModal from './TaskModal.vue'
import TaskDrawer from './TaskDrawer.vue'
import CreatePlanModal from '../plan/CreatePlanModal.vue'
import SkeletonBoard from '../common/SkeletonBoard.vue'

const props = defineProps<{
  projectId: number
  workspaceId?: string
  openTaskUuid?: string | null
}>()

const emit = defineEmits<{
  'task-open': [uuid: string]
  'task-close': []
}>()

const taskStore = useTaskStore()
const planStore = usePlanStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const { isDark } = useTheme()

const btnBg = computed(() => isDark.value ? '#F7F9F9' : '#1c1c1e')
const btnColor = computed(() => isDark.value ? '#15202B' : '#ffffff')

const showModal = ref(false)
const showPlanModal = ref(false)
const loading = ref(false)
const dropError = ref<string | null>(null)
const selectedTask = ref<Task | null>(null)
const isSyncing = ref(false)

const MEMBER_ALLOWED: Record<string, Set<TaskStatus>> = {
  todo:        new Set(['in_progress']),
  in_progress: new Set(['todo', 'review']),
  review:      new Set(['todo', 'in_progress']),
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

// SortableJS needs mutable per-column arrays
const localTasks = reactive<Record<string, Task[]>>(
  Object.fromEntries(columns.map(c => [c.key, []]))
)

function syncFromStore() {
  if (isSyncing.value) return
  for (const col of columns) {
    localTasks[col.key] = taskStore.tasks
      .filter(t => t.status === col.key)
      .slice()
  }
}

watch(() => taskStore.tasks, syncFromStore, { deep: true, immediate: true })

// Open a task and notify parent to update the URL
function openTask(task: Task) {
  selectedTask.value = task
  emit('task-open', task.uuid)
}

function closeTask() {
  selectedTask.value = null
  emit('task-close')
}

// Respond to an externally-requested task UUID (from URL query param)
watch(
  [() => props.openTaskUuid, () => taskStore.tasks],
  ([uuid]) => {
    if (!uuid) { selectedTask.value = null; return }
    if (selectedTask.value?.uuid === uuid) return
    const match = taskStore.tasks.find(t => t.uuid === uuid)
    if (match) selectedTask.value = match
  },
  { immediate: true },
)

const myRole = computed(() => membersStore.myMembership?.role ?? null)
const isAdminOrOwner = computed(() => myRole.value === 'admin' || myRole.value === 'owner')
const isSolo = computed(() => membersStore.members.length <= 1)
const isTeam = computed(() => membersStore.members.length > 1)
const totalTasks = computed(() => taskStore.tasks.length)

const canDragAny = computed(() => {
  if (isAdminOrOwner.value || isSolo.value) return true
  return taskStore.tasks.some(t => t.assigned_to_id === auth.user?.id)
})

function canDragTask(task: Task): boolean {
  if (isAdminOrOwner.value || isSolo.value) return true
  return task.assigned_to_id === auth.user?.id
}

async function loadTasks() {
  loading.value = true
  await taskStore.fetchByProject(props.projectId)
  loading.value = false
}

onMounted(async () => {
  await loadTasks()
  if (props.workspaceId) {
    await Promise.all([
      membersStore.fetchMyMembership(props.workspaceId),
      membersStore.fetchMembers(props.workspaceId),
    ])
  }
})

watch(() => props.projectId, loadTasks)
watch(() => props.workspaceId, async (id) => {
  if (id) {
    await Promise.all([
      membersStore.fetchMyMembership(id),
      membersStore.fetchMembers(id),
    ])
  }
})

function onDragStart() {
  dropError.value = null
}

function showDropError(msg: string) {
  dropError.value = msg
  setTimeout(() => { dropError.value = null }, 3500)
}

async function onDragEnd(evt: any) {
  const fromStatus = (evt.from as HTMLElement).dataset.status as TaskStatus
  const toStatus = (evt.to as HTMLElement).dataset.status as TaskStatus
  const newIndex: number = evt.newIndex
  const oldIndex: number = evt.oldIndex
  const sameColumn = fromStatus === toStatus

  // Task is already at newIndex in localTasks[toStatus] — SortableJS moved it
  const movedTask = localTasks[toStatus]?.[newIndex]
  if (!movedTask) { syncFromStore(); return }

  // No-op
  if (sameColumn && newIndex === oldIndex) return

  // Block unassigned tasks in team workspaces — no exceptions
  if (!isSolo.value && movedTask.assigned_to_id === null) {
    showDropError(
      'This task has no assignee. Assign it to a team member before moving it. ' +
      'Tip: ask AI in Chat to assign tasks to the team automatically.'
    )
    syncFromStore(); return
  }

  // Permission check — revert if not allowed
  if (!isAdminOrOwner.value && !isSolo.value) {
    if (movedTask.assigned_to_id !== auth.user?.id) {
      showDropError('You can only move tasks assigned to you.')
      syncFromStore(); return
    }
    if (!sameColumn && !MEMBER_ALLOWED[fromStatus]?.has(toStatus)) {
      showDropError('You can only move: Pending → In Progress → Review, or In Revision back.')
      syncFromStore(); return
    }
  }

  isSyncing.value = true
  try {
    await taskStore.reorder(movedTask.uuid, newIndex, toStatus)
    await taskStore.fetchByProject(props.projectId)
    // If status changed, a linked plan step may have been synced — refresh plans
    if (toStatus !== fromStatus) planStore.fetchByProject(props.projectId)
  } catch (e: any) {
    const msg = e?.response?.data?.detail ?? e?.message
    if (msg) showDropError(msg)
    else console.error(e)
    syncFromStore()
  } finally {
    isSyncing.value = false
  }
}

async function onTaskCreated(data: Record<string, any>) {
  await taskStore.create(data as any)
  showModal.value = false
}

function onTaskUpdated(updated: Task) {
  const previous = taskStore.tasks.find((t) => t.id === updated.id)
  const statusChanged = previous && previous.status !== updated.status
  const idx = taskStore.tasks.findIndex((t) => t.id === updated.id)
  if (idx !== -1) taskStore.tasks[idx] = updated
  selectedTask.value = updated
  // If status changed, a linked plan step may have been synced — refresh plans
  if (statusChanged) planStore.fetchByProject(props.projectId)
}
</script>

<style scoped>
.task-board { padding: 0; }

/* ── Empty nudge ── */
.board-empty-nudge {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.nudge-spark {
  font-size: 16px;
  flex-shrink: 0;
  color: var(--text-muted);
}
.nudge-text {
  flex: 1;
  font-size: 13.5px;
  color: var(--text-muted);
  line-height: 1.5;
  min-width: 200px;
}
.nudge-text strong { color: var(--text); font-weight: 700; }
.nudge-plan-btn {
  background: #1c1c1e;
  color: #fff;
  border-color: #1c1c1e;
}
.nudge-plan-btn:hover { background: #333; border-color: #333; }
:global([data-theme="dark"]) .nudge-plan-btn { background: #F7F9F9; color: #15202B; border-color: #F7F9F9; }
:global([data-theme="dark"]) .nudge-plan-btn:hover { background: #e0e0e0; }

/* ── Board topbar ── */
.board-topbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 18px;
}
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
  overflow: hidden;
}

/* ── Column header ── */
.column-header {
  padding: 14px 14px 10px;
  flex-shrink: 0;
}
.column-header-left { display: flex; align-items: center; gap: 7px; }

.col-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.col-todo        .col-dot { background: #94A3B8; }
.col-in_progress .col-dot { background: #3B82F6; }
.col-review      .col-dot { background: #F59E0B; }
.col-blocked     .col-dot { background: #EF4444; }
.col-completed   .col-dot { background: #10B981; }

.column-header h3 { font-size: 13px; font-weight: 600; letter-spacing: 0; text-transform: none; }
.col-todo        .column-header h3 { color: #64748B; }
.col-in_progress .column-header h3 { color: #3B82F6; }
.col-review      .column-header h3 { color: #F59E0B; }
.col-blocked     .column-header h3 { color: #EF4444; }
.col-completed   .column-header h3 { color: #10B981; }

.count { font-size: 12px; font-weight: 500; color: var(--text-light); line-height: 1; }

/* ── Column body (sortable container) ── */
.column-body {
  padding: 0 8px 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
  min-height: 60px;
}

/* ── SortableJS classes ── */

/* The ghost: hollow placeholder that shows WHERE the card will land */
:global(.task-ghost) {
  opacity: 0 !important;
  /* invisible — the gap itself shows the insertion point */
}

/* The chosen card (lifted): subtle lift + ring */
:global(.task-chosen) {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18), 0 0 0 2px var(--primary) !important;
  transform: scale(1.02) !important;
  z-index: 999;
  cursor: grabbing !important;
}

/* The drag clone following the cursor */
:global(.task-dragging) {
  opacity: 0.95 !important;
  cursor: grabbing !important;
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
.col-add-btn:hover { color: var(--text-muted); background: var(--bg); }

/* ── Dark mode ── */
:global([data-theme="dark"]) .board-column { background: #1E2732; border-color: #2F3E4E; }
:global([data-theme="dark"]) .col-add-btn { border-top-color: #2F3E4E; color: #536471; }
:global([data-theme="dark"]) .col-add-btn:hover { background: rgba(255,255,255,0.04); color: #8B98A5; }
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
