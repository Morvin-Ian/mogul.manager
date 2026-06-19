<template>
  <div class="home-view">
    <!-- Page Header -->
    <div class="page-hdr">
      <div class="page-hdr-left">
        <div>
          <p class="page-sub">Manage and track your projects</p>
          <h1 class="page-title">Project Dashboard</h1>
        </div>
      </div>
      <div class="page-hdr-right">
        <div class="search-bar">
          <svg viewBox="0 0 20 20" fill="none" width="16" height="16" class="search-icon">
            <path
              d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
              fill="currentColor"
            />
          </svg>
          <input
            v-model="searchQuery"
            class="search-input"
            placeholder="Search tasks, projects, meetings..."
            @focus="showSearchDropdown = true"
            @keydown.esc="showSearchDropdown = false"
          />
        </div>

        <!-- Search results dropdown -->
        <div
          v-if="showSearchDropdown && searchQuery.trim()"
          ref="dropdownRef"
          class="search-dropdown"
        >
          <div v-if="noResults" class="sd-empty">
            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
              <circle cx="11" cy="11" r="6" stroke="currentColor" stroke-width="1.5"/>
              <path d="M16.5 16.5l3.5 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>No results for <strong>"{{ searchQuery }}"</strong></span>
          </div>
          <div v-else class="sd-results">
            <div v-if="searchResults.tasks.length" class="sd-group">
              <div class="sd-group-hdr">Tasks</div>
              <div
                v-for="task in searchResults.tasks"
                :key="task.id"
                class="sd-item"
                @mousedown.prevent="goToTask(task)"
              >
                <div class="sd-item-icon">
                  <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
                    <rect x="1.5" y="1.5" width="13" height="13" rx="2" stroke="currentColor" stroke-width="1.3"/>
                    <path d="M5 8l2.5 2.5 4-4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="sd-item-body">
                  <span class="sd-item-title">{{ task.title }}</span>
                  <span class="sd-item-sub">Project #{{ task.project_id }}</span>
                </div>
                <span class="sd-item-status" :class="`sd-status-${task.status ?? 'todo'}`">
                  {{ task.status ?? 'todo' }}
                </span>
              </div>
            </div>
            <div v-if="searchResults.projects.length" class="sd-group">
              <div class="sd-group-hdr">Projects</div>
              <div
                v-for="p in searchResults.projects"
                :key="p.uuid"
                class="sd-item"
                @mousedown.prevent="goToProject(p)"
              >
                <div class="sd-item-icon">
                  <svg viewBox="0 0 20 20" fill="none" width="16" height="16">
                    <path d="M2 5.5A1.5 1.5 0 013.5 4h3.586a1 1 0 01.707.293L9.5 5.5H16.5A1.5 1.5 0 0118 7v8.5A1.5 1.5 0 0116.5 17h-13A1.5 1.5 0 012 15.5v-10z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="sd-item-body">
                  <span class="sd-item-title">{{ p.title }}</span>
                  <span class="sd-item-sub">{{ p.workspace_title || '' }}</span>
                </div>
              </div>
            </div>
            <div v-if="searchResults.workspaces.length" class="sd-group">
              <div class="sd-group-hdr">Workspaces</div>
              <div
                v-for="ws in searchResults.workspaces"
                :key="ws.uuid"
                class="sd-item"
                @mousedown.prevent="goToWorkspace(ws)"
              >
                <div class="sd-item-icon">
                  <svg viewBox="0 0 20 20" fill="none" width="16" height="16">
                    <rect x="2" y="3" width="16" height="14" rx="2" stroke="currentColor" stroke-width="1.4"/>
                    <path d="M2 8h16" stroke="currentColor" stroke-width="1.4"/>
                  </svg>
                </div>
                <div class="sd-item-body">
                  <span class="sd-item-title">{{ ws.title }}</span>
                  <span class="sd-item-sub">{{ ws.description || '' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Dashboard Grid -->
    <div class="dash-grid">
      <TasksPanel
        class="tasks-panel"
        :tasks="myTasks"
        :projects="allProjects"
        :loading="loading"
        :searchQuery="searchQuery"
        @create-project="showProjectForm = true"
        @task-updated="handleTaskUpdated"
      />
      <div class="center-col">
        <ProjectsOverview :projects="allProjects" />
        <QuickActions
          @create-project="showProjectForm = true"
          @create-workspace="showWorkspaceForm = true"
        />
        <WorkspacesPanel
          :workspaces="workspaceStore.workspaces"
          :projects="allProjects"
          @create="showWorkspaceForm = true"
          @edit="openEditWorkspace"
          @delete="deleteWorkspace"
        />
      </div>
      <div class="right-col">
        <DeadlinesPanel :tasks="allTasks" :projects="allProjects" />
        <CommentsPanel :tasks="allTasks" @comment-updated="handleCommentUpdated" />
      </div>
    </div>

    <!-- Project creation modal -->
    <ProjectForm v-if="showProjectForm" @close="showProjectForm = false" @saved="handleProjectSaved" />

    <!-- Post-creation plan prompt -->
    <CreatePlanModal
      v-if="newProjectIdForPlan"
      :project-id="newProjectIdForPlan"
      @close="newProjectIdForPlan = null"
      @created="newProjectIdForPlan = null"
    />

    <!-- Workspace create / edit modal -->
    <WorkspaceForm
      v-if="showWorkspaceForm"
      :workspace="editingWorkspace"
      @close="showWorkspaceForm = false; editingWorkspace = null"
      @saved="handleWorkspaceSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkspaceStore } from '../stores/workspaces'
import { useProjectStore } from '../stores/projects'
import { useTaskStore } from '../stores/tasks'
import { useCommentStore } from '../stores/comments'
import { useAuthStore } from '../stores/auth'
import { get } from '../stores/client'
import type { Task, Project, Workspace } from '../types'
import ProjectForm from '../components/project/ProjectForm.vue'
import WorkspaceForm from '../components/workspace/WorkspaceForm.vue'
import CreatePlanModal from '../components/plan/CreatePlanModal.vue'

import TasksPanel from '../components/dashboard/TasksPanel.vue'
import ProjectsOverview from '../components/dashboard/ProjectsOverview.vue'
import QuickActions from '../components/dashboard/QuickActions.vue'
import WorkspacesPanel from '../components/dashboard/WorkspacesPanel.vue'
import DeadlinesPanel from '../components/dashboard/DeadlinesPanel.vue'
import CommentsPanel from '../components/dashboard/CommentsPanel.vue'

const router = useRouter()
const workspaceStore = useWorkspaceStore()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const commentStore = useCommentStore()
const auth = useAuthStore()

const loading = ref(false)
const searchQuery = ref('')
const showSearchDropdown = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return { tasks: [], projects: [], workspaces: [] }
  return {
    tasks: allTasks.value.filter(t =>
      t.title.toLowerCase().includes(q) || (t.description ?? '').toLowerCase().includes(q)
    ).slice(0, 6),
    projects: allProjects.value.filter(p =>
      p.title.toLowerCase().includes(q) || (p.description ?? '').toLowerCase().includes(q)
    ).slice(0, 5),
    workspaces: workspaceStore.workspaces.filter(ws =>
      ws.title.toLowerCase().includes(q) || (ws.description ?? '').toLowerCase().includes(q)
    ).slice(0, 3),
  }
})

const noResults = computed(() =>
  searchResults.value.tasks.length === 0 &&
  searchResults.value.projects.length === 0 &&
  searchResults.value.workspaces.length === 0
)

// Hide dropdown when query becomes empty
watch(searchQuery, (val) => {
  if (!val.trim()) showSearchDropdown.value = false
})

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') showSearchDropdown.value = false
}

function onClickOutside(e: MouseEvent) {
  const el = dropdownRef.value
  const searchBar = document.querySelector('.search-bar')
  if (showSearchDropdown.value && el && !el.contains(e.target as Node) && searchBar && !searchBar.contains(e.target as Node)) {
    showSearchDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  document.addEventListener('click', onClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.removeEventListener('click', onClickOutside)
})

function goToTask(task: Task) {
  showSearchDropdown.value = false
  searchQuery.value = ''
  router.push(`/projects/${task.project_uuid ?? task.project_id}`)
}

function goToProject(project: Project) {
  showSearchDropdown.value = false
  searchQuery.value = ''
  router.push(`/projects/${project.uuid}`)
}

function goToWorkspace(ws: Workspace) {
  showSearchDropdown.value = false
  searchQuery.value = ''
  router.push(`/workspaces/${ws.uuid}`)
}
const showProjectForm = ref(false)
const newProjectIdForPlan = ref<number | null>(null)
const showWorkspaceForm = ref(false)
const editingWorkspace = ref<Workspace | null>(null)
const allProjects = ref<Project[]>([])
const allTasks = ref<Task[]>([])

// Tasks panel: only show tasks assigned to me, or unassigned tasks (solo workspace)
const myTasks = computed(() =>
  allTasks.value.filter(t =>
    t.assigned_to_id === auth.user?.id || t.assigned_to_id === null
  )
)

async function loadAllData() {
  loading.value = true
  try {
    await workspaceStore.fetchAll()
    const wsIds = workspaceStore.workspaces.map(ws => ws.id)
    if (!wsIds.length) return
    const projectArrays = await Promise.all(wsIds.map(id => get<Project[]>(`/projects?workspace_id=${id}`)))
    allProjects.value = projectArrays.flat()
    const projectIds = allProjects.value.map(p => p.id)
    if (projectIds.length) {
      const taskArrays = await Promise.all(projectIds.map(id => get<Task[]>(`/tasks?project_id=${id}`)))
      allTasks.value = taskArrays.flat()
      commentStore.clear()
      await commentStore.fetchRelevant()
    }
  } catch (e) {
    console.error('Failed to load dashboard data', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadAllData)

function handleTaskUpdated(task: Task) {
  const idx = allTasks.value.findIndex(t => t.id === task.id)
  if (idx !== -1) allTasks.value[idx] = task
}

function handleCommentUpdated(taskId: number, delta: number) {
  const task = allTasks.value.find(t => t.id === taskId)
  if (task) task.comment_count = Math.max(0, (task.comment_count ?? 0) + delta)
}

async function handleWorkspaceSaved(data: { title: string; description: string }) {
  // Backend resolves workspaces by uuid, not numeric id
  if (editingWorkspace.value) {
    await workspaceStore.update(editingWorkspace.value.uuid, data)
    editingWorkspace.value = null
  } else {
    await workspaceStore.create(data)
  }
  showWorkspaceForm.value = false
  await loadAllData()
}

function openEditWorkspace(ws: Workspace) {
  editingWorkspace.value = ws
  showWorkspaceForm.value = true
}

async function deleteWorkspace(id: number) {
  const ws = workspaceStore.workspaces.find(w => w.id === id)
  if (!ws) return
  await workspaceStore.remove(ws.uuid)
  await loadAllData()
}

async function handleProjectSaved(data: Record<string, any>) {
  let wsId = data.workspace_id ?? workspaceStore.workspaces[0]?.id
  if (!wsId) {
    const ws = await workspaceStore.create({ title: 'My Projects', description: null })
    wsId = ws.id
  }
  const project = await projectStore.create({ ...data, workspace_id: wsId } as any)
  showProjectForm.value = false
  await loadAllData()
  newProjectIdForPlan.value = project.id   // trigger plan prompt
}
</script>

<style scoped>
.home-view {
  padding: 32px 40px;
  min-height: 100%;
}

/* ── Page Header ────────────────────── */
.page-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 20px;
}

.page-hdr-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-sub {
  font-size: 13.5px;
  color: var(--text-muted);
  font-weight: 400;
  margin-bottom: 3px;
}

.page-title {
  font-size: 30px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.5px;
  line-height: 1.2;
}

.page-hdr-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.65);
  border: 1.5px solid rgba(200, 200, 208, 0.8);
  border-radius: var(--radius-full);
  padding: 10px 20px;
  width: 420px;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  box-shadow: 0 1px 6px rgba(10,11,13,0.06);
}

.search-bar:focus-within {
  border-color: var(--border-strong);
  background: rgba(255,255,255,0.95);
  box-shadow: 0 2px 12px rgba(10,11,13,0.09);
}

.search-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}

.search-input {
  border: none;
  outline: none;
  background: none;
  font-size: 13.5px;
  color: var(--text);
  width: 100%;
}

.search-input::placeholder {
  color: var(--text-light);
}

/* ── Search Dropdown ──────────────────── */
.search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1.5px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 12px 48px rgba(10,11,13,0.16), 0 4px 12px rgba(10,11,13,0.06);
  z-index: 200;
  padding: 6px;
  max-height: 420px;
  overflow-y: auto;
}

.sd-empty {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px 16px;
  color: var(--text-muted);
  font-size: 13.5px;
  justify-content: center;
}

.sd-results {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sd-group-hdr {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 12px 4px;
}

.sd-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.1s;
}
.sd-item:hover {
  background: var(--bg);
}

.sd-item-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-light);
  flex-shrink: 0;
}

.sd-item-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.sd-item-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sd-item-sub {
  font-size: 11.5px;
  color: var(--text-light);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sd-item-status {
  font-size: 10.5px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: var(--radius-full);
  flex-shrink: 0;
  letter-spacing: 0.1px;
}
.sd-status-todo        { background: #E2E8F0; color: #475569; }
.sd-status-in_progress { background: #D4A878; color: #7A3410; }
.sd-status-review      { background: #80C8C4; color: #106860; }
.sd-status-blocked     { background: #D07878; color: #601010; }
.sd-status-completed   { background: #68CC80; color: #145820; }

/* Dark mode */
:global([data-theme="dark"]) .search-dropdown {
  background: #1e2732;
  border-color: #38444d;
  box-shadow: 0 16px 48px rgba(0,0,0,0.5);
}
:global([data-theme="dark"]) .sd-item:hover {
  background: rgba(255,255,255,0.06);
}

/* ── Dashboard Grid ─────────────────── */
.dash-grid {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr) 330px;
  column-gap: 12px;
}

.tasks-panel { grid-column: 1; display: flex; flex-direction: column; }
.center-col  { grid-column: 2; display: flex; flex-direction: column; gap: 4px; }
.right-col   { grid-column: 3; display: flex; flex-direction: column; gap: 4px; min-height: 0; }

.deadlines-panel { padding: 16px 18px; }
.comments-panel  { flex: 1; min-height: 0; }

/* ── Responsive ─────────────────────── */
@media (max-width: 1300px) {
  .dash-grid {
    grid-template-columns: 300px minmax(0, 1fr) 300px;
  }
}

@media (max-width: 960px) {
  .dash-grid {
    grid-template-columns: 1fr 1fr;
  }
  .tasks-panel {
    grid-column: 1 / 3;
    grid-row: 1;
  }
  .center-col {
    grid-column: 1;
    grid-row: 2;
  }
  .right-col {
    grid-column: 2;
    grid-row: 2;
  }
}

@media (max-width: 640px) {
  .home-view {
    padding: 16px;
  }
  .dash-grid {
    grid-template-columns: 1fr;
  }
  .tasks-panel,
  .center-col,
  .right-col {
    grid-column: 1;
    grid-row: auto;
  }
  .search-bar {
    width: 200px;
  }
  .page-title {
    font-size: 20px;
  }
}
</style>
