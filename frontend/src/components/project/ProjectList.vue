<template>
  <div class="project-list">
    <div class="section-header">
      <div>
        <h2 class="section-title">Projects</h2>
        <p class="section-sub">{{ projects.length }} project{{ projects.length !== 1 ? 's' : '' }} in this workspace</p>
      </div>
      <button v-if="canCreateProject" class="new-project-btn" @click="showForm = true">
        <font-awesome-icon :icon="['fas', 'plus']" />
        New Project
      </button>
      <span v-else class="member-hint">
        <svg viewBox="0 0 14 14" fill="none" width="11" height="11">
          <circle cx="7" cy="7" r="5.5" stroke="currentColor" stroke-width="1.3"/>
          <path d="M7 6v4M7 4.5v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        Only workspace admins can create projects
      </span>
    </div>

    <div v-if="loading" class="sk-grid">
      <SkeletonCard v-for="n in 4" :key="n" />
    </div>

    <div v-else-if="projects.length === 0" class="empty-projects">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
          <rect x="3" y="3" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
          <rect x="13" y="3" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
          <rect x="3" y="13" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
          <rect x="13" y="13" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
        </svg>
      </div>
      <h4>No projects yet</h4>
      <p v-if="canCreateProject">Add your first project to start tracking work inside this workspace.</p>
      <p v-else>The workspace admin hasn't created any projects yet.</p>
      <button v-if="canCreateProject" class="new-project-btn" @click="showForm = true">
        <font-awesome-icon :icon="['fas', 'plus']" />
        Create project
      </button>
    </div>

    <div v-else class="project-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="$router.push(`/projects/${project.uuid}`)"
      >
        <!-- Top row: folder icon + status -->
        <div class="card-top">
          <div class="card-folder">
            <svg viewBox="0 0 20 20" fill="none" width="20" height="20">
              <path d="M2 5.5A1.5 1.5 0 013.5 4h3.586a1 1 0 01.707.293L9.5 5.5H16.5A1.5 1.5 0 0118 7v8.5A1.5 1.5 0 0116.5 17h-13A1.5 1.5 0 012 15.5v-10z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="card-status-pill">
            <span class="status-dot" :style="{ background: STATUS_COLORS[project.status] }"></span>
            <span class="status-text" :style="{ color: STATUS_COLORS[project.status] }">{{ statusLabel(project.status) }}</span>
          </div>
        </div>

        <!-- Title -->
        <h3 class="card-title">{{ project.title }}</h3>

        <!-- Description -->
        <p class="card-desc">{{ project.description || 'No description added yet.' }}</p>

        <!-- Meta row: due date + updated -->
        <div class="card-meta">
          <span v-if="project.due_date" class="meta-item" :class="{ 'meta-overdue': isOverdue(project.due_date) }">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <rect x="1" y="2" width="12" height="10.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
              <path d="M1 5.5h12M5 1v2.5M9 1v2.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            {{ formatDate(project.due_date) }}
          </span>
          <span v-else class="meta-item meta-nodate">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <rect x="1" y="2" width="12" height="10.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
              <path d="M1 5.5h12M5 1v2.5M9 1v2.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            No due date
          </span>
          <span class="meta-updated">Updated {{ timeAgo(project.updated_at) }}</span>
        </div>

        <!-- Divider -->
        <div class="card-divider"></div>

        <!-- Stats row -->
        <div class="card-stats">
          <div class="stat-progress">
            <!-- Donut progress ring -->
            <svg viewBox="0 0 32 32" width="26" height="26" class="progress-ring">
              <circle cx="16" cy="16" r="12" fill="none" stroke="var(--border)" stroke-width="3.5"/>
              <circle
                cx="16" cy="16" r="12" fill="none"
                :stroke="ringColor(taskPct(project))"
                stroke-width="3.5"
                stroke-linecap="round"
                :stroke-dasharray="`${taskPct(project) * 75.4 / 100} 75.4`"
                transform="rotate(-90 16 16)"
                style="transition: stroke-dasharray 0.4s ease"
              />
            </svg>
            <span class="pct-text">{{ project.task_count > 0 ? taskPct(project) + '%' : '—' }}</span>
          </div>
          <div class="stat-tasks">
            <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
              <path d="M2 4h12M2 8h8M2 12h10" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
            <span>{{ project.completed_count }} / {{ project.task_count }} Tasks</span>
          </div>
        </div>
      </div>
    </div>

    <ProjectForm
      v-if="showForm"
      :workspace-id="workspaceId"
      @close="showForm = false"
      @saved="onProjectSaved"
    />

    <!-- Post-creation: plan prompt -->
    <CreatePlanModal
      v-if="showPlanModal && journeyProjectId"
      :project-id="journeyProjectId"
      @close="onPlanModalClose"
      @created="onPlanCreated"
    />

    <!-- Post-creation: document upload journey -->
    <Teleport to="body">
      <div v-if="showDocJourney" class="journey-overlay" @click.self="skipDocJourney">
        <div class="journey-card">
          <div class="journey-icon journey-icon--doc">
            <font-awesome-icon :icon="['fas', 'file-arrow-up']" />
          </div>
          <h3>Add a document?</h3>
          <p>Upload a file to give your team context for <strong>{{ journeyProjectTitle }}</strong>. It becomes searchable in AI Chat.</p>
          <div v-if="!docUploading && !docUploaded" class="journey-upload-area">
            <label class="upload-label">
              <input type="file" accept=".pdf,.docx,.txt,.csv" hidden @change="onDocFileChange" />
              <font-awesome-icon :icon="['fas', 'cloud-arrow-up']" class="upload-icon" />
              <span>Click to choose a PDF, DOCX, TXT, or CSV</span>
            </label>
          </div>
          <div v-else-if="docUploading" class="journey-upload-state">
            <font-awesome-icon :icon="['fas', 'spinner']" spin />
            Uploading {{ docFileName }}…
          </div>
          <div v-else-if="docUploaded" class="journey-upload-state success">
            <font-awesome-icon :icon="['fas', 'circle-check']" />
            {{ docFileName }} uploaded successfully!
          </div>
          <div class="journey-actions">
            <button class="btn" @click="skipDocJourney">{{ docUploaded ? 'Done' : 'Skip for now' }}</button>
            <button v-if="docUploaded" class="btn btn-primary" @click="goToProject">
              <font-awesome-icon :icon="['fas', 'arrow-right']" />
              Open project
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../../stores/projects'
import { useMembersStore } from '../../stores/members'
import { useDocumentStore } from '../../stores/documents'
import type { ProjectStatus } from '../../types'
import ProjectForm from './ProjectForm.vue'
import CreatePlanModal from '../plan/CreatePlanModal.vue'
import SkeletonCard from '../common/SkeletonCard.vue'

const props = defineProps<{ workspaceId: number }>()

const router = useRouter()
const projectStore = useProjectStore()
const membersStore = useMembersStore()
const docStore = useDocumentStore()
const showForm = ref(false)

// Post-creation journey
const showPlanModal = ref(false)
const showDocJourney = ref(false)
const journeyProjectTitle = ref('')
const journeyProjectId = ref<number | null>(null)
const journeyProjectUuid = ref<string | null>(null)
const docUploading = ref(false)
const docUploaded = ref(false)
const docFileName = ref('')

async function onDocFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file || !journeyProjectId.value) return
  docFileName.value = file.name
  docUploading.value = true
  try {
    await docStore.upload(file, { project_id: journeyProjectId.value })
    docUploaded.value = true
  } finally {
    docUploading.value = false
  }
}
function skipDocJourney() {
  showDocJourney.value = false
  docUploaded.value = false
  docFileName.value = ''
  showPlanModal.value = true        // offer plan prompt next
}
function goToProject() {
  showDocJourney.value = false
  showPlanModal.value = true        // offer plan prompt next
}
function onPlanModalClose() {
  showPlanModal.value = false
  if (journeyProjectUuid.value) router.push(`/projects/${journeyProjectUuid.value}`)
}
function onPlanCreated() {
  showPlanModal.value = false
  if (journeyProjectUuid.value) router.push(`/projects/${journeyProjectUuid.value}`)
}

const loading = ref(false)
const projects = computed(() => projectStore.projects)
const canCreateProject = computed(() => {
  const role = membersStore.myMembership?.role
  return !role || role === 'owner' || role === 'admin'
})

async function loadProjects() {
  loading.value = true
  await Promise.all([
    projectStore.fetchByWorkspace(props.workspaceId),
    membersStore.fetchMyMembership(props.workspaceId),
  ])
  loading.value = false
}
onMounted(loadProjects)
watch(() => props.workspaceId, loadProjects)

const STATUS_META: Record<ProjectStatus, { label: string }> = {
  planning:  { label: 'Planning' },
  active:    { label: 'Active' },
  on_hold:   { label: 'On Hold' },
  completed: { label: 'Completed' },
  archived:  { label: 'Archived' },
}
const STATUS_COLORS: Record<ProjectStatus, string> = {
  planning:  '#8B6FE8',
  active:    '#00BA7C',
  on_hold:   '#F59E0B',
  completed: '#3B82F6',
  archived:  '#8B98A5',
}

function statusLabel(s: ProjectStatus) { return STATUS_META[s]?.label ?? s }

function taskPct(p: { task_count: number; completed_count: number }) {
  if (!p.task_count) return 0
  return Math.round((p.completed_count / p.task_count) * 100)
}

function ringColor(pct: number): string {
  if (pct === 100) return '#00BA7C'
  if (pct >= 60)  return '#3B82F6'
  if (pct >= 30)  return '#F59E0B'
  return '#EF4444'
}

function isOverdue(d: string) { return new Date(d) < new Date() }

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
function timeAgo(d: string) {
  const diff = Math.floor((Date.now() - new Date(d).getTime()) / 60000)
  if (diff < 1) return 'just now'
  if (diff < 60) return `${diff}m ago`
  if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
  return `${Math.floor(diff / 1440)}d ago`
}

async function onProjectSaved(data: Record<string, any>) {
  const project = await projectStore.create({ ...data, workspace_id: data.workspace_id ?? props.workspaceId } as any)
  showForm.value = false
  journeyProjectTitle.value = project.title
  journeyProjectId.value = project.id
  journeyProjectUuid.value = project.uuid
  showDocJourney.value = true
}
</script>

<style scoped>
.project-list { margin-top: 4px; }

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 12px;
}
.section-title { font-size: 18px; font-weight: 800; color: var(--text); letter-spacing: -0.4px; }
.section-sub   { font-size: 12.5px; color: var(--text-muted); margin-top: 2px; }

.new-project-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 18px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
  white-space: nowrap;
  font-family: inherit;
  flex-shrink: 0;
}
.new-project-btn:hover { opacity: 0.82; }
.new-project-btn:active { transform: scale(0.97); }
:global([data-theme="dark"]) .new-project-btn { background: #F7F9F9; color: #15202B; }

.member-hint {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-light);
  font-weight: 500;
  padding: 7px 12px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-full);
}

/* Grid */
.sk-grid,
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

/* ── Project card ── */
.project-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px 22px 18px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0;
  transition: box-shadow 0.2s, transform 0.18s;
  box-shadow: 0 4px 16px rgba(10,11,13,0.08), 0 1px 4px rgba(10,11,13,0.04);
}
.project-card:hover {
  box-shadow: 0 16px 48px rgba(10,11,13,0.16), 0 4px 12px rgba(10,11,13,0.08);
  transform: translateY(-4px);
}

/* Top row */
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.card-folder {
  color: var(--text-light);
  display: flex;
  align-items: center;
}
.card-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-text {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1px;
}

/* Title */
.card-title {
  font-size: 16.5px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
  line-height: 1.25;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Description */
.card-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 14px;
  flex: 1;
}

/* Meta */
.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}
.meta-overdue { color: var(--danger); }
.meta-nodate { color: var(--text-light); }
.meta-updated {
  font-size: 11.5px;
  color: var(--text-light);
  white-space: nowrap;
}

/* Divider */
.card-divider {
  height: 1px;
  background: var(--border);
  margin-bottom: 14px;
}

/* Stats row */
.card-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-progress {
  display: flex;
  align-items: center;
  gap: 6px;
}
.progress-ring { flex-shrink: 0; }
.pct-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}
.stat-tasks {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-muted);
}

/* Empty state */
.empty-projects {
  text-align: center;
  padding: 72px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.empty-icon {
  width: 60px; height: 60px;
  background: #1c1c1e;
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(10,11,13,0.22);
}
.empty-projects h4 { font-size: 16px; font-weight: 700; color: var(--text); letter-spacing: -0.2px; }
.empty-projects p  { font-size: 13.5px; color: var(--text-muted); max-width: 260px; line-height: 1.55; }

/* Dark mode */
:global([data-theme="dark"]) .project-card {
  background: rgba(30,39,50,0.95);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3), 0 1px 4px rgba(0,0,0,0.2);
}
:global([data-theme="dark"]) .project-card:hover {
  box-shadow: 0 16px 48px rgba(0,0,0,0.5), 0 4px 12px rgba(0,0,0,0.3);
}
</style>
