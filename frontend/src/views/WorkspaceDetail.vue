<template>
  <div class="workspace-detail">
    <!-- Workspace list view -->
    <template v-if="!workspaceId && !workspaceStore.loading">
      <div class="page-head">
        <div>
          <h2>Workspaces</h2>
          <p>Organize your projects and tasks into focused workspaces.</p>
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
import { computed, ref, watch } from 'vue'
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
  padding: 28px 32px;
  max-width: 1200px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 80px 20px;
  text-align: center;
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
  gap: 14px;
}

.workspace-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
  padding-bottom: 24px;
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
