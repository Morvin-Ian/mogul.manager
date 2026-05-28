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
            <!-- Status accent pill -->
            <div class="proj-status-icon" :class="`icon-${project.status}`">
              <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
                <rect x="3" y="3" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
                <rect x="11" y="3" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
                <rect x="3" y="11" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
                <rect x="11" y="11" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>

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

      <TaskBoard :project-id="project.id" :workspace-id="project.workspace_id" />

      <ProjectForm
        v-if="showForm"
        :project="editingProject"
        :workspace-id="project.workspace_id"
        @close="closeForm"
        @saved="onSave"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projects'
import { useMembersStore } from '../stores/members'
import { useAuthStore } from '../stores/auth'
import { useConfirm } from '../composables/useConfirm'
import type { Project, ProjectStatus } from '../types'
import TaskBoard from '../components/task/TaskBoard.vue'
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
const { confirm } = useConfirm()

const showForm = ref(false)
const editingProject = ref<Project | null>(null)
const projectId = computed(() => Number(route.params.id))
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
        await membersStore.fetchMyMembership(projectStore.current.workspace_id)
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
  const wsId = project.value.workspace_id
  await projectStore.remove(projectId.value)
  router.push(`/workspaces/${wsId}`)
}
</script>

<style scoped>
.project-detail {
  padding: 36px 36px 80px;
  max-width: 1400px;
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
  gap: 18px;
}

/* Status icon box */
.proj-status-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-planning  { background: rgba(168,160,248,0.18); color: #5248C8; }
.icon-active    { background: rgba(0,186,124,0.16);   color: #00845A; }
.icon-on_hold   { background: rgba(255,179,0,0.16);   color: #A87800; }
.icon-completed { background: rgba(104,204,128,0.18); color: #1A5820; }
.icon-archived  { background: rgba(139,152,165,0.15); color: #536471; }

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
</style>
