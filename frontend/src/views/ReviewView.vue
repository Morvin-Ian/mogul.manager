<template>
  <div class="review-page">
    <div class="review-head">
      <div>
        <h2 class="review-title">Review</h2>
        <p class="review-sub">Tasks awaiting review{{ isAdminOrOwner ? ' across your workspace' : ' assigned to you' }}</p>
      </div>
      <select
        v-if="workspaceStore.workspaces.length > 1"
        v-model="selectedWorkspaceId"
        class="ws-select"
      >
        <option v-for="ws in workspaceStore.workspaces" :key="ws.id" :value="ws.id">
          {{ ws.title }}
        </option>
      </select>
    </div>

    <!-- Stats -->
    <div class="review-stats">
      <div class="stat-card">
        <span class="stat-num">{{ visibleTasks.length }}</span>
        <span class="stat-label">In Review</span>
      </div>
<div class="stat-card">
        <span class="stat-num">{{ uniqueAssignees }}</span>
        <span class="stat-label">{{ isAdminOrOwner ? 'Assignees' : 'Your tasks' }}</span>
      </div>
    </div>

    <!-- Skeleton grid while loading -->
    <div v-if="loading" class="review-grid">
      <div v-for="n in 6" :key="n" class="review-card sk-card">
        <div class="rc-head">
          <div class="sk sk-chip"></div>
          <div class="sk-assignee-row">
            <div class="sk sk-avatar-sm"></div>
            <div class="sk sk-name"></div>
          </div>
        </div>
        <div class="sk sk-title-line"></div>
        <div class="sk sk-body-line"></div>
        <div class="sk sk-body-line sk-body-short"></div>
        <div class="sk-footer-row">
          <div class="sk sk-footer-chip"></div>
          <div class="sk sk-footer-chip"></div>
        </div>
      </div>
    </div>

    <div v-else-if="visibleTasks.length === 0" class="review-empty">
      <div class="empty-icon-wrap">
        <font-awesome-icon :icon="['fas', 'circle-check']" />
      </div>
      <p>No tasks in review</p>
      <span>Tasks moved to the Review column will appear here</span>
    </div>

    <div v-else class="review-grid">
      <div
        v-for="task in visibleTasks"
        :key="task.id"
        class="review-card"
        @click="selectedTask = task"
      >
        <div class="rc-head">
          <span class="rc-priority" :class="`rcp-${task.priority}`">{{ priorityLabel(task.priority) }}</span>
          <div v-if="task.assignee_name" class="rc-assignee">
            <div class="rc-avatar" :style="task.assignee_avatar_url ? {} : { background: gradient(task.assignee_name) }">
              <img v-if="task.assignee_avatar_url" :src="task.assignee_avatar_url" :alt="task.assignee_name" class="rc-avatar-img" />
              <span v-else>{{ task.assigned_to_id === auth.user?.id ? 'Me' : task.assignee_name.charAt(0).toUpperCase() }}</span>
            </div>
            <span>{{ task.assigned_to_id === auth.user?.id ? 'You' : task.assignee_name }}</span>
          </div>
          <span v-else class="rc-unassigned">Unassigned</span>
        </div>

        <p class="rc-title">{{ task.title }}</p>

        <p class="rc-project">
          <font-awesome-icon :icon="['fas', 'folder-open']" />
          {{ projectName(task.project_id) }}
        </p>

        <!-- Review links -->
        <div v-if="reviewLinks(task).length" class="rc-links">
          <a
            v-for="link in reviewLinks(task)"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="rc-link"
            :class="`rcl-${link.type}`"
            @click.stop
          >
            <font-awesome-icon :icon="linkIcon(link.type)" />
            <span class="rc-link-text">{{ link.label || shortenUrl(link.url) }}</span>
          </a>
        </div>
        <p v-else class="rc-no-links">
          <font-awesome-icon :icon="['fas', 'link-slash']" />
          No links submitted
        </p>

        <div class="rc-footer">
          <span v-if="task.due_date" class="rc-due" :class="{ 'rc-due--overdue': isOverdue(task.due_date) }">
            <font-awesome-icon :icon="['fas', 'calendar']" />
            {{ formatDate(task.due_date) }}
          </span>
          <span v-else class="rc-no-date">No due date</span>
          <span class="rc-updated">Updated {{ timeAgo(task.updated_at) }}</span>
        </div>
      </div>
    </div>

    <TaskDrawer
      v-if="selectedTask"
      :task="selectedTask"
      :workspace-id="selectedWorkspaceId"
      :project-id="selectedTask.project_id"
      @close="selectedTask = null"
      @deleted="selectedTask = null; loadTasks()"
      @updated="onTaskUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import AiNudge from '../components/common/AiNudge.vue'
import { useWorkspaceStore } from '../stores/workspaces'
import { useProjectStore } from '../stores/projects'
import { useTaskStore } from '../stores/tasks'
import { useMembersStore } from '../stores/members'
import { useAuthStore } from '../stores/auth'
import type { Task } from '../types'
import TaskDrawer from '../components/task/TaskDrawer.vue'

interface ReviewLink { url: string; label: string; type: string }

const workspaceStore = useWorkspaceStore()
const projectStore = useProjectStore()
const taskStore = useTaskStore()
const membersStore = useMembersStore()
const auth = useAuthStore()

const loading = ref(false)
const allTasks = ref<Task[]>([])
const selectedTask = ref<Task | null>(null)
const selectedWorkspaceId = ref<number | null>(null)

const isAdminOrOwner = computed(() => {
  const role = membersStore.myMembership?.role
  return role === 'admin' || role === 'owner'
})

const visibleTasks = computed(() =>
  isAdminOrOwner.value
    ? allTasks.value
    : allTasks.value.filter(t => t.assigned_to_id === auth.user?.id)
)

const uniqueAssignees = computed(() =>
  isAdminOrOwner.value
    ? new Set(visibleTasks.value.map(t => t.assigned_to_id).filter(Boolean)).size
    : visibleTasks.value.length
)

function reviewLinks(task: Task): ReviewLink[] {
  const meta = task.metadata_json as Record<string, any> | null
  return (meta?.review_links as ReviewLink[]) ?? []
}

function projectName(id: number): string {
  return projectStore.projects.find(p => p.id === id)?.title ?? 'Unknown project'
}

function linkIcon(type: string): string[] {
  if (type === 'repo') return ['fas', 'code-branch']
  if (type === 'doc') return ['fas', 'file-lines']
  if (type === 'design') return ['fas', 'pen-ruler']
  return ['fas', 'link']
}

function shortenUrl(url: string): string {
  try { return new URL(url).hostname.replace('www.', '') } catch { return url }
}

function priorityLabel(p: number): string {
  return ({ 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' } as Record<number, string>)[p] ?? ''
}

function isOverdue(d: string) { return new Date(d) < new Date() }

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function timeAgo(d: string) {
  const diff = Math.floor((Date.now() - new Date(d).getTime()) / 60000)
  if (diff < 1) return 'just now'
  if (diff < 60) return `${diff}m ago`
  if (diff < 1440) return `${Math.floor(diff / 60)}h ago`
  return `${Math.floor(diff / 1440)}d ago`
}

const GRADIENTS = [
  'linear-gradient(135deg,#6366F1,#8B5CF6)',
  'linear-gradient(135deg,#0EA5E9,#2563EB)',
  'linear-gradient(135deg,#10B981,#059669)',
  'linear-gradient(135deg,#F59E0B,#D97706)',
  'linear-gradient(135deg,#EF4444,#DC2626)',
  'linear-gradient(135deg,#0D9488,#0891B2)',
]
function gradient(name: string): string {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) & 0xffffffff
  return GRADIENTS[Math.abs(h) % GRADIENTS.length]
}

async function loadTasks() {
  if (!selectedWorkspaceId.value) return
  loading.value = true
  try {
    await Promise.all([
      projectStore.fetchByWorkspace(selectedWorkspaceId.value),
      membersStore.fetchMyMembership(selectedWorkspaceId.value),
    ])
    allTasks.value = await taskStore.fetchReviewTasks(selectedWorkspaceId.value)
  } finally {
    loading.value = false
  }
}

function onTaskUpdated(updated: Task) {
  const idx = allTasks.value.findIndex(t => t.id === updated.id)
  if (idx !== -1) {
    if (updated.status !== 'review') allTasks.value.splice(idx, 1)
    else allTasks.value[idx] = updated
  }
  if (selectedTask.value?.id === updated.id) {
    selectedTask.value = updated.status === 'review' ? updated : null
  }
}

watch(selectedWorkspaceId, loadTasks)

onMounted(async () => {
  if (workspaceStore.workspaces.length === 0) {
    await workspaceStore.fetchAll()
  }
  if (workspaceStore.workspaces.length > 0) {
    selectedWorkspaceId.value = workspaceStore.workspaces[0].id
  }
})
</script>

<style scoped>
.review-page {
  padding: 36px 40px 80px;
}

.review-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.review-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
}

.review-sub {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 3px;
}

.ws-select {
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 13px;
  font-family: inherit;
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
  outline: none;
  flex-shrink: 0;
}

/* ── Stats ── */
.review-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
}

.stat-card {
  flex: 1;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-num {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -1px;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

/* ── Skeleton ── */
@keyframes sk-shimmer { 0%{background-position:-600px 0} 100%{background-position:600px 0} }
.sk {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 600px 100%;
  animation: sk-shimmer 1.5s ease-in-out infinite;
  border-radius: 4px;
  flex-shrink: 0;
}
.sk-card { cursor: default; pointer-events: none; gap: 10px; display: flex; flex-direction: column; }
.sk-chip         { height: 20px; width: 60px; border-radius: 99px; }
.sk-assignee-row { display: flex; align-items: center; gap: 6px; }
.sk-avatar-sm    { width: 24px; height: 24px; border-radius: 50%; }
.sk-name         { height: 12px; width: 70px; }
.sk-title-line   { height: 16px; width: 85%; margin-top: 4px; }
.sk-body-line    { height: 12px; width: 100%; }
.sk-body-short   { width: 65%; }
.sk-footer-row   { display: flex; gap: 6px; margin-top: 4px; }
.sk-footer-chip  { height: 18px; width: 72px; border-radius: 99px; }

.review-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 64px 20px;
  text-align: center;
}

.empty-icon-wrap {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: #1c1c1e;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: 0 4px 16px rgba(10,11,13,0.2);
}

.review-empty p {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  margin: 0;
}

.review-empty span {
  font-size: 13px;
  color: var(--text-muted);
}

/* ── Grid ── */
.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

/* ── Card ── */
.review-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 16px;
  padding: 18px 18px 14px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: box-shadow 0.18s, transform 0.16s, border-color 0.15s;
}

.review-card:hover {
  box-shadow: 0 10px 36px rgba(10,11,13,0.11), 0 2px 8px rgba(10,11,13,0.07);
  transform: translateY(-3px);
  border-color: var(--border-strong);
}

:global([data-theme="dark"]) .review-card {
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
:global([data-theme="dark"]) .review-card:hover {
  box-shadow: 0 10px 36px rgba(0,0,0,0.45);
}

.rc-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rc-priority {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 4px;
  flex-shrink: 0;
}
.rcp-1 { background: #DCFCE7; color: #16A34A; }
.rcp-2 { background: #FEF3C7; color: #D97706; }
.rcp-3 { background: #FEE2E2; color: #DC2626; }
.rcp-4 { background: #FEE2E2; color: #991B1B; }
:global([data-theme="dark"]) .rcp-1 { background: rgba(22,163,74,0.2); color: #4ADE80; }
:global([data-theme="dark"]) .rcp-2 { background: rgba(217,119,6,0.2); color: #FBB040; }
:global([data-theme="dark"]) .rcp-3 { background: rgba(220,38,38,0.2); color: #F87171; }
:global([data-theme="dark"]) .rcp-4 { background: rgba(153,27,27,0.2); color: #FCA5A5; }

.rc-assignee {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.rc-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  color: #fff;
  font-size: 9px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}
.rc-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }

.rc-unassigned {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-light);
}

.rc-title {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
  line-height: 1.4;
}

.rc-project {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

/* ── Review links ── */
.rc-links {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rc-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 11px;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
  text-decoration: none;
  border: 1.5px solid transparent;
  transition: opacity 0.12s, transform 0.1s;
  overflow: hidden;
}
.rc-link:hover { opacity: 0.82; transform: translateX(2px); }

.rc-link-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rcl-repo   { background: #F0FDF4; color: #16A34A; border-color: #BBF7D0; }
.rcl-doc    { background: #EFF6FF; color: #2563EB; border-color: #BFDBFE; }
.rcl-design { background: #FDF4FF; color: #9333EA; border-color: #E9D5FF; }
.rcl-link   { background: #F8FAFC; color: #475569; border-color: #E2E8F0; }

:global([data-theme="dark"]) .rcl-repo   { background: rgba(22,163,74,0.15); color: #4ADE80; border-color: rgba(22,163,74,0.3); }
:global([data-theme="dark"]) .rcl-doc    { background: rgba(37,99,235,0.15); color: #60A5FA; border-color: rgba(37,99,235,0.3); }
:global([data-theme="dark"]) .rcl-design { background: rgba(147,51,234,0.15); color: #C084FC; border-color: rgba(147,51,234,0.3); }
:global([data-theme="dark"]) .rcl-link   { background: rgba(255,255,255,0.07); color: #8B98A5; border-color: rgba(255,255,255,0.1); }

.rc-no-links {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-light);
  font-style: italic;
}

/* ── Card footer ── */
.rc-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
  margin-top: 2px;
}

.rc-due {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-muted);
}
.rc-due--overdue { color: var(--danger); }
.rc-no-date { font-size: 11.5px; color: var(--text-light); }
.rc-updated { font-size: 11px; color: var(--text-light); white-space: nowrap; }
</style>
