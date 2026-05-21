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
    <SkeletonBoard v-if="loading" />
    <div v-else class="board-columns">
      <div
        v-for="col in columns"
        :key="col.key"
        class="board-column"
        :class="`col-${col.key}`"
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
import type { TaskStatus } from '../../types'
import { patch } from '../../stores/client'
import TaskCard from './TaskCard.vue'
import TaskModal from './TaskModal.vue'
import SkeletonBoard from '../common/SkeletonBoard.vue'

const props = defineProps<{ projectId: number }>()

const taskStore = useTaskStore()
const showModal = ref(false)
const loading = ref(false)
const draggedId = ref<number | null>(null)

interface Column { key: TaskStatus; label: string }

const columns: Column[] = [
  { key: 'todo',        label: 'To Do' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'review',      label: 'Review' },
  { key: 'blocked',     label: 'Blocked' },
  { key: 'completed',   label: 'Done' },
]

const grouped = computed(() => {
  const map: Record<string, any[]> = {}
  for (const col of columns) {
    map[col.key] = taskStore.tasks.filter((t) => t.status === col.key)
  }
  return map
})

async function loadTasks() {
  loading.value = true
  await taskStore.fetchByProject(props.projectId)
  loading.value = false
}

onMounted(loadTasks)
watch(() => props.projectId, loadTasks)

function onDragStart(id: number) { draggedId.value = id }

async function onDrop(status: TaskStatus) {
  if (!draggedId.value) return
  try {
    await patch(`/tasks/${draggedId.value}`, { status })
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

.board-columns {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 16px;
  align-items: flex-start;
}

.board-column {
  flex: 0 0 260px;
  background: var(--bg);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 280px);
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  border-radius: var(--radius) var(--radius) 0 0;
}

.column-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.col-todo        .col-dot { background: #8A919E; }
.col-in_progress .col-dot { background: #0052FF; }
.col-review      .col-dot { background: #F59E0B; }
.col-blocked     .col-dot { background: #CF202F; }
.col-completed   .col-dot { background: #05B169; }

.column-header h3 {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: -0.1px;
  color: var(--text-muted);
}

.col-todo        .column-header h3 { color: #5B616E; }
.col-in_progress .column-header h3 { color: #0039B3; }
.col-review      .column-header h3 { color: #92400E; }
.col-blocked     .column-header h3 { color: #BE123C; }
.col-completed   .column-header h3 { color: #027A48; }

.count {
  background: var(--surface);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
  min-width: 24px;
  text-align: center;
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
  padding: 24px 0;
  color: var(--text-light);
}

.empty-col span {
  font-size: 11.5px;
}
</style>
