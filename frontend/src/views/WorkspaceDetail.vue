<template>
  <div class="workspace-detail">
    <!-- Workspace list view -->
    <template v-if="!workspaceId && !workspaceStore.loading">
      <div class="page-head">
        <div class="page-head-text">
          <h2>Workspaces</h2>
          <p>Organise projects, tasks, and deadlines into focused areas of work.</p>
        </div>
        <div class="page-actions">
          <button class="create-ws-btn" @click="openCreateForm">
            <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
              <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            New Workspace
          </button>
        </div>
      </div>

      <!-- Explainer callout -->
      <div v-if="!dismissedExplainer" class="explainer-callout">
        <button class="explainer-dismiss" @click="dismissExplainer" title="Dismiss">×</button>

        <p class="explainer-heading">How it's organised</p>

        <!-- Primary hierarchy row -->
        <div class="explainer-body">
          <div class="explainer-col">
            <div class="explainer-icon explainer-icon--workspace">
              <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
                <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <p class="explainer-label">Workspace</p>
              <p class="explainer-text">A top-level container for a team or area of work.</p>
              <p class="explainer-example">"Freelance Clients" · "TC4A"</p>
            </div>
          </div>

          <div class="explainer-arrow">
            <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
              <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <div class="explainer-col">
            <div class="explainer-icon explainer-icon--project">
              <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
                <rect x="3" y="3" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
                <rect x="11" y="3" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
                <rect x="3" y="11" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
                <rect x="11" y="11" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.5"/>
              </svg>
            </div>
            <div>
              <p class="explainer-label">Project</p>
              <p class="explainer-text">A focused initiative with a kanban board and timeline.</p>
              <p class="explainer-example">"Website Redesign" · "Q2 Campaign"</p>
            </div>
          </div>

          <div class="explainer-arrow">
            <svg viewBox="0 0 24 24" fill="none" width="18" height="18">
              <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <div class="explainer-col">
            <div class="explainer-icon explainer-icon--task">
              <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
                <path d="M4 10l4 4 8-8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <p class="explainer-label">Task</p>
              <p class="explainer-text">A single action with a status, assignee, and due date.</p>
              <p class="explainer-example">"Write homepage copy" · "Review PR"</p>
            </div>
          </div>
        </div>

        <!-- Supporting concepts row -->
        <div class="explainer-support">
          <div class="support-col">
            <div class="explainer-icon explainer-icon--file">
              <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
                <path d="M13 2H5a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7l-4-5z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                <path d="M13 2v5h5M7 9h6M7 12h6M7 15h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
              </svg>
            </div>
            <div>
              <p class="explainer-label">Files <span class="support-badge support-badge--context">Context</span></p>
              <p class="explainer-text">Upload docs — the AI uses them as grounded context in Chat.</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="workspaceStore.workspaces.length === 0" class="empty-state">
        <div class="empty-state-icon">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M3 7a2 2 0 012-2h3l2 2h9a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>No workspaces yet</h3>
        <p>Create your first workspace to start organizing projects and tasks.</p>
        <button class="btn btn-primary" @click="openCreateForm">Create workspace</button>
      </div>
      <div v-else class="workspace-grid">
        <WorkspaceCard
          v-for="ws in workspaceStore.workspaces"
          :key="ws.id"
          :workspace="ws"
        />
      </div>
    </template>

    <Loading v-if="workspaceStore.loading" label="Loading workspace…" />

    <!-- Single workspace view -->
    <template v-if="currentWorkspace && !workspaceStore.loading">
      <div class="workspace-head">
        <div class="workspace-head-left">
          <button class="back-pill" @click="$router.push('/workspaces')">
            <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
              <path d="M8 2L4 6l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Workspaces
          </button>
          <div class="workspace-head-title">
            <div class="ws-head-initial">{{ currentWorkspace.title.slice(0,1).toUpperCase() }}</div>
            <div>
              <h2>{{ currentWorkspace.title }}</h2>
              <p v-if="currentWorkspace.description">{{ currentWorkspace.description }}</p>
            </div>
          </div>
        </div>
        <div class="workspace-actions">
          <button class="btn btn-sm" @click="$router.push(`/team/${currentWorkspace.uuid}`)">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M5 10.5c0-1.5 1.12-2.5 3-2.5s3 1 3 2.5M3 7.5a1.5 1.5 0 110-3 1.5 1.5 0 010 3zm8 0a1.5 1.5 0 110-3 1.5 1.5 0 010 3zM8 4.5a1.5 1.5 0 110-3 1.5 1.5 0 010 3z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Team
          </button>
          <button v-if="isAdminOrOwner" class="btn btn-sm" @click="editWorkspace">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M9.5 2.5l2 2L5 11H3v-2l6.5-6.5zM8.5 3.5l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
          <button v-if="isOwner" class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
      </div>
      <AiNudge
        storage-key="workspace-detail"
        label="✨ AI can act on this workspace right now"
        :prompts="[
          'What tasks are overdue in this workspace?',
          `Summarize progress across all projects in ${currentWorkspace.title}`,
          'Create a new project and add tasks to it',
          'Which team member has the most tasks?',
        ]"
      />
      <ProjectList :workspace-id="currentWorkspace.id" />

    </template>

    <WorkspaceForm
      v-if="showForm"
      :workspace="editingWorkspace"
      @close="closeForm"
      @saved="onSave"
    />

    <!-- Post-creation: create first project journey -->
    <Teleport to="body">
      <div v-if="showPlanJourney" class="journey-overlay" @click.self="skipPlanJourney">
        <div class="journey-card">
          <div class="journey-icon">
            <font-awesome-icon :icon="['fas', 'folder-plus']" />
          </div>
          <h3>Create your first project?</h3>
          <p><strong>{{ journeyWsTitle }}</strong> is ready. Add a project to start tracking tasks and uploading documents.</p>
          <div class="journey-actions">
            <button class="btn" @click="skipPlanJourney">Skip for now</button>
            <button class="btn btn-primary" @click="skipPlanJourney">
              <font-awesome-icon :icon="['fas', 'arrow-right']" />
              Got it
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWorkspaceStore } from '../stores/workspaces'
import { useMembersStore } from '../stores/members'
import { useAuthStore } from '../stores/auth'
import { useConfirm } from '../composables/useConfirm'
import type { Workspace } from '../types'

import WorkspaceCard from '../components/workspace/WorkspaceCard.vue'
import WorkspaceForm from '../components/workspace/WorkspaceForm.vue'
import ProjectList from '../components/project/ProjectList.vue'
import AiNudge from '../components/common/AiNudge.vue'
import Loading from '../components/common/Loading.vue'

const route = useRoute()
const router = useRouter()
const workspaceStore = useWorkspaceStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const { confirm } = useConfirm()

const isOwner = computed(() => currentWorkspace.value?.user_id === auth.user?.id)
const isAdminOrOwner = computed(() => {
  const role = membersStore.myMembership?.role
  return isOwner.value || role === 'admin'
})

const dismissedExplainer = ref(localStorage.getItem('ws_explainer_dismissed') === '1')
function dismissExplainer() {
  dismissedExplainer.value = true
  localStorage.setItem('ws_explainer_dismissed', '1')
}

onMounted(() => workspaceStore.fetchAll())

const showForm = ref(false)
const editingWorkspace = ref<Workspace | null>(null)

// Post-creation journey: prompt to create first project
const showPlanJourney = ref(false)
const journeyWsTitle = ref('')

function skipPlanJourney() {
  showPlanJourney.value = false
}
const workspaceId = computed(() => {
  const id = route.params.id
  return id ? (id as string) : null
})
const currentWorkspace = computed(() => workspaceStore.current)

watch(workspaceId, async (id) => {
  if (id) {
    try {
      await workspaceStore.fetchOne(id)
      await membersStore.fetchMyMembership(id)
    } catch {
      router.push('/')
    }
  } else {
    workspaceStore.current = null
  }
}, { immediate: true })

function openCreateForm() {
  editingWorkspace.value = null
  showForm.value = true
}

function editWorkspace() {
  if (currentWorkspace.value) {
    editingWorkspace.value = { ...currentWorkspace.value }
    showForm.value = true
  }
}

function closeForm() {
  showForm.value = false
  editingWorkspace.value = null
}

async function onSave(data: { title: string; description: string }) {
  if (editingWorkspace.value && currentWorkspace.value) {
    await workspaceStore.update(currentWorkspace.value.uuid, data)
  } else {
    const ws = await workspaceStore.create(data)
    closeForm()
    router.push(`/workspaces/${ws.uuid}`)
    // Prompt to create first project
    journeyWsTitle.value = ws.title
    showPlanJourney.value = true
    return
  }
  closeForm()
}

async function handleDelete() {
  if (!currentWorkspace.value) return
  const ok = await confirm({
    title: 'Delete workspace?',
    message: `"${currentWorkspace.value.title}" will be permanently deleted.`,
    consequences: [
      'All projects inside this workspace will be deleted',
      'All tasks, comments, and files will be deleted',
      'All team members will lose access',
      'This action cannot be undone',
    ],
    confirmLabel: 'Yes, delete workspace',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await workspaceStore.remove(currentWorkspace.value.uuid)
  router.push('/')
}
</script>

<style scoped>
.workspace-detail {
  padding: 36px 40px 80px;
}

/* Explainer */
.explainer-callout {
  position: relative;
  background: #F4F4F6;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 24px;
}

.explainer-dismiss {
  position: absolute;
  top: 10px;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  color: var(--text-light);
  line-height: 1;
  padding: 2px 6px;
  border-radius: 4px;
  transition: color 0.1s, background 0.1s;
}
.explainer-dismiss:hover { color: var(--text); background: var(--border); }

.explainer-body {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.explainer-col {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 180px;
}

.explainer-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.explainer-icon--workspace { background: #E5E2FF; border: 1px solid #B0A8E8; color: #3830A0; }
.explainer-icon--project   { background: #D5EDF0; border: 1px solid #80C4C0; color: #1A7068; }
.explainer-icon--task      { background: #D8F0D8; border: 1px solid #70C878; color: #1A5820; }
.explainer-icon--file      { background: #F5E4CC; border: 1px solid #D0A060; color: #6A3008; }

.explainer-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 3px;
  letter-spacing: -0.1px;
}

.explainer-text {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  margin-bottom: 4px;
}

.explainer-example {
  font-size: 11px;
  color: var(--text-light);
  letter-spacing: 0.1px;
}

.explainer-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-light);
  padding-top: 8px;
  flex-shrink: 0;
}

.explainer-heading {
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: var(--text-light);
  margin-bottom: 16px;
}

/* supporting concepts */
.explainer-support {
  display: flex;
  gap: 0;
  margin-top: 14px;
  border-top: 1px solid var(--border);
  padding-top: 14px;
}

.support-col {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  padding: 0 12px;
}
.support-col:first-child { padding-left: 0; }
.support-col:last-child  { padding-right: 0; }

.support-divider {
  width: 1px;
  background: var(--border);
  margin: 0 4px;
  flex-shrink: 0;
}

.support-badge {
  display: inline-flex;
  align-items: center;
  padding: 1px 7px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3px;
  vertical-align: middle;
  margin-left: 5px;
}
.support-badge--ai      { background: #F2E0CC; color: #7A3410; border: 1px solid #CFA070; }
.support-badge--context { background: #F5E4CC; color: #6A3008; border: 1px solid #D0A060; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 20px;
  text-align: center;
}

.empty-state p {
  max-width: 320px;
}

.empty-state-icon {
  width: 64px;
  height: 64px;
  background: #E5E2FF;
  border: 1.5px solid #B0A8E8;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3830A0;
}

.empty-state-icon svg { width: 28px; height: 28px; }

.empty-state h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.empty-state p {
  color: var(--text-muted);
  font-size: 14px;
  max-width: 280px;
  line-height: 1.6;
}

.workspace-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 380px));
  gap: 16px;
  justify-content: start;
}

/* ── Page head (workspace list) ── */
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
}

.page-head-text h2 {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
  line-height: 1.2;
}

.page-head-text p {
  font-size: 13.5px;
  color: var(--text-muted);
  margin-top: 4px;
}

.create-ws-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 10px 20px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
  white-space: nowrap;
  font-family: inherit;
  flex-shrink: 0;
  box-shadow: 0 2px 12px rgba(10,11,13,0.18);
}
.create-ws-btn:hover  { opacity: 0.82; }
.create-ws-btn:active { transform: scale(0.97); }

/* ── Single workspace head ── */
.workspace-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--border);
}

.workspace-head-left {
  display: flex;
  flex-direction: column;
  gap: 14px;
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

.workspace-head-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ws-head-initial {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: #1c1c1e;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
  flex-shrink: 0;
  letter-spacing: -0.5px;
}

.workspace-head h2 {
  font-size: 24px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
}

.workspace-head p {
  color: var(--text-muted);
  margin-top: 4px;
  font-size: 13.5px;
  line-height: 1.5;
}

.workspace-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  align-items: center;
}


</style>
