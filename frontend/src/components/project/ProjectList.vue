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
        <div class="proj-inner">
          <!-- Top: status chip + menu -->
          <div class="proj-top">
            <span class="proj-status-chip" :class="`chip-${project.status}`">
              <span class="chip-dot"></span>
              {{ statusLabel(project.status) }}
            </span>
            <span v-if="project.is_archived" class="proj-archived-tag">Archived</span>
          </div>

          <!-- Title + description -->
          <div class="proj-body">
            <h3 class="proj-title">{{ project.title }}</h3>
            <p v-if="project.description" class="proj-desc">{{ project.description }}</p>
          </div>

          <!-- Footer -->
          <div class="proj-footer">
            <span v-if="project.due_date" class="proj-due" :class="isOverdue(project.due_date) ? 'proj-due--overdue' : ''">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
                <rect x="1" y="1.5" width="10" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                <path d="M1 4.5h10M4 1v2M8 1v2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
              </svg>
              {{ formatDate(project.due_date) }}
            </span>
            <span v-else class="proj-no-date">No due date</span>
            <span class="proj-updated">Updated {{ timeAgo(project.updated_at) }}</span>
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
import SkeletonCard from '../common/SkeletonCard.vue'

const props = defineProps<{ workspaceId: number }>()

const router = useRouter()
const projectStore = useProjectStore()
const membersStore = useMembersStore()
const docStore = useDocumentStore()
const showForm = ref(false)

// Post-creation journey: document upload
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
  if (journeyProjectUuid.value) router.push(`/projects/${journeyProjectUuid.value}`)
}

function goToProject() {
  showDocJourney.value = false
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

const STATUS_META: Record<ProjectStatus, { label: string; color: string }> = {
  planning:  { label: 'Planning',  color: '#A8A0F8' },
  active:    { label: 'Active',    color: '#00BA7C' },
  on_hold:   { label: 'On Hold',   color: '#FFB300' },
  completed: { label: 'Completed', color: '#68CC80' },
  archived:  { label: 'Archived',  color: '#8B98A5' },
}

function statusLabel(s: ProjectStatus) { return STATUS_META[s]?.label ?? s }

function isOverdue(d: string) {
  return new Date(d) < new Date()
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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
  // Trigger document upload journey
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

.section-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
}

.section-sub {
  font-size: 12.5px;
  color: var(--text-muted);
  margin-top: 2px;
}

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
  grid-template-columns: repeat(auto-fill, minmax(288px, 1fr));
  gap: 14px;
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
  width: 60px;
  height: 60px;
  background: #1c1c1e;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px rgba(10,11,13,0.22);
}

.empty-projects h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
}

.empty-projects p {
  font-size: 13.5px;
  color: var(--text-muted);
  max-width: 260px;
  line-height: 1.55;
}

/* ── Project card ── */
.project-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.18s, border-color 0.18s;
  overflow: hidden;
  position: relative;
  min-height: 160px;
  box-shadow: 0 2px 8px rgba(10,11,13,0.06), 0 0 0 0 transparent;
}

.project-card:hover {
  box-shadow: 0 12px 40px rgba(10,11,13,0.13), 0 2px 8px rgba(10,11,13,0.07);
  transform: translateY(-4px);
  border-color: var(--border-strong);
}

.project-card:active {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(10,11,13,0.1);
}

.proj-inner {
  padding: 18px 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
  height: 100%;
}

:global([data-theme="dark"]) .project-card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
:global([data-theme="dark"]) .project-card:hover {
  box-shadow: 0 12px 40px rgba(0,0,0,0.45), 0 2px 8px rgba(0,0,0,0.3);
}

.proj-top {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Status chip */
.proj-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 999px;
  letter-spacing: 0.1px;
}

.chip-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  flex-shrink: 0;
}

.chip-planning  { background: rgba(168,160,248,0.18); color: #5248C8; }
.chip-active    { background: rgba(0,186,124,0.14);   color: #00845A; }
.chip-on_hold   { background: rgba(255,179,0,0.16);   color: #A87800; }
.chip-completed { background: rgba(104,204,128,0.18); color: #1A5820; }
.chip-archived  { background: rgba(139,152,165,0.15); color: #536471; }

.chip-planning  .chip-dot { background: #A8A0F8; }
.chip-active    .chip-dot { background: #00BA7C; }
.chip-on_hold   .chip-dot { background: #FFB300; }
.chip-completed .chip-dot { background: #68CC80; }
.chip-archived  .chip-dot { background: #8B98A5; }

.proj-archived-tag {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-light);
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 2px 7px;
  border-radius: 999px;
  letter-spacing: 0.2px;
}

.proj-body { flex: 1; }

.proj-title {
  font-size: 15.5px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
  line-height: 1.3;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.proj-desc {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Footer */
.proj-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}

.proj-due {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-muted);
}

.proj-due--overdue {
  color: var(--danger);
}

.proj-no-date {
  font-size: 11.5px;
  color: var(--text-light);
}

.proj-updated {
  font-size: 11px;
  color: var(--text-light);
  white-space: nowrap;
}
</style>
