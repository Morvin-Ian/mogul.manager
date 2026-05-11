<template>
  <div class="task-board">
    <div class="section-header">
      <h2>Tasks</h2>
      <button class="btn btn-sm btn-primary" @click="showModal = true">+ New Task</button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else class="board-columns">
      <div v-for="col in columns" :key="col.key" class="board-column" @dragover.prevent @drop="onDrop(col.key)">
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
          <p v-if="!grouped[col.key]?.length" class="empty-col">No tasks</p>
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

const props = defineProps<{
  projectId: number
}>()

const taskStore = useTaskStore()
const showModal = ref(false)
const loading = ref(false)
const draggedId = ref<number | null>(null)

interface Column {
  key: TaskStatus
  label: string
}

const columns: Column[] = [
  { key: 'todo', label: 'To Do' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'review', label: 'Review' },
  { key: 'blocked', label: 'Blocked' },
  { key: 'completed', label: 'Completed' },
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

function onDragStart(id: number) {
  draggedId.value = id
}

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
