<template>
  <div class="project-list">
    <div class="section-header">
      <h2>Projects</h2>
      <button class="btn btn-sm btn-primary" @click="showForm = true">+ New Project</button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="projects.length === 0" class="empty">No projects yet.</div>
    <div v-else class="project-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="card project-card"
        @click="$router.push(`/projects/${project.id}`)"
      >
        <h3>{{ project.title }}</h3>
        <p v-if="project.description" class="card-desc">{{ project.description }}</p>
        <div class="card-meta">
          <span class="badge" :class="`badge-${project.status}`">{{ project.status }}</span>
          <span v-if="project.due_date" class="date">Due {{ formatDate(project.due_date) }}</span>
        </div>
      </div>
    </div>
    <ProjectForm
      v-if="showForm"
      @close="showForm = false"
      @saved="onProjectSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useProjectStore } from '../../stores/projects'
import ProjectForm from './ProjectForm.vue'

const props = defineProps<{
  workspaceId: number
}>()

const projectStore = useProjectStore()
const showForm = ref(false)
const loading = ref(false)
const projects = computed(() => projectStore.projects)

async function loadProjects() {
  loading.value = true
  await projectStore.fetchByWorkspace(props.workspaceId)
  loading.value = false
}

onMounted(loadProjects)

watch(() => props.workspaceId, loadProjects)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString()
}

async function onProjectSaved(data: Record<string, any>) {
  await projectStore.create({ ...data, workspace_id: props.workspaceId } as any)
  showForm.value = false
}
</script>

<style scoped>
.project-list {
  margin-top: 8px;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 14px;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s, transform 0.15s;
}

.card:hover {
  box-shadow: var(--shadow);
  border-color: var(--border-strong);
  transform: translateY(-2px);
}

.card h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--text);
  letter-spacing: -0.2px;
}

.card-desc {
  color: var(--text-muted);
  font-size: 13px;
  margin-bottom: 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
