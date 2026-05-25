<template>
  <div class="workspace-detail">
    <!-- Workspace list view -->
    <template v-if="!workspaceId && !workspaceStore.loading">
      <div class="page-head">
        <div>
          <h2>Workspaces</h2>
          <p>Your execution layer — organise ongoing work into projects, tasks, and deadlines.</p>
        </div>
        <div class="page-actions">
          <button class="btn btn-primary" @click="openCreateForm">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
              <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            New Workspace
          </button>
        </div>
      </div>

      <!-- Explainer callout -->
      <div v-if="!dismissedExplainer" class="explainer-callout">
        <button class="explainer-dismiss" @click="dismissExplainer" title="Dismiss">×</button>
        <div class="explainer-body">
          <div class="explainer-col">
            <div class="explainer-icon explainer-icon--workspace">
              <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/>
              </svg>
            </div>
            <div>
              <p class="explainer-label">Workspace</p>
              <p class="explainer-text">A top-level container for a team, client, or area of work. Think of it as a folder that holds everything related to one big context.</p>
              <p class="explainer-example">e.g. "Freelance Clients", "TC4A Internship", "Side Projects"</p>
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
              <p class="explainer-text">A defined piece of work inside a workspace with its own kanban board. Use one project per deliverable or initiative.</p>
              <p class="explainer-example">e.g. "Website Redesign", "Q2 Marketing Campaign"</p>
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
              <p class="explainer-text">A single actionable item. Assign it, set a due date, add notes, and move it across statuses as work progresses.</p>
              <p class="explainer-example">e.g. "Write homepage copy", "Review pull request #14"</p>
            </div>
          </div>
        </div>
        <p class="explainer-tip">
          <svg viewBox="0 0 16 16" fill="none" width="13" height="13" style="flex-shrink:0">
            <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3"/>
            <path d="M8 7v4M8 5.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          <strong>Tip:</strong> Use <em>Plans</em> when you're figuring out <em>what</em> to do. Use <em>Workspaces</em> when you're tracking <em>how it's going</em>. A plan step can create a task directly in a workspace project.
        </p>
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
          <div>
            <h2>{{ currentWorkspace.title }}</h2>
            <p v-if="currentWorkspace.description">{{ currentWorkspace.description }}</p>
          </div>
        </div>
        <div class="workspace-actions">
          <button class="btn btn-sm" @click="editWorkspace">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M9.5 2.5l2 2L5 11H3v-2l6.5-6.5zM8.5 3.5l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
          <button class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
      </div>
      <ProjectList :workspace-id="currentWorkspace.id" />
    </template>

    <WorkspaceForm
      v-if="showForm"
      :workspace="editingWorkspace"
      @close="closeForm"
      @saved="onSave"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWorkspaceStore } from '../stores/workspaces'
import type { Workspace } from '../types'
import WorkspaceCard from '../components/workspace/WorkspaceCard.vue'
import WorkspaceForm from '../components/workspace/WorkspaceForm.vue'
import ProjectList from '../components/project/ProjectList.vue'
import Loading from '../components/common/Loading.vue'

const route = useRoute()
const router = useRouter()
const workspaceStore = useWorkspaceStore()

const dismissedExplainer = ref(localStorage.getItem('ws_explainer_dismissed') === '1')
function dismissExplainer() {
  dismissedExplainer.value = true
  localStorage.setItem('ws_explainer_dismissed', '1')
}

onMounted(() => workspaceStore.fetchAll())

const showForm = ref(false)
const editingWorkspace = ref<Workspace | null>(null)
const workspaceId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})
const currentWorkspace = computed(() => workspaceStore.current)

watch(workspaceId, async (id) => {
  if (id) {
    try {
      await workspaceStore.fetchOne(id)
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
    await workspaceStore.update(currentWorkspace.value.id, data)
  } else {
    const ws = await workspaceStore.create(data)
    router.push(`/workspaces/${ws.id}`)
  }
  closeForm()
}

async function handleDelete() {
  if (!currentWorkspace.value) return
  if (!confirm('Delete this workspace and all its projects and tasks?')) return
  await workspaceStore.remove(currentWorkspace.value.id)
  router.push('/')
}
</script>

<style scoped>
.workspace-detail {
  padding: 32px;
  max-width: 1200px;
}

/* Explainer */
.explainer-callout {
  position: relative;
  background: var(--primary-light);
  border: 1px solid var(--primary-border);
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
.explainer-dismiss:hover { color: var(--text); background: var(--primary-border); }

.explainer-body {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
}

.explainer-col {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex: 1;
  min-width: 200px;
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
.explainer-icon--workspace { background: #F0FDF4; border: 1px solid #BBF7D0; color: #15803D; }
.explainer-icon--project   { background: #EFF6FF; border: 1px solid #BFDBFE; color: #1D4ED8; }
.explainer-icon--task      { background: var(--primary-light); border: 1px solid var(--primary-border); color: var(--primary); }

.explainer-label {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.explainer-text {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.55;
  margin-bottom: 6px;
}

.explainer-example {
  font-size: 11.5px;
  color: var(--primary);
  font-style: italic;
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

.explainer-tip {
  display: flex;
  align-items: flex-start;
  gap: 7px;
  font-size: 11.5px;
  color: var(--text-muted);
  background: rgba(255,255,255,0.5);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  line-height: 1.55;
  border: 1px solid var(--primary-border);
  margin-top: 14px;
}
.explainer-tip svg { margin-top: 1px; color: var(--primary); }

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
  background: var(--primary-light);
  border: 1.5px solid var(--primary-border);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.workspace-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 28px;
  border-bottom: 1px solid var(--border);
}

.workspace-head-left {
  display: flex;
  align-items: center;
  gap: 14px;
}


.workspace-head h2 {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
}

.workspace-head p {
  color: var(--text-muted);
  margin-top: 4px;
  font-size: 14px;
}

.workspace-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  align-items: center;
}
</style>
