<template>
  <div class="deps-tab">
    <div v-if="store.loading" class="feed-empty">Loading dependencies…</div>

    <template v-else>
      <div class="dep-section">
        <div class="dep-section-title">
          <font-awesome-icon :icon="['fas', 'arrow-up-long']" />
          Depends on
          <span class="dep-count">{{ store.dependsOn.length }}</span>
        </div>
        <p v-if="store.dependsOn.length === 0" class="dep-empty">
          No upstream dependencies — this task is not blocked by anything.
        </p>
        <div v-else class="dep-list">
          <div v-for="dep in store.dependsOn" :key="dep.uuid" class="dep-row">
            <div class="dep-info">
              <span class="dep-status-dot" :class="`dsd-${dep.status}`" :title="dep.status"></span>
              <span class="dep-title">{{ dep.title }}</span>
              <span v-if="dep.assignee_name" class="dep-assignee">{{ dep.assignee_name }}</span>
            </div>
            <button class="dep-remove" title="Remove dependency" @click="handleRemove(dep.uuid)">
              <font-awesome-icon :icon="['fas', 'xmark']" />
            </button>
          </div>
        </div>
      </div>

      <div class="dep-divider"></div>

      <div class="dep-section">
        <div class="dep-section-title">
          <font-awesome-icon :icon="['fas', 'arrow-down-long']" />
          Blocks
          <span class="dep-count">{{ store.blockedBy.length }}</span>
        </div>
        <p v-if="store.blockedBy.length === 0" class="dep-empty">
          No downstream dependencies — no tasks are blocked by this one.
        </p>
        <div v-else class="dep-list">
          <div v-for="dep in store.blockedBy" :key="dep.uuid" class="dep-row dep-row--blocked">
            <div class="dep-info">
              <span class="dep-status-dot" :class="`dsd-${dep.status}`" :title="dep.status"></span>
              <span class="dep-title">{{ dep.title }}</span>
              <span v-if="dep.assignee_name" class="dep-assignee">{{ dep.assignee_name }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="dep-divider"></div>

      <div class="dep-section">
        <div class="dep-section-title">
          <font-awesome-icon :icon="['fas', 'link']" />
          Add dependency
        </div>
        <div class="add-dep-row">
          <input
            v-model="searchQuery"
            class="dep-search"
            placeholder="Search tasks by title…"
          />
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="t in searchResults"
            :key="t.uuid"
            class="search-result-row"
            @click="handleAdd(t)"
          >
            <span class="dep-status-dot" :class="`dsd-${t.status}`"></span>
            <div class="srr-info">
              <span class="srr-title">{{ t.title }}</span>
              <span v-if="t.assignee_name" class="srr-assignee">{{ t.assignee_name }}</span>
            </div>
            <font-awesome-icon :icon="['fas', 'plus']" class="srr-add" />
          </div>
        </div>
        <p v-else-if="searchQuery" class="dep-empty">No tasks found.</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDependencyStore } from '../../stores/dependencies'
import { useTaskStore } from '../../stores/tasks'
import { useToast } from '../../composables/useToast'
import type { Task } from '../../types'

const props = defineProps<{
  taskUuid: string
  projectId: number
}>()

const emit = defineEmits<{ countChange: [number] }>()

const store = useDependencyStore()
const taskStore = useTaskStore()
const toast = useToast()
const searchQuery = ref('')

const allProjectTasks = computed(() => taskStore.tasks)

const searchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  const q = searchQuery.value.toLowerCase()
  return allProjectTasks.value.filter(
    (t) => t.title.toLowerCase().includes(q) && !isAlreadyDep(t)
  )
})

onMounted(() => {
  store.fetch(props.taskUuid)
  if (taskStore.tasks.length === 0) {
    taskStore.fetchByProject(props.projectId)
  }
})
onUnmounted(() => { store.clear() })

function isAlreadyDep(t: Task): boolean {
  return store.dependsOn.some((d) => d.uuid === t.uuid) || t.uuid === props.taskUuid
}

async function handleAdd(t: Task) {
  if (isAlreadyDep(t)) return
  try {
    await store.add(props.taskUuid, t.uuid)
    toast.success(`Now depends on "${t.title}"`)
    searchQuery.value = ''
    searchResults.value = []
    emit('countChange', store.dependsOn.length)
  } catch (e: any) {
    toast.error(e?.message || 'Failed to add dependency')
  }
}

async function handleRemove(depUuid: string) {
  try {
    await store.remove(props.taskUuid, depUuid)
    toast.success('Dependency removed')
    emit('countChange', store.dependsOn.length)
  } catch (e: any) {
    toast.error(e?.message || 'Failed to remove dependency')
  }
}
</script>

<style scoped>
.deps-tab {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.feed-empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-light);
  font-size: 13px;
}

.dep-section {
  padding: 4px 0;
}

.dep-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 0 6px;
}

.dep-section-title svg {
  opacity: 0.6;
  font-size: 11px;
}

.dep-count {
  background: var(--bg);
  color: var(--text-light);
  font-size: 10px;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 999px;
  margin-left: auto;
}

.dep-empty {
  font-size: 12.5px;
  color: var(--text-light);
  font-style: italic;
  padding: 6px 0;
}

.dep-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.dep-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 8px;
  background: var(--bg);
  border: 1px solid var(--border);
  transition: background 0.1s;
}

.dep-row:hover {
  background: var(--surface);
}

.dep-row--blocked {
  border-left: 3px solid #F59E0B;
}

.dep-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
}

.dep-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dsd-todo        { background: #94A3B8; }
.dsd-in_progress { background: #3B82F6; }
.dsd-review      { background: #F59E0B; }
.dsd-blocked     { background: #EF4444; }
.dsd-completed   { background: #10B981; }

.dep-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dep-assignee {
  font-size: 11px;
  color: var(--text-light);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.dep-remove {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--text-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  transition: all 0.12s;
  flex-shrink: 0;
}

.dep-remove:hover {
  background: #FFF1F2;
  color: #BE123C;
}

.dep-divider {
  height: 1px;
  background: var(--border);
  margin: 10px 0;
}

.add-dep-row {
  padding: 2px 0;
}

.dep-search {
  width: 100%;
  padding: 8px 11px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}

.dep-search:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 6px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
}

.search-result-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  cursor: pointer;
  transition: background 0.1s;
}

.search-result-row:not(.srr-disabled):hover {
  background: var(--bg);
}

.srr-disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.srr-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.srr-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.srr-assignee {
  font-size: 11px;
  color: var(--text-light);
}

.srr-hint {
  font-size: 10px;
  color: var(--text-light);
  font-style: italic;
  flex-shrink: 0;
}

.srr-add {
  color: var(--primary);
  flex-shrink: 0;
  font-size: 12px;
}

:global([data-theme="dark"]) .dep-row {
  background: #253341;
  border-color: #38444D;
}
:global([data-theme="dark"]) .dep-row:hover {
  background: #2E3D4D;
}
:global([data-theme="dark"]) .dep-remove:hover {
  background: rgba(190, 18, 60, 0.2);
  color: #FF6B78;
}
:global([data-theme="dark"]) .dep-search {
  background: #253341;
  border-color: #38444D;
  color: var(--text);
}
:global([data-theme="dark"]) .search-results {
  background: #1E2732;
  border-color: #38444D;
}
:global([data-theme="dark"]) .search-result-row:not(.srr-disabled):hover {
  background: #253341;
}
:global([data-theme="dark"]) .dep-divider {
  background: #38444D;
}
:global([data-theme="dark"]) .dep-count {
  background: #253341;
  color: #8BAFC8;
}
</style>
