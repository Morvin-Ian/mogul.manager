<template>
  <div class="project-detail">
    <Loading v-if="projectStore.loading" label="Loading project…" />

    <template v-if="project">
      <div class="page-head">
        <div class="page-head-left">
          <button class="back-btn" @click="$router.back()">
            <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
              <path d="M10 13L5 8l5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Back
          </button>
          <div>
            <div class="project-title-row">
              <h2>{{ project.title }}</h2>
              <span class="badge" :class="`badge-${project.status}`">{{ project.status.replace('_', ' ') }}</span>
            </div>
            <p v-if="project.description">{{ project.description }}</p>
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
                AI: {{ project.ai_summary }}
              </span>
            </div>
          </div>
        </div>
        <div class="page-actions">
          <button class="btn btn-sm" @click="editProject">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M9.5 2.5l2 2L5 11H3v-2l6.5-6.5zM8.5 3.5l2 2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Edit
          </button>
          <button class="btn btn-sm btn-danger" @click="handleDelete">Delete</button>
        </div>
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
import Loading from '../components/common/Loading.vue'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const showForm = ref(false)
const editingProject = ref<Project | null>(null)
const projectId = computed(() => Number(route.params.id))
const project = computed(() => projectStore.current)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
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

<style scoped>
.project-detail {
  padding: 28px 32px;
  max-width: 1400px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 16px;
}

.page-head-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
  transition: color 0.1s;
}

.back-btn:hover { color: var(--text); }

.project-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 5px;
}

.project-title-row h2 {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
}

.page-head p {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
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
  border: 1px solid var(--border);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-weight: 500;
}

.ai-chip { color: var(--primary); background: var(--primary-light); border-color: var(--primary-border); font-style: italic; }
</style>
