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
              <span class="status-chip" :class="`chip-${p.status}`">{{ statusLabel(p.status) }}</span>
              <span v-if="p.ai_summary" class="ai-badge">
                <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" />
                AI
              </span>
            </div>
            <h3 class="card-title">{{ p.title }}</h3>
            <p v-if="p.description" class="card-desc">{{ p.description }}</p>
            <div class="card-footer">
              <span v-if="p.due_date" class="card-meta">
                <font-awesome-icon :icon="['far', 'calendar']" />
                {{ formatDate(p.due_date) }}
              </span>
              <span class="card-meta">
                <font-awesome-icon :icon="['fas', 'list-check']" />
                Updated {{ timeAgo(p.updated_at) }}
              </span>
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
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--radius-lg); padding: 18px 20px;
  cursor: pointer; transition: border-color 0.14s, box-shadow 0.14s, transform 0.12s;
  display: flex; flex-direction: column; gap: 8px;
}
.project-card:hover {
  border-color: var(--border-strong);
  box-shadow: 0 4px 16px rgba(10,11,13,0.08);
  transform: translateY(-1px);
}

.skeleton-card {
  height: 130px;
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  cursor: default;
}
@keyframes shimmer { to { background-position: -200% 0; } }

.card-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; }

.status-chip {
  font-size: 11px; font-weight: 700; padding: 2px 9px;
  border-radius: var(--radius-full); letter-spacing: 0.1px;
}
.chip-planning  { background: rgba(168,160,248,0.18); color: #5248C8; }
.chip-active    { background: rgba(0,186,124,0.14);   color: #00845A; }
.chip-on_hold   { background: rgba(255,179,0,0.16);   color: #A87800; }
.chip-completed { background: rgba(104,204,128,0.18); color: #1A5820; }
.chip-archived  { background: rgba(139,152,165,0.15); color: #536471; }

.ai-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10.5px; font-weight: 700; color: var(--primary);
  background: var(--primary-light); border: 1px solid var(--primary-border);
  padding: 2px 7px; border-radius: var(--radius-full);
}

.card-title {
  font-size: 15px; font-weight: 700; color: var(--text);
  letter-spacing: -0.3px; line-height: 1.3;
}
.card-desc {
  font-size: 12.5px; color: var(--text-muted); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-footer { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 4px; }
.card-meta {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 11.5px; color: var(--text-light); font-weight: 500;
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
:global([data-theme="dark"]) .chip-planning  { background: rgba(168,160,248,0.22) !important; color: #A8A0F8 !important; }
:global([data-theme="dark"]) .chip-active    { background: rgba(0,186,124,0.2) !important;    color: #00BA7C !important; }
:global([data-theme="dark"]) .chip-on_hold   { background: rgba(255,179,0,0.2) !important;    color: #FFB300 !important; }
:global([data-theme="dark"]) .chip-completed { background: rgba(104,204,128,0.22) !important; color: #68CC80 !important; }
:global([data-theme="dark"]) .chip-archived  { background: rgba(139,152,165,0.18) !important; color: #8B98A5 !important; }
</style>
