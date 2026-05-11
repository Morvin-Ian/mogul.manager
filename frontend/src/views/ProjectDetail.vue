<template>
  <div class="project-detail">
    <div v-if="projectStore.loading" class="loading">Loading...</div>

    <template v-if="project">
      <div class="page-head">
        <div>
          <h2>{{ project.title }}</h2>
          <p v-if="project.description">{{ project.description }}</p>
        </div>
        <div class="page-actions">
          <button class="btn btn-sm" @click="editProject">Edit</button>
          <button class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
      </div>

      <div class="project-meta">
        <span class="badge" :class="`badge-${project.status}`">{{ project.status }}</span>
        <span v-if="project.due_date">Due: {{ formatDate(project.due_date) }}</span>
        <span v-if="project.ai_summary" class="ai-summary">AI: {{ project.ai_summary }}</span>
      </div>

      <TaskBoard :project-id="project.id" />

      <ProjectForm
        v-if="showForm"
        :project="editingProject"
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
import type { Project } from '../types'
import TaskBoard from '../components/task/TaskBoard.vue'
import ProjectForm from '../components/project/ProjectForm.vue'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const showForm = ref(false)
const editingProject = ref<Project | null>(null)
const projectId = computed(() => Number(route.params.id))
const project = computed(() => projectStore.current)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString()
}

watch(projectId, async (id) => {
  if (id) {
    try {
      await projectStore.fetchOne(id)
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
  if (!confirm('Delete this project and all its tasks?')) return
  const wsId = project.value.workspace_id
  await projectStore.remove(projectId.value)
  router.push(`/workspaces/${wsId}`)
}
</script>
