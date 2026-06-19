<template>
  <div class="projects-view">
    <div class="page-head">
      <div>
        <h2>Projects</h2>
        <p>All projects across your workspaces</p>
      </div>
      <div class="page-actions">
        <div class="search-bar" :class="{ focused: searchFocused }">
          <font-awesome-icon :icon="['fas', 'magnifying-glass']" class="search-icon" />
          <input
            v-model="search"
            class="search-input"
            placeholder="Search projects…"
            @focus="searchFocused = true"
            @blur="searchFocused = false"
          />
        </div>
      </div>
    </div>

    <!-- Filter pills -->
    <div class="filter-row">
      <button
        v-for="s in statusFilters"
        :key="s.value"
        class="filter-pill"
        :class="{ active: statusFilter === s.value }"
        @click="statusFilter = s.value"
      >{{ s.label }}</button>
    </div>

    <div v-if="projectStore.loading" class="projects-grid">
      <div v-for="i in 6" :key="i" class="project-card skeleton-card" />
    </div>

    <div v-else-if="filtered.length === 0" class="empty-state">
      <div class="empty-icon">
        <font-awesome-icon :icon="['fas', 'folder-open']" />
      </div>
      <h3>No projects found</h3>
      <p v-if="search || statusFilter">Try a different search or filter.</p>
      <p v-else>Create a workspace first, then add projects to it.</p>
      <button class="btn btn-primary" @click="$router.push('/workspaces')">
        <font-awesome-icon :icon="['fas', 'plus']" />
        Go to Workspaces
      </button>
    </div>

    <template v-else>
      <!-- Group by workspace -->
      <div v-for="group in grouped" :key="group.workspaceUuid" class="workspace-group">
        <div class="group-header" @click="toggleGroup(group.workspaceUuid)">
          <div class="group-header-left">
            <font-awesome-icon
              :icon="['fas', collapsed.has(group.workspaceUuid) ? 'chevron-right' : 'chevron-down']"
              class="group-chevron"
            />
            <span class="group-title">{{ group.workspaceTitle }}</span>
            <span class="group-count">{{ group.projects.length }}</span>
          </div>
          <button class="btn btn-sm" @click.stop="$router.push(`/workspaces/${group.workspaceUuid}`)">
            <font-awesome-icon :icon="['fas', 'arrow-up-right-from-square']" />
            Open
          </button>
        </div>

        <div v-if="!collapsed.has(group.workspaceUuid)" class="projects-grid">
          <div
            v-for="p in group.projects"
            :key="p.uuid"
            class="project-card"
            @click="$router.push(`/projects/${p.uuid}`)"
          >
            <div class="card-top">
              <div class="card-folder">
                <svg viewBox="0 0 20 20" fill="none" width="20" height="20">
                  <path d="M2 5.5A1.5 1.5 0 013.5 4h3.586a1 1 0 01.707.293L9.5 5.5H16.5A1.5 1.5 0 0118 7v8.5A1.5 1.5 0 0116.5 17h-13A1.5 1.5 0 012 15.5v-10z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="card-top-right">
                <span class="card-status-pill">
                  <span class="status-dot" :style="{ background: STATUS_COLORS[p.status] }"></span>
                  <span class="status-text" :style="{ color: STATUS_COLORS[p.status] }">{{ statusLabel(p.status) }}</span>
                </span>
                <span v-if="p.ai_summary" class="ai-badge">
                  <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" />
                  AI
                </span>
              </div>
            </div>
            <h3 class="card-title">{{ p.title }}</h3>
            <p class="card-desc">{{ p.description || 'No description added yet.' }}</p>
            <div class="card-meta">
              <span v-if="p.due_date" class="meta-item" :class="{ 'meta-overdue': isOverdue(p.due_date) }">
                <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                  <rect x="1" y="2" width="12" height="10.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                  <path d="M1 5.5h12M5 1v2.5M9 1v2.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                </svg>
                {{ formatDate(p.due_date) }}
              </span>
              <span v-else class="meta-item meta-nodate">
                <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                  <rect x="1" y="2" width="12" height="10.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
                  <path d="M1 5.5h12M5 1v2.5M9 1v2.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
                </svg>
                No due date
              </span>
              <span class="meta-updated">Updated {{ timeAgo(p.updated_at) }}</span>
            </div>
            <div class="card-divider"></div>
            <div class="card-stats">
              <div class="stat-progress">
                <svg viewBox="0 0 32 32" width="26" height="26" class="progress-ring">
                  <circle cx="16" cy="16" r="12" fill="none" stroke="var(--border)" stroke-width="3.5"/>
                  <circle
                    cx="16" cy="16" r="12" fill="none"
                    :stroke="ringColor(taskPct(p))"
                    stroke-width="3.5"
                    stroke-linecap="round"
                    :stroke-dasharray="`${taskPct(p) * 75.4 / 100} 75.4`"
                    transform="rotate(-90 16 16)"
                    style="transition: stroke-dasharray 0.4s ease"
                  />
                </svg>
                <span class="pct-text">{{ p.task_count > 0 ? taskPct(p) + '%' : '—' }}</span>
              </div>
              <div class="stat-tasks">
                <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
                  <path d="M2 4h12M2 8h8M2 12h10" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                </svg>
                <span>{{ p.completed_count }} / {{ p.task_count }} Tasks</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projects'
import type { ProjectStatus } from '../types'

const router = useRouter()
const projectStore = useProjectStore()

const search = ref('')
const searchFocused = ref(false)
const statusFilter = ref<string>('all')
const collapsed = ref(new Set<string>())

const statusFilters = [
  { value: 'all',       label: 'All' },
  { value: 'planning',  label: 'Planning' },
  { value: 'active',    label: 'Active' },
  { value: 'on_hold',   label: 'On Hold' },
  { value: 'completed', label: 'Completed' },
]

const STATUS_LABELS: Record<ProjectStatus, string> = {
  planning: 'Planning', active: 'Active', on_hold: 'On Hold',
  completed: 'Completed', archived: 'Archived',
}
function statusLabel(s: ProjectStatus) { return STATUS_LABELS[s] ?? s }

const STATUS_COLORS: Record<ProjectStatus, string> = {
  planning:  '#8B6FE8',
  active:    '#00BA7C',
  on_hold:   '#F59E0B',
  completed: '#3B82F6',
  archived:  '#8B98A5',
}

function taskPct(p: { task_count: number; completed_count: number }) {
  if (!p.task_count) return 0
  return Math.round((p.completed_count / p.task_count) * 100)
}

function ringColor(pct: number): string {
  if (pct === 100) return '#00BA7C'
  if (pct >= 60)  return '#3B82F6'
  if (pct >= 30)  return '#F59E0B'
  return '#EF4444'
}

function isOverdue(d: string) { return new Date(d) < new Date() }

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function timeAgo(iso: string) {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000
  if (diff < 60)  return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

function toggleGroup(uuid: string) {
  if (collapsed.value.has(uuid)) collapsed.value.delete(uuid)
  else collapsed.value.add(uuid)
}

const filtered = computed(() => {
  return projectStore.projects.filter((p) => {
    if (statusFilter.value !== 'all' && p.status !== statusFilter.value) return false
    if (search.value.trim()) {
      const q = search.value.toLowerCase()
      return p.title.toLowerCase().includes(q) || (p.description ?? '').toLowerCase().includes(q)
    }
    return true
  })
})

const grouped = computed(() => {
  const map = new Map<string, { workspaceUuid: string; workspaceTitle: string; projects: typeof filtered.value }>()
  for (const p of filtered.value) {
    const wsUuid = p.workspace_uuid ?? String(p.workspace_id)
    const wsTitle = p.workspace_title ?? 'Unknown Workspace'
    if (!map.has(wsUuid)) map.set(wsUuid, { workspaceUuid: wsUuid, workspaceTitle: wsTitle, projects: [] })
    map.get(wsUuid)!.projects.push(p)
  }
  return [...map.values()].sort((a, b) => a.workspaceTitle.localeCompare(b.workspaceTitle))
})

onMounted(() => projectStore.fetchAll())
</script>

<style scoped>
.projects-view {
  padding: 36px 40px 80px;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}
.page-head h2 {
  font-size: 26px; font-weight: 800; color: var(--text); letter-spacing: -0.6px;
}
.page-head p { font-size: 13.5px; color: var(--text-muted); margin-top: 3px; }

.search-bar {
  display: flex; align-items: center; gap: 8px;
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--radius-full); padding: 7px 14px;
  transition: border-color 0.15s, box-shadow 0.15s; width: 240px;
}
.search-bar.focused { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-muted); }
.search-icon { color: var(--text-light); font-size: 13px; flex-shrink: 0; }
.search-input { border: none; background: transparent; outline: none; font-size: 13.5px; color: var(--text); width: 100%; font-family: inherit; }
.search-input::placeholder { color: var(--text-light); }

/* Filter row */
.filter-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 28px; }
.filter-pill {
  padding: 5px 14px; border-radius: var(--radius-full);
  border: 1.5px solid var(--border); background: var(--surface);
  font-size: 12.5px; font-weight: 600; color: var(--text-muted);
  cursor: pointer; font-family: inherit; transition: all 0.12s;
}
.filter-pill:hover { border-color: var(--border-strong); color: var(--text); }
.filter-pill.active { background: var(--text); color: var(--surface); border-color: var(--text); }

/* Workspace groups */
.workspace-group { margin-bottom: 32px; }

.group-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 4px; cursor: pointer; margin-bottom: 14px;
  border-bottom: 1.5px solid var(--border);
}
.group-header-left { display: flex; align-items: center; gap: 8px; }
.group-chevron { font-size: 11px; color: var(--text-light); }
.group-title { font-size: 14px; font-weight: 700; color: var(--text); }
.group-count {
  font-size: 11px; font-weight: 600; color: var(--text-light);
  background: var(--bg); border: 1px solid var(--border);
  padding: 1px 8px; border-radius: var(--radius-full);
}

/* Project cards grid */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.project-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px 22px 18px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s, transform 0.18s;
  box-shadow: 0 4px 16px rgba(10,11,13,0.08), 0 1px 4px rgba(10,11,13,0.04);
}
.project-card:hover {
  box-shadow: 0 16px 48px rgba(10,11,13,0.16), 0 4px 12px rgba(10,11,13,0.08);
  transform: translateY(-4px);
}

.skeleton-card {
  height: 180px;
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  cursor: default;
}
@keyframes shimmer { to { background-position: -200% 0; } }

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.card-folder {
  color: var(--text-light);
  display: flex;
  align-items: center;
}
.card-top-right {
  display: flex;
  align-items: center;
  gap: 6px;
}
.card-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-text {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1px;
}

.ai-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10.5px; font-weight: 700; color: var(--primary);
  background: var(--primary-light); border: 1px solid var(--primary-border);
  padding: 2px 7px; border-radius: var(--radius-full);
}

.card-title {
  font-size: 16.5px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
  line-height: 1.25;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 14px;
  flex: 1;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}
.meta-overdue { color: var(--danger); }
.meta-nodate { color: var(--text-light); }
.meta-updated {
  font-size: 11.5px;
  color: var(--text-light);
  white-space: nowrap;
}

.card-divider {
  height: 1px;
  background: var(--border);
  margin-bottom: 14px;
}

.card-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-progress {
  display: flex;
  align-items: center;
  gap: 6px;
}
.progress-ring { flex-shrink: 0; }
.pct-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}
.stat-tasks {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-muted);
}

/* Empty state */
.empty-state {
  text-align: center; padding: 80px 20px;
  display: flex; flex-direction: column; align-items: center; gap: 14px;
}
.empty-icon {
  width: 56px; height: 56px; background: var(--bg); border: 1.5px solid var(--border);
  border-radius: 16px; display: flex; align-items: center; justify-content: center;
  font-size: 22px; color: var(--text-light);
}
.empty-state h3 { font-size: 18px; font-weight: 700; color: var(--text); }
.empty-state p  { font-size: 14px; color: var(--text-muted); max-width: 320px; }

/* Dark mode */
:global([data-theme="dark"]) .filter-pill.active { background: #F7F9F9 !important; color: #15202B !important; border-color: #F7F9F9 !important; }
:global([data-theme="dark"]) .project-card {
  background: rgba(30,39,50,0.95);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3), 0 1px 4px rgba(0,0,0,0.2);
}
:global([data-theme="dark"]) .project-card:hover {
  box-shadow: 0 16px 48px rgba(0,0,0,0.5), 0 4px 12px rgba(0,0,0,0.3);
}
</style>
