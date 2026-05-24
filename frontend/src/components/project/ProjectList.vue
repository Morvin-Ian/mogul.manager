<template>
  <div class="project-list">
    <div class="section-header">
      <h2>Projects</h2>
      <button class="btn btn-sm btn-primary" @click="showForm = true">
        <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        New Project
      </button>
    </div>
    <div v-if="loading" class="sk-grid">
      <SkeletonCard v-for="n in 4" :key="n" />
    </div>
    <div v-else-if="projects.length === 0" class="empty-projects">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="3" y="3" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
          <rect x="13" y="3" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
          <rect x="3" y="13" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
          <rect x="13" y="13" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.5"/>
        </svg>
      </div>
      <p>No projects yet. Create your first project to get started.</p>
      <button class="btn btn-primary btn-sm" @click="showForm = true">Create project</button>
    </div>
    <div v-else class="project-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="$router.push(`/projects/${project.id}`)"
      >
        <div class="project-card-top">
          <span class="badge" :class="`badge-${project.status}`">{{ project.status.replace('_', ' ') }}</span>
        </div>
        <h3>{{ project.title }}</h3>
        <p v-if="project.description" class="card-desc">{{ project.description }}</p>
        <div class="project-card-footer">
          <span v-if="project.due_date" class="due-date">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <rect x="1.5" y="2.5" width="11" height="10" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
              <path d="M1.5 6h11M5 1v3M9 1v3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
            </svg>
            Due {{ formatDate(project.due_date) }}
          </span>
          <span v-else class="date">No due date</span>
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
import SkeletonCard from '../common/SkeletonCard.vue'

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
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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

.sk-grid,
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 16px;
}

.empty-projects {
  text-align: center;
  padding: 64px 20px;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  width: 52px;
  height: 52px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-light);
}

.empty-icon svg { width: 24px; height: 24px; }

.empty-projects p {
  font-size: 14px;
  max-width: 260px;
  line-height: 1.5;
}

.project-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 22px 18px;
  cursor: pointer;
  transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.project-card:hover {
  box-shadow: var(--shadow);
  border-color: var(--primary-border);
  transform: translateY(-2px);
}

.project-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

h3 {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
  line-height: 1.35;
}

.card-desc {
  color: var(--text-muted);
  font-size: 13px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.project-card-footer {
  margin-top: 2px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.due-date {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.date {
  font-size: 12px;
  color: var(--text-light);
}
</style>
