<template>
  <div class="project-detail">
    <Loading v-if="projectStore.loading" label="Loading project…" />

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
              <!-- Task progress bar -->
              <div v-if="taskStats.total > 0" class="progress-bar-wrap">
                <div class="progress-bar-track">
                  <div
                    class="progress-bar-fill"
                    :style="{ width: taskStats.pct + '%' }"
                  ></div>
                </div>
                <span class="progress-pct">{{ taskStats.pct }}%</span>
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
          `Build a plan for ${project.title}`,
          'Move all overdue tasks to In Revision',
        ]"
      />
      <TaskBoard :project-id="project.id" :workspace-id="project.workspace_uuid" />

      <!-- Project plans -->
      <div class="proj-plans-section">
        <div class="proj-section-header">
          <div class="proj-section-title">
            <font-awesome-icon :icon="['fas', 'list-check']" />
            Plans
            <span class="proj-section-count">{{ projectPlans.length }}</span>
          </div>
          <button class="btn btn-sm" @click="showPlanJourney = true">
            <font-awesome-icon :icon="['fas', 'plus']" />
            New plan
          </button>
        </div>
        <div v-if="projectPlans.length" class="proj-plans-grid">
          <div
            v-for="plan in projectPlans"
            :key="plan.uuid"
            class="proj-plan-card"
            @click="$router.push(`/plans/${plan.uuid}`)"
          >
            <div class="plan-card-top">
              <span class="plan-status" :class="`ps-${plan.status}`">{{ plan.status }}</span>
              <span class="plan-meta">{{ plan.steps.length }} steps · {{ planPct(plan) }}%</span>
            </div>
            <p class="plan-title">{{ plan.title }}</p>
            <div class="plan-progress-bar">
              <div class="plan-progress-fill" :style="{ width: planPct(plan) + '%' }" />
            </div>
          </div>
        </div>
        <p v-else class="proj-empty-hint">No plans yet. Create one to break the project into AI-generated steps.</p>
      </div>

      <!-- Project documents -->
      <div class="proj-docs-section">
        <div class="proj-docs-header">
          <div class="proj-docs-title">
            <font-awesome-icon :icon="['fas', 'file-lines']" />
            Documents
            <span class="proj-docs-count">{{ projectDocs.length }}</span>
          </div>
          <div class="proj-docs-actions">
            <button class="btn btn-sm" @click="showDocUpload = true">
              <font-awesome-icon :icon="['fas', 'upload']" />
              Upload
            </button>
            <button class="btn btn-sm" @click="$router.push('/documents')">
              <font-awesome-icon :icon="['fas', 'arrow-up-right-from-square']" />
              All docs
            </button>
          </div>
        </div>
        <div class="proj-docs-grid">
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

    <!-- Plan creation journey -->
    <Teleport to="body">
      <div v-if="showPlanJourney" class="journey-overlay" @click.self="showPlanJourney = false">
        <div class="journey-card">
          <div class="journey-icon">
            <font-awesome-icon :icon="['fas', 'list-check']" />
          </div>
          <h3>Create a plan</h3>
          <p>Describe the goal and AI will break it into steps — aware of this project's existing tasks.</p>
          <div class="journey-input-row">
            <input
              v-model="newPlanTitle"
              class="journey-input"
              placeholder="e.g. Build user auth, Redesign landing page…"
              @keydown.enter="createPlan"
              autofocus
            />
          </div>
          <div class="journey-actions">
            <button class="btn" @click="showPlanJourney = false">Cancel</button>
            <button
              class="btn btn-primary"
              :disabled="!newPlanTitle.trim() || planCreating"
              @click="createPlan"
            >
              <font-awesome-icon v-if="planCreating" :icon="['fas', 'spinner']" spin />
              {{ planCreating ? 'Creating…' : 'Create plan' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDocumentStore } from '../stores/documents'
import { usePlanStore } from '../stores/plans'
import type { Document, Plan } from '../types'
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
import Loading from '../components/common/Loading.vue'

const STATUS_LABELS: Record<ProjectStatus, string> = {
  planning: 'Planning', active: 'Active', on_hold: 'On Hold',
  completed: 'Completed', archived: 'Archived',
}
function statusLabel(s: ProjectStatus) { return STATUS_LABELS[s] ?? s }

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const taskStore = useTaskStore()
const docStore = useDocumentStore()
const planStore = usePlanStore()
const { confirm } = useConfirm()

const projectDocs = ref<Document[]>([])
const projectPlans = ref<Plan[]>([])

// Plan creation
const showPlanJourney = ref(false)
const newPlanTitle = ref('')
const planCreating = ref(false)

async function createPlan() {
  if (!newPlanTitle.value.trim() || !project.value) return
  planCreating.value = true
  try {
    const plan = await planStore.create({ title: newPlanTitle.value.trim(), project_id: project.value.id })
    showPlanJourney.value = false
    newPlanTitle.value = ''
    projectPlans.value = await planStore.fetchByProject(project.value.id)
    router.push(`/plans/${plan.uuid}`)
  } finally {
    planCreating.value = false
  }
}

function planPct(plan: Plan): number {
  if (!plan.steps.length) return 0
  const done = plan.steps.filter(s => s.status === 'completed' || s.status === 'skipped').length
  return Math.round((done / plan.steps.length) * 100)
}

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
        ;[projectDocs.value, projectPlans.value] = await Promise.all([
          docStore.fetchByProject(p.id),
          planStore.fetchByProject(p.id),
        ])
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
.pill-planning  { background: rgba(168,160,248,0.18); color: #5248C8; }
.pill-active    { background: rgba(0,186,124,0.14);   color: #00845A; }
.pill-on_hold   { background: rgba(255,179,0,0.16);   color: #A87800; }
.pill-completed { background: rgba(104,204,128,0.18); color: #1A5820; }
.pill-archived  { background: rgba(139,152,165,0.15); color: #536471; }

.pill-planning  .pill-dot { background: #A8A0F8; }
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

/* Progress bar */
.progress-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
}

.progress-bar-track {
  flex: 1;
  height: 4px;
  background: var(--border);
  border-radius: 999px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10B981, #059669);
  border-radius: 999px;
  transition: width 0.4s ease;
  min-width: 2px;
}

.progress-pct {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-muted);
  flex-shrink: 0;
  min-width: 34px;
  text-align: right;
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

:global([data-theme="dark"]) .progress-bar-track {
  background: #38444D;
}

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

/* ── Project plans section ── */
.proj-plans-section {
  margin-top: 32px;
  padding-top: 28px;
  border-top: 1.5px solid var(--border);
}
.proj-plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}
.proj-plan-card {
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--radius-lg); padding: 14px 16px;
  cursor: pointer; transition: border-color 0.13s, box-shadow 0.13s, transform 0.1s;
  display: flex; flex-direction: column; gap: 7px;
}
.proj-plan-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 3px 12px rgba(10,11,13,0.07);
  transform: translateY(-1px);
}
.plan-card-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; }
.plan-title { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.35; }
.plan-meta { font-size: 11px; color: var(--text-light); }
.plan-status {
  font-size: 10.5px; font-weight: 700; padding: 2px 8px;
  border-radius: var(--radius-full); text-transform: capitalize;
}
.ps-active    { background: rgba(0,186,124,0.14); color: #00845A; }
.ps-draft     { background: rgba(139,152,165,0.15); color: #536471; }
.ps-completed { background: rgba(104,204,128,0.18); color: #1A5820; }
.ps-cancelled { background: rgba(207,32,47,0.1); color: #CF202F; }
.plan-progress-bar {
  height: 3px; background: var(--border); border-radius: 999px; overflow: hidden;
}
.plan-progress-fill {
  height: 100%; background: linear-gradient(90deg, #10B981, #059669);
  border-radius: 999px; transition: width 0.3s;
}
.proj-empty-hint { font-size: 13px; color: var(--text-muted); font-style: italic; }

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
</style>
