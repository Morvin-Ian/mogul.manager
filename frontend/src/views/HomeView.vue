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
          <input v-model="searchQuery" class="search-input" placeholder="Search tasks, projects, meetings..." />
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
      <ProjectsOverview class="overview-panel" :projects="allProjects" />
      <QuickActions
        class="quickactions-panel"
        @create-project="showProjectForm = true"
        @create-workspace="showWorkspaceForm = true"
      />
      <WorkspacesPanel
        class="workspaces-panel"
        :workspaces="workspaceStore.workspaces"
        :projects="allProjects"
        @create="showWorkspaceForm = true"
        @edit="openEditWorkspace"
        @delete="deleteWorkspace"
      />
      <DeadlinesPanel class="deadlines-panel" :tasks="allTasks" :projects="allProjects" />
      <CommentsPanel class="comments-panel" :tasks="allTasks" />
    </div>

    <!-- Project creation modal -->
    <ProjectForm v-if="showProjectForm" @close="showProjectForm = false" @saved="handleProjectSaved" />

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
import { ref, computed, onMounted } from 'vue'
import { useWorkspaceStore } from '../stores/workspaces'
import { useProjectStore } from '../stores/projects'
import { useTaskStore } from '../stores/tasks'
import { useCommentStore } from '../stores/comments'
import { useAuthStore } from '../stores/auth'
import { get } from '../stores/client'
import type { Task, Project, Workspace } from '../types'
import ProjectForm from '../components/project/ProjectForm.vue'
import WorkspaceForm from '../components/workspace/WorkspaceForm.vue'

import TasksPanel from '../components/dashboard/TasksPanel.vue'
import ProjectsOverview from '../components/dashboard/ProjectsOverview.vue'
import QuickActions from '../components/dashboard/QuickActions.vue'
import WorkspacesPanel from '../components/dashboard/WorkspacesPanel.vue'
import DeadlinesPanel from '../components/dashboard/DeadlinesPanel.vue'
import CommentsPanel from '../components/dashboard/CommentsPanel.vue'

const workspaceStore = useWorkspaceStore()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const commentStore = useCommentStore()
const auth = useAuthStore()

const loading = ref(false)
const searchQuery = ref('')
const showProjectForm = ref(false)
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
      await Promise.allSettled(allTasks.value.slice(0, 5).map(t => commentStore.fetchForTask(t.id)))
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

async function handleWorkspaceSaved(data: { title: string; description: string }) {
  if (editingWorkspace.value) {
    await workspaceStore.update(editingWorkspace.value.id, data)
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
  await workspaceStore.remove(id)
  await loadAllData()
}

async function handleProjectSaved(data: Record<string, any>) {
  let wsId = data.workspace_id ?? workspaceStore.workspaces[0]?.id
  if (!wsId) {
    const ws = await workspaceStore.create({ title: 'My Projects', description: null })
    wsId = ws.id
  }
  await projectStore.create({ ...data, workspace_id: wsId } as any)
  showProjectForm.value = false
  await loadAllData()
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

/* ── Dashboard Grid ─────────────────── */
.dash-grid {
  display: grid;
  grid-template-columns: 340px minmax(0, 1fr) 330px;
  grid-template-rows: auto auto auto;
  column-gap: 12px;
  row-gap: 8px;
}

/* ── Grid positions ─────────────────── */
.tasks-panel        { grid-column: 1; grid-row: 1 / 4; display: flex; flex-direction: column; }
.overview-panel     { grid-column: 2; grid-row: 1; align-self: start; }
.quickactions-panel { grid-column: 2; grid-row: 2; align-self: start; }
.workspaces-panel   { grid-column: 2; grid-row: 3; align-self: start; }
.deadlines-panel    { grid-column: 3; grid-row: 1; padding: 16px 18px; }
.comments-panel     { grid-column: 3; grid-row: 2 / 4; }

/* ── Responsive ─────────────────────── */
@media (max-width: 1300px) {
  .dash-grid {
    grid-template-columns: 300px minmax(0, 1fr) 300px;
  }
}

@media (max-width: 960px) {
  .dash-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto;
  }
  .tasks-panel {
    grid-column: 1 / 3;
    grid-row: 1;
  }
  .overview-panel {
    grid-column: 1;
    grid-row: 2;
  }
  .quickactions-panel {
    grid-column: 2;
    grid-row: 2;
  }
  .workspaces-panel {
    grid-column: 1 / 3;
    grid-row: 3;
  }
  .deadlines-panel {
    grid-column: 1;
    grid-row: 4;
  }
  .comments-panel {
    grid-column: 2;
    grid-row: 4;
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
  .overview-panel,
  .workspaces-panel,
  .quickactions-panel,
  .deadlines-panel,
  .comments-panel {
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
