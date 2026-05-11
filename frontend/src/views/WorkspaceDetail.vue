<template>
  <div class="workspace-detail">
    <div class="section-header">
      <h2>My Workspaces</h2>
      <button class="btn btn-primary btn-sm" @click="openCreateForm">+ New Workspace</button>
    </div>

    <div v-if="workspaceStore.loading" class="loading">Loading...</div>

    <template v-if="currentWorkspace">
      <div class="workspace-head">
        <div>
          <h2>{{ currentWorkspace.title }}</h2>
          <p v-if="currentWorkspace.description">{{ currentWorkspace.description }}</p>
        </div>
        <div class="workspace-actions">
          <button class="btn btn-sm" @click="editWorkspace">Edit</button>
          <button class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
      </div>
      <ProjectList :workspace-id="currentWorkspace.id" />
    </template>

    <template v-else-if="!workspaceStore.loading && !workspaceId">
      <div v-if="workspaceStore.workspaces.length === 0" class="empty">
        No workspaces yet. Create one to get started.
      </div>
      <div v-else class="workspace-grid">
        <WorkspaceCard
          v-for="ws in workspaceStore.workspaces"
          :key="ws.id"
          :workspace="ws"
        />
      </div>
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
