<template>
  <div class="task-board">
    <div class="section-header">
      <h2>Tasks</h2>
      <button class="btn btn-sm btn-primary" @click="showModal = true">+ New Task</button>
    </div>
    <div v-if="loading" class="loading">Loading…</div>
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
          <h3>{{ col.label }}</h3>
          <span class="count">{{ grouped[col.key]?.length || 0 }}</span>
        </div>
        <div class="column-body">
          <TaskCard
            v-for="task in grouped[col.key]"
            :key="task.id"
            :task="task"
            @dragstart="onDragStart"
          />
          <p v-if="!grouped[col.key]?.length" class="empty-col">Empty</p>
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
  { key: 'completed',   label: 'Completed' },
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
.task-board {
  padding: 0;
}

.board-columns {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 12px;
  align-items: flex-start;
}

.board-column {
  flex: 0 0 260px;
  background: var(--surface);
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
  padding: 12px 14px 10px;
  border-bottom: 1px solid var(--border);
}

.column-header h3 {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-muted);
}

.col-todo       .column-header h3 { color: #71717a; }
.col-in_progress .column-header h3 { color: #0369a1; }
.col-review     .column-header h3 { color: #92400e; }
.col-blocked    .column-header h3 { color: #991b1b; }
.col-completed  .column-header h3 { color: #065f46; }

.count {
  background: var(--bg);
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border);
}

.column-body {
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
  min-height: 80px;
}

.empty-col {
  font-size: 12px;
  color: var(--text-light);
  text-align: center;
  padding: 20px 0;
}
</style>
