<template>
  <div class="project-detail">
    <!-- Skeleton while loading -->
    <template v-if="projectStore.loading">
      <div class="sk-page">
        <!-- Header skeleton -->
        <div class="sk-header">
          <div class="sk sk-back"></div>
          <div class="sk-head-row">
            <div class="sk sk-h1"></div>
            <div class="sk sk-pill"></div>
          </div>
          <div class="sk-meta-row">
            <div class="sk sk-meta-chip"></div>
            <div class="sk sk-meta-chip"></div>
            <div class="sk sk-meta-chip sk-meta-wide"></div>
          </div>
        </div>
        <!-- Tabs skeleton -->
        <div class="sk-tabs-row">
          <div v-for="n in 4" :key="n" class="sk sk-tab"></div>
        </div>
        <!-- Kanban columns skeleton -->
        <div class="sk-board">
          <div v-for="col in 4" :key="col" class="sk-col">
            <div class="sk sk-col-title"></div>
            <div v-for="card in [3,2,4,2][col-1]" :key="card" class="sk-task-card">
              <div class="sk sk-task-line"></div>
              <div class="sk sk-task-line sk-task-short"></div>
              <div class="sk-task-foot">
                <div class="sk sk-task-chip"></div>
                <div class="sk sk-task-avatar"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template v-if="project">
      <div class="page-head">
        <div class="page-head-left">
          <button class="back-pill" @click="$router.back()">
            <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
              <path d="M8 2L4 6l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Back to workspace
          </button>

          <div class="project-head-row">
            <div class="project-title-block">
              <div class="project-title-row">
                <h2>{{ project.title }}</h2>
                <span class="proj-status-pill" :class="`pill-${project.status}`">
                  <span class="pill-dot"></span>
                  {{ statusLabel(project.status) }}
                </span>
              </div>
              <p v-if="project.description" class="proj-description">{{ project.description }}</p>
              <div class="project-meta-inline">
                <span v-if="project.due_date" class="meta-chip">
                  <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                    <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                  </svg>
                  Due {{ formatDate(project.due_date) }}
                </span>
                <span class="meta-chip task-stat-chip">
                  <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                    <rect x="1" y="1" width="10" height="10" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M4 6l2 2 2-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ taskStats.total }} tasks
                </span>
                <span class="meta-chip task-stat-chip task-stat-done">
                  {{ taskStats.done }} done
                </span>
                <span v-if="taskStats.inProgress > 0" class="meta-chip task-stat-chip task-stat-progress">
                  {{ taskStats.inProgress }} in progress
                </span>
                <span v-if="project.ai_summary" class="meta-chip ai-chip">
                  <svg viewBox="0 0 14 14" fill="none" width="10" height="10">
                    <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.2"/>
                    <path d="M5 7l1.5 1.5L9 5.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  {{ project.ai_summary }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="page-actions">
          <button v-if="canEdit" class="btn btn-sm" @click="editProject">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M9.5 2.5l2 2L5 11H3v-2l6.5-6.5zM8.5 3.5l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
          <button v-if="isAdmin" class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
      </div>

      <AiNudge
        storage-key="project-detail"
        label="✨ AI can manage this project for you"
        :prompts="[
          `Create tasks for ${project.title}`,
          `What is blocking ${project.title}?`,
          'Move all overdue tasks to In Revision',
        ]"
      />

      <!-- Tabs -->
      <div class="proj-tabs">
        <button
          class="proj-tab"
          :class="{ active: activeTab === 'board' }"
          @click="activeTab = 'board'"
        >
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <rect x="1" y="1" width="4" height="12" rx="1" stroke="currentColor" stroke-width="1.2"/>
            <rect x="7" y="1" width="4" height="8" rx="1" stroke="currentColor" stroke-width="1.2"/>
            <rect x="7" y="11" width="4" height="2" rx="1" stroke="currentColor" stroke-width="1.2"/>
            <rect x="13" y="1" width="0" height="0" rx="0"/>
          </svg>
          Board
          <span v-if="taskStats.total" class="tab-count">{{ taskStats.total }}</span>
        </button>
        <button
          class="proj-tab"
          :class="{ active: activeTab === 'plan' }"
          @click="activeTab = 'plan'"
        >
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M7 1l1.5 4H13l-3.5 2.5 1.5 4L7 9l-4 2.5 1.5-4L1 5h4.5L7 1z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
          </svg>
          Plan
        </button>
        <button
          class="proj-tab"
          :class="{ active: activeTab === 'docs' }"
          @click="activeTab = 'docs'"
        >
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M3 1h6l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V2a1 1 0 011-1z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>
            <path d="M9 1v3h3M5 7h4M5 9.5h3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
          Documents
          <span v-if="projectDocs.length" class="tab-count">{{ projectDocs.length }}</span>
        </button>
      </div>

      <!-- Board tab -->
      <div v-show="activeTab === 'board'">
        <TaskBoard
          :project-id="project.id"
          :workspace-id="project.workspace_uuid"
          :open-task-uuid="openTaskUuid"
          @task-open="onTaskOpen"
          @task-close="onTaskClose"
        />
      </div>

      <!-- Plan tab -->
      <div v-show="activeTab === 'plan'">
        <PlanPanel :project-id="project.id" />
      </div>

      <!-- Documents tab -->
      <div v-show="activeTab === 'docs'" class="docs-tab">
        <div class="docs-tab-head">
          <p class="docs-tab-sub">Files uploaded here are indexed and searchable by the AI in Chat.</p>
          <div class="docs-tab-actions">
            <button class="btn btn-sm" @click="showDocUpload = true">
              <font-awesome-icon :icon="['fas', 'upload']" />
              Upload document
            </button>
            <button class="btn btn-sm btn-ghost" @click="$router.push('/documents')">
              <font-awesome-icon :icon="['fas', 'arrow-up-right-from-square']" />
              All documents
            </button>
          </div>
        </div>

        <div v-if="projectDocs.length === 0" class="docs-empty">
          <div class="docs-empty-icon">
            <font-awesome-icon :icon="['fas', 'file-lines']" />
          </div>
          <p class="docs-empty-title">No documents yet</p>
          <p class="docs-empty-sub">Upload a PDF, DOCX, TXT or CSV to give your team and AI context for this project.</p>
          <button class="btn btn-primary" @click="showDocUpload = true">
            <font-awesome-icon :icon="['fas', 'upload']" />
            Upload first document
          </button>
        </div>

        <div v-else class="proj-docs-grid">
          <div
            v-for="doc in projectDocs"
            :key="doc.uuid"
            class="proj-doc-card"
            @click="$router.push(`/documents/${doc.uuid}`)"
          >
            <span class="proj-doc-badge" :class="`ftype-${doc.file_type}`">{{ doc.file_type.toUpperCase() }}</span>
            <p class="proj-doc-title">{{ doc.title }}</p>
            <div class="proj-doc-meta">
              <span class="proj-doc-status" :class="`ds-${doc.status}`">{{ doc.status }}</span>
              <span>{{ formatDocSize(doc.file_size) }}</span>
            </div>
          </div>
        </div>
      </div>

      <ProjectForm
        v-if="showForm"
        :project="editingProject"
        :workspace-id="project.workspace_id"
        @close="closeForm"
        @saved="onSave"
      />

      <!-- Document upload modal -->
      <DocUploadModal
        v-if="showDocUpload"
        :workspaces="[]"
        :projects="[]"
        :error="docUploadError"
        :uploading="docUploading"
        :locked-project-id="project.id"
        @close="showDocUpload = false"
        @upload="onDocUpload"
      />
    </template>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documents'
import type { Document } from '../types'
import DocUploadModal from '../components/common/DocUploadModal.vue'
import { useProjectStore } from '../stores/projects'
import { useMembersStore } from '../stores/members'
import { useAuthStore } from '../stores/auth'
import { useTaskStore } from '../stores/tasks'
import { useConfirm } from '../composables/useConfirm'
import type { Project, ProjectStatus } from '../types'
import TaskBoard from '../components/task/TaskBoard.vue'
import AiNudge from '../components/common/AiNudge.vue'
import ProjectForm from '../components/project/ProjectForm.vue'
import PlanPanel from '../components/plan/PlanPanel.vue'

const STATUS_LABELS: Record<ProjectStatus, string> = {
  planning: 'Planning', active: 'Active', on_hold: 'On Hold',
  completed: 'Completed', archived: 'Archived',
}
function statusLabel(s: ProjectStatus) { return STATUS_LABELS[s] ?? s }

const route = useRoute()
const router = useRouter()

const openTaskUuid = computed(() => (route.query.task as string) || null)

function onTaskOpen(uuid: string) {
  if (route.query.task !== uuid) router.replace({ query: { task: uuid } })
}
function onTaskClose() {
  if (route.query.task) router.replace({ query: {} })
}
const projectStore = useProjectStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const taskStore = useTaskStore()
const docStore = useDocumentStore()
const { confirm } = useConfirm()

const activeTab = ref<'board' | 'plan' | 'docs'>('board')
const projectDocs = ref<Document[]>([])

// Document upload
const showDocUpload = ref(false)
const docUploading = ref(false)
const docUploadError = ref<string | null>(null)

async function onDocUpload(file: File) {
  if (!project.value) return
  docUploading.value = true
  docUploadError.value = null
  try {
    await docStore.upload(file, { project_id: project.value.id })
    showDocUpload.value = false
    projectDocs.value = await docStore.fetchByProject(project.value.id)
  } catch (e: any) {
    docUploadError.value = e.message
  } finally {
    docUploading.value = false
  }
}

function formatDocSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const taskStats = computed(() => {
  const tasks = taskStore.tasks
  const total = tasks.length
  const done = tasks.filter((t) => t.status === 'completed').length
  const inProgress = tasks.filter((t) => t.status === 'in_progress').length
  const pct = total ? Math.round((done / total) * 100) : 0
  return { total, done, inProgress, pct }
})

const showForm = ref(false)
const editingProject = ref<Project | null>(null)
const projectId = computed(() => route.params.id as string)
const project = computed(() => projectStore.current)
const membership = computed(() => membersStore.myMembership)
const isAdmin = computed(() => membership.value?.role === 'admin' || membership.value?.role === 'owner')
const canEdit = computed(() => isAdmin.value || project.value?.created_by_id === auth.user?.id)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

watch(projectId, async (id) => {
  if (id) {
    try {
      await projectStore.fetchOne(id)
      if (projectStore.current) {
        const p = projectStore.current
        await membersStore.fetchMyMembership(p.workspace_uuid ?? String(p.workspace_id))
        projectDocs.value = await docStore.fetchByProject(p.id)
      }
    } catch {
      router.push('/')
    }
  }
}, { immediate: true })

function editProject() {
  if (project.value) {
    editingProject.value = { ...project.value }
    showForm.value = true
  }
}

function closeForm() {
  showForm.value = false
  editingProject.value = null
}

async function onSave(data: Record<string, any>) {
  if (editingProject.value) {
    await projectStore.update(projectId.value, data)
  }
  closeForm()
}

async function handleDelete() {
  if (!project.value) return
  const ok = await confirm({
    title: 'Delete project?',
    message: `"${project.value.title}" will be permanently removed.`,
    consequences: [
      'All tasks inside this project will be deleted',
      'All comments and attachments will be lost',
      'This action cannot be undone',
    ],
    confirmLabel: 'Yes, delete project',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  const wsUuid = project.value.workspace_uuid
  await projectStore.remove(projectId.value)
  router.push(`/workspaces/${wsUuid}`)
}
</script>

<style scoped>
.project-detail {
  padding: 36px 40px 80px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 36px;
  gap: 20px;
}

.page-head-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.back-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
  align-self: flex-start;
}
.back-pill:hover { background: var(--bg); color: var(--text); border-color: var(--border-strong); }

.project-head-row {
  display: flex;
  align-items: flex-start;
}

.project-title-block { flex: 1; min-width: 0; }

.project-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.project-title-row h2 {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.7px;
  line-height: 1.2;
}

/* Status pill on project header */
.proj-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 700;
  padding: 4px 11px;
  border-radius: 999px;
}
.pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.pill-planning  { background: rgba(100,116,139,0.15); color: #475569; }
.pill-active    { background: rgba(0,186,124,0.14);   color: #00845A; }
.pill-on_hold   { background: rgba(255,179,0,0.16);   color: #A87800; }
.pill-completed { background: rgba(104,204,128,0.18); color: #1A5820; }
.pill-archived  { background: rgba(139,152,165,0.15); color: #536471; }

.pill-planning  .pill-dot { background: #94A3B8; }
.pill-active    .pill-dot { background: #00BA7C; }
.pill-on_hold   .pill-dot { background: #FFB300; }
.pill-completed .pill-dot { background: #68CC80; }
.pill-archived  .pill-dot { background: #8B98A5; }

.proj-description {
  color: var(--text-muted);
  font-size: 13.5px;
  line-height: 1.6;
  margin-bottom: 10px;
}

.project-meta-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--bg);
  border: 1.5px solid var(--border);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.ai-chip {
  color: var(--primary);
  background: var(--primary-light);
  border-color: var(--primary-border);
}

/* Task stat chips */
.task-stat-chip {
  font-weight: 600;
}

.task-stat-done {
  background: #ECFDF5;
  color: #047857;
  border-color: #A7F3D0;
}

.task-stat-progress {
  background: #EBF0FF;
  color: #1D4ED8;
  border-color: rgba(0, 82, 255, 0.2);
}

/* Dark mode overrides */
:global([data-theme="dark"]) .task-stat-done {
  background: rgba(0, 186, 124, 0.15);
  color: #00BA7C;
  border-color: rgba(0, 186, 124, 0.3);
}

:global([data-theme="dark"]) .task-stat-progress {
  background: rgba(91, 155, 255, 0.15);
  color: #5B9BFF;
  border-color: rgba(91, 155, 255, 0.3);
}

/* ── Tabs ── */
.proj-tabs {
  display: flex;
  gap: 2px;
  border-bottom: 1.5px solid var(--border);
  margin-bottom: 0;
  padding: 0 2px;
}
.proj-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1.5px;
  cursor: pointer;
  font-family: inherit;
  transition: color 0.14s, border-color 0.14s;
  letter-spacing: -0.1px;
}
.proj-tab:hover { color: var(--text); }
.proj-tab.active {
  color: var(--text);
  border-bottom-color: #1c1c1e;
}
:global([data-theme="dark"]) .proj-tab.active { border-bottom-color: #F7F9F9; }
.tab-count {
  font-size: 11px;
  font-weight: 700;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 1px 6px;
  color: var(--text-muted);
}
.proj-tab.active .tab-count {
  background: #1c1c1e;
  color: #fff;
  border-color: #1c1c1e;
}
:global([data-theme="dark"]) .proj-tab.active .tab-count { background: #F7F9F9; color: #15202B; border-color: #F7F9F9; }

/* ── Documents tab ── */
.docs-tab {
  padding-top: 24px;
}
.docs-tab-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.docs-tab-sub {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
}
.docs-tab-actions { display: flex; gap: 8px; flex-shrink: 0; }

.docs-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 20px;
  text-align: center;
}
.docs-empty-icon {
  width: 56px; height: 56px;
  border-radius: 16px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  color: var(--text-light);
}
.docs-empty-title { font-size: 15px; font-weight: 700; color: var(--text); }
.docs-empty-sub { font-size: 13.5px; color: var(--text-muted); max-width: 340px; line-height: 1.6; }

/* ── Shared section styles ── */
.proj-section-header, .proj-docs-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;
}
.proj-section-title, .proj-docs-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 700; color: var(--text);
}
.proj-section-count, .proj-docs-count {
  font-size: 11px; font-weight: 600; color: var(--text-light);
  background: var(--bg); border: 1px solid var(--border);
  padding: 1px 7px; border-radius: var(--radius-full);
}
.proj-docs-actions { display: flex; gap: 8px; }

/* ── Project documents section ── */
.proj-docs-section {
  margin-top: 32px;
  padding-top: 28px;
  border-top: 1.5px solid var(--border);
}
.proj-docs-header {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;
}
.proj-docs-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 700; color: var(--text);
}
.proj-docs-count {
  font-size: 11px; font-weight: 600; color: var(--text-light);
  background: var(--bg); border: 1px solid var(--border);
  padding: 1px 7px; border-radius: var(--radius-full);
}
.proj-docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}
.proj-doc-card {
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--radius-lg); padding: 12px 14px;
  cursor: pointer; transition: border-color 0.13s, box-shadow 0.13s, transform 0.1s;
  display: flex; flex-direction: column; gap: 5px;
}
.proj-doc-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 3px 12px rgba(10,11,13,0.07);
  transform: translateY(-1px);
}
.proj-doc-badge {
  align-self: flex-start;
  font-size: 9.5px; font-weight: 800; letter-spacing: 0.5px;
  padding: 2px 7px; border-radius: var(--radius-full); border: 1px solid;
}
.ftype-pdf  { background: #FFF1F2; color: #BE123C; border-color: #FECDD3; }
.ftype-docx { background: #EFF6FF; color: #1D4ED8; border-color: #BFDBFE; }
.ftype-txt  { background: var(--bg); color: var(--text-light); border-color: var(--border); }
.ftype-csv  { background: #F0FDF4; color: #15803D; border-color: #BBF7D0; }
.proj-doc-title {
  font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}
.proj-doc-meta {
  display: flex; align-items: center; gap: 8px;
  font-size: 11.5px; color: var(--text-light);
}
.proj-doc-status {
  font-size: 10.5px; font-weight: 700; padding: 1px 7px;
  border-radius: var(--radius-full); text-transform: capitalize;
}
.ds-ready      { background: rgba(0,186,124,0.14); color: #00845A; }
.ds-processing,.ds-pending { background: rgba(0,82,255,0.1); color: var(--primary); }
.ds-failed     { background: rgba(207,32,47,0.1); color: #CF202F; }

/* ── Skeleton ── */
@keyframes sk-shimmer { 0%{background-position:-600px 0} 100%{background-position:600px 0} }
.sk {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 600px 100%;
  animation: sk-shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
}
.sk-page    { padding: 36px 40px 80px; }
.sk-header  { margin-bottom: 28px; display: flex; flex-direction: column; gap: 10px; }
.sk-back    { height: 24px; width: 100px; border-radius: 99px; }
.sk-head-row{ display: flex; align-items: center; gap: 12px; margin-top: 4px; }
.sk-h1      { height: 28px; width: 260px; }
.sk-pill    { height: 22px; width: 80px; border-radius: 99px; }
.sk-meta-row{ display: flex; gap: 8px; }
.sk-meta-chip  { height: 20px; width: 70px; border-radius: 99px; }
.sk-meta-wide  { width: 140px; }
.sk-tabs-row{ display: flex; gap: 6px; margin-bottom: 24px; }
.sk-tab     { height: 32px; width: 80px; border-radius: 8px; }
.sk-board   { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.sk-col     { display: flex; flex-direction: column; gap: 10px; }
.sk-col-title { height: 18px; width: 80px; margin-bottom: 6px; }
.sk-task-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  padding: 12px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.sk-task-line  { height: 13px; width: 100%; }
.sk-task-short { width: 65%; }
.sk-task-foot  { display: flex; align-items: center; justify-content: space-between; margin-top: 2px; }
.sk-task-chip  { height: 16px; width: 50px; border-radius: 99px; }
.sk-task-avatar{ width: 22px; height: 22px; border-radius: 50%; }
</style>
