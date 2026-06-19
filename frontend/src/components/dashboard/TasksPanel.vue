<template>
  <div class="panel" style="display:flex;flex-direction:column;">
    <div class="panel-hdr">
      <span class="panel-title">My Tasks</span>
      <button class="add-btn" @click="$emit('create-project')" title="New Project">+</button>
    </div>
    <div class="task-filter">
      <button class="filter-pill" :class="{ active: taskFilter === 'all' }" @click="taskFilter = 'all'">All</button>
      <button class="filter-pill" :class="{ active: taskFilter === 'today' }" @click="taskFilter = 'today'">Today</button>
      <button class="filter-pill" :class="{ active: taskFilter === 'tomorrow' }" @click="taskFilter = 'tomorrow'">Tomorrow</button>
    </div>
    <div class="ongoing-wrap">
      <div class="ongoing-row" @click="showStatusDropdown = !showStatusDropdown">
        <span class="ongoing-badge">{{ badgeCount }}</span>
        <span class="ongoing-label">{{ activeStatusLabel }}</span>
        <svg viewBox="0 0 16 16" fill="currentColor" width="13" height="13"
          class="chevron-icon" :class="{ 'chevron-open': showStatusDropdown }">
          <path fill-rule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clip-rule="evenodd"/>
        </svg>
      </div>
      <div v-if="showStatusDropdown" class="status-dropdown">
        <button
          v-for="s in statusOptions" :key="String(s.value)"
          class="status-opt"
          :class="{ active: statusFilter === s.value }"
          @click="selectStatus(s.value)"
        >
          <span class="status-opt-dot" :style="{ background: s.color }"/>
          <span class="status-opt-label">{{ s.label }}</span>
          <span class="status-opt-count">{{ countForStatus(s.value) }}</span>
        </button>
      </div>
    </div>
    <div v-if="loading" class="tasks-loading">
      <div class="loading-dot" v-for="n in 3" :key="n" />
    </div>
    <div v-else-if="displayedTasks.length === 0" class="tasks-empty">
      <svg viewBox="0 0 48 48" fill="none" width="44" height="44">
        <rect x="8" y="8" width="14" height="14" rx="3" stroke="#D1D5DB" stroke-width="2"/>
        <rect x="26" y="8" width="14" height="14" rx="3" stroke="#D1D5DB" stroke-width="2"/>
        <rect x="8" y="26" width="14" height="14" rx="3" stroke="#D1D5DB" stroke-width="2"/>
        <rect x="26" y="26" width="14" height="14" rx="3" stroke="#D1D5DB" stroke-width="2"/>
      </svg>
      <p>No tasks yet.</p>
      <button class="btn-sm-primary" @click="$emit('create-project')">Create a project</button>
    </div>
    <div v-else class="task-list">
      <div
        v-for="task in displayedTasks"
        :key="task.id"
        class="task-card"
        :class="`task-card-${task.status ?? 'todo'}`"
        @click="$router.push(`/projects/${task.project_uuid ?? task.project_id}`)"
      >
        <div class="task-card-top">
          <div class="task-proj-chip" :class="`task-chip-${task.status ?? 'todo'}`">
            {{ taskInitials(task.title) }}
          </div>
          <button
            class="task-check"
            :class="{ done: task.status === 'completed' }"
            @click.stop="toggleTask(task)"
          >
            <svg viewBox="0 0 20 20" fill="none" width="11" height="11">
              <path d="M4 10l4.5 4.5 7.5-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        <h4 class="task-title">{{ task.title }}</h4>
        <p v-if="task.description" class="task-desc">{{ task.description }}</p>
        <div class="task-status-row">
          <span class="task-status-pill" :class="`status-pill-${task.status ?? 'todo'}`">
            {{ statusLabelFor(task.status) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTaskStore } from '../../stores/tasks'
import type { Task, Project } from '../../types'

const props = defineProps<{ tasks: Task[]; projects: Project[]; loading: boolean; searchQuery: string }>()
const emit = defineEmits<{ 'create-project': []; 'task-updated': [task: Task] }>()

const taskStore = useTaskStore()

const taskFilter = ref<'all' | 'today' | 'tomorrow'>('all')
const statusFilter = ref<string | null>(null)
const showStatusDropdown = ref(false)

const effectiveSearch = computed(() => props.searchQuery)

const statusOptions = [
  { value: null,          label: 'All Tasks',    color: '#64748B' },
  { value: 'todo',        label: 'Pending',       color: '#64748B' },
  { value: 'in_progress', label: 'In Progress',  color: '#B06030' },
  { value: 'review',      label: 'In Review',    color: '#1A8878' },
  { value: 'blocked',     label: 'In Revision', color: '#C04040' },
  { value: 'completed',   label: 'Completed',    color: '#28A048' },
]

function countForStatus(value: string | null) {
  if (value === null) return props.tasks.filter(t => t.status !== 'completed').length
  return props.tasks.filter(t => t.status === value).length
}

function selectStatus(value: string | null) {
  statusFilter.value = value
  showStatusDropdown.value = false
}

const badgeCount = computed(() => countForStatus(statusFilter.value))

const activeStatusLabel = computed(() =>
  statusOptions.find(s => s.value === statusFilter.value)?.label ?? 'On Going Tasks'
)

const displayedTasks = computed(() => {
  const today = new Date().toDateString()
  const tomorrow = new Date(Date.now() + 86400000).toDateString()
  let tasks = props.tasks

  if (effectiveSearch.value.trim()) {
    const q = effectiveSearch.value.toLowerCase()
    tasks = tasks.filter(
      t => t.title.toLowerCase().includes(q) || (t.description ?? '').toLowerCase().includes(q)
    )
  }

  if (statusFilter.value !== null) {
    tasks = tasks.filter(t => t.status === statusFilter.value)
  }

  if (taskFilter.value === 'today') {
    tasks = tasks.filter(t => t.due_date && new Date(t.due_date).toDateString() === today)
  } else if (taskFilter.value === 'tomorrow') {
    tasks = tasks.filter(t => t.due_date && new Date(t.due_date).toDateString() === tomorrow)
  }

  return tasks.slice(0, 20)
})

function taskInitials(title: string): string {
  const words = title.trim().split(/\s+/)
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase()
  return words[0].slice(0, 2).toUpperCase()
}

function statusLabelFor(status: string | undefined): string {
  const map: Record<string, string> = {
    todo: 'Pending',
    in_progress: 'In Progress',
    review: 'In Review',
    blocked: 'In Revision',
    completed: 'Completed',
  }
  return map[status ?? 'todo'] ?? 'Pending'
}

async function toggleTask(task: Task) {
  const newStatus = task.status === 'completed' ? 'todo' : 'completed'
  const updated = await taskStore.update(task.uuid, { status: newStatus })
  emit('task-updated', updated)
}
</script>

<style scoped>
/* ── My Tasks Panel ─────────────────── */
.add-btn {
  width: 30px;
  height: 30px;
  background: transparent;
  border: 1.5px solid var(--border-strong);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 20px;
  font-weight: 300;
  line-height: 1;
  transition: border-color 0.12s, color 0.12s;
  padding-bottom: 1px;
}
.add-btn:hover {
  border-color: var(--text);
  color: var(--text);
}

.task-filter {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.filter-pill {
  padding: 7px 18px;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--border);
  background: transparent;
  font-size: 14px;
  font-weight: 400;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s;
}

.filter-pill.active {
  background: #1c1c1e;
  color: #fff;
  border-color: #1c1c1e;
  font-weight: 500;
}

.ongoing-wrap {
  position: relative;
  margin-bottom: 18px;
}

.ongoing-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 18px;
  border: 1.5px solid var(--border);
  border-radius: 20px;
  background: #ffffff;
  cursor: pointer;
  font-size: 14.5px;
  color: var(--text-muted);
  font-weight: 400;
  transition: border-color 0.12s, box-shadow 0.12s;
}

.ongoing-row:hover {
  border-color: var(--border-strong);
  box-shadow: 0 2px 8px rgba(10,11,13,0.07);
}

.ongoing-badge {
  min-width: 26px;
  height: 26px;
  padding: 0 7px;
  background: #1c1c1e;
  color: #fff;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.ongoing-label {
  flex: 1;
  color: var(--text);
  font-weight: 500;
}

.chevron-icon {
  color: var(--text-light);
  transition: transform 0.2s;
}

.chevron-open {
  transform: rotate(180deg);
}

/* ── Status Dropdown ────────────────── */
.status-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1.5px solid var(--border);
  border-radius: 16px;
  padding: 6px;
  z-index: 50;
  box-shadow: 0 8px 24px rgba(10,11,13,0.12);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-opt {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: none;
  background: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 400;
  color: var(--text-muted);
  transition: background 0.12s, color 0.12s;
  text-align: left;
  width: 100%;
}

.status-opt:hover {
  background: var(--bg);
  color: var(--text);
}

.status-opt.active {
  background: var(--bg);
  color: var(--text);
  font-weight: 500;
}

.status-opt-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-opt-label {
  flex: 1;
}

.status-opt-count {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg);
  border-radius: 999px;
  padding: 1px 8px;
}

.tasks-loading {
  display: flex;
  gap: 6px;
  justify-content: center;
  padding: 32px 0;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background: var(--border-strong);
  border-radius: 50%;
  animation: pulse 1.2s ease-in-out infinite;
}

.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

.tasks-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px 0;
  color: var(--text-muted);
  text-align: center;
}

.tasks-empty p {
  font-size: 13px;
}

.btn-sm-primary {
  padding: 7px 16px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-sm-primary:hover {
  opacity: 0.85;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
  overflow-y: auto;
  max-height: 800px;
  min-height: 0;
  padding-right: 2px;
}

.task-card {
  border: 1.5px solid rgba(0,0,0,0.05);
  border-radius: 18px;
  padding: 18px 18px 20px 20px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
}

.task-card:hover {
  box-shadow: 0 6px 20px rgba(10, 11, 13, 0.08);
  transform: translateY(-1px);
}

.task-card-todo        { background: #F8FAFC; border-color: #CBD5E1; }
.task-card-in_progress { background: #F2E0CC; border-color: #CFA070; }
.task-card-review      { background: #D5EDF0; border-color: #80C4C0; }
.task-card-blocked     { background: #F5DEDE; border-color: #CC8888; }
.task-card-completed   { background: #D8F0DC; border-color: #70C888; }

.task-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.task-proj-chip {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.task-chip-todo        { background: #E2E8F0; color: #475569; }
.task-chip-in_progress { background: #D4A878; color: #7A3410; }
.task-chip-review      { background: #80C8C4; color: #106860; }
.task-chip-blocked     { background: #D07878; color: #601010; }
.task-chip-completed   { background: #68CC80; color: #145820; }

.task-check {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1.5px solid var(--border-strong);
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: transparent;
  flex-shrink: 0;
  transition: border-color 0.15s, background 0.15s, color 0.15s;
}

.task-check:hover {
  border-color: #10B981;
  color: #10B981;
}

.task-check.done {
  color: #ffffff;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 10px;
  line-height: 1.4;
}

.task-desc {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-status-row {
  margin-top: 8px;
}

.task-status-pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.1px;
}

.status-pill-todo        { background: #E2E8F0; color: #475569; }
.status-pill-in_progress { background: #D4A878; color: #7A3410; }
.status-pill-review      { background: #80C8C4; color: #106860; }
.status-pill-blocked     { background: #D07878; color: #601010; }
.status-pill-completed   { background: #68CC80; color: #145820; }
</style>
