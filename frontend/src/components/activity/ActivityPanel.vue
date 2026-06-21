<template>
  <div class="activity-panel">
    <div v-if="store.loading" class="ap-loading">Loading activity…</div>

    <div v-else-if="store.entries.length === 0" class="ap-empty">
      <div class="ap-empty-icon">
        <font-awesome-icon :icon="['fas', 'clock-rotate-left']" />
      </div>
      <p class="ap-empty-title">No activity yet</p>
      <p class="ap-empty-sub">Actions taken in this project will appear here.</p>
    </div>

    <div v-else class="ap-feed">
      <div v-for="entry in store.entries" :key="entry.id" class="ap-item">
        <div class="ap-avatar" :style="entry.user?.profile_path ? {} : { background: memberGradient(entry.user?.username || '?') }">
          <img v-if="entry.user?.profile_path" :src="entry.user.profile_path" :alt="entry.user?.username" class="ap-avatar-img" />
          <span v-else>{{ (entry.user?.username || '?').charAt(0).toUpperCase() }}</span>
        </div>
        <div class="ap-body">
          <div class="ap-meta">
            <span class="ap-username">{{ entry.user?.username || 'Unknown' }}</span>
            <span class="ap-time">{{ timeAgo(entry.created_at) }}</span>
          </div>
          <p class="ap-summary">{{ entry.summary || `${entry.action} ${entry.entity_type}` }}</p>
        </div>
        <div class="ap-action-badge" :class="`aab-${entry.action}`">
          {{ actionLabel(entry.action) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useActivityStore } from '../../stores/activity'

const props = defineProps<{ projectId: number }>()

const store = useActivityStore()

const GRADIENTS = [
  'linear-gradient(135deg,#6366F1,#8B5CF6)',
  'linear-gradient(135deg,#0EA5E9,#2563EB)',
  'linear-gradient(135deg,#10B981,#059669)',
  'linear-gradient(135deg,#F59E0B,#D97706)',
  'linear-gradient(135deg,#EF4444,#DC2626)',
  'linear-gradient(135deg,#0D9488,#0891B2)',
]

function memberGradient(name: string): string {
  let h = 0
  for (const c of name) h = (h * 31 + c.charCodeAt(0)) & 0xffffffff
  return GRADIENTS[Math.abs(h) % GRADIENTS.length]
}

function timeAgo(date: string): string {
  const seconds = Math.floor((Date.now() - new Date(date).getTime()) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  return new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const ACTION_LABELS: Record<string, string> = {
  created: 'Created',
  updated: 'Updated',
  deleted: 'Deleted',
  dependency_added: 'Linked',
  dependency_removed: 'Unlinked',
  member_added: 'Added',
  member_removed: 'Removed',
  status_changed: 'Moved',
  assigned: 'Assigned',
}
function actionLabel(a: string): string {
  return ACTION_LABELS[a] || a.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

onMounted(() => { store.fetchByProject(props.projectId) })
onUnmounted(() => { store.clear() })
</script>

<style scoped>
.activity-panel {
  padding-top: 24px;
}

.ap-loading {
  text-align: center;
  padding: 40px;
  color: var(--text-light);
  font-size: 13px;
}

.ap-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 50px 20px;
  text-align: center;
}

.ap-empty-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--text-light);
}

.ap-empty-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.ap-empty-sub {
  font-size: 13px;
  color: var(--text-muted);
  max-width: 300px;
  line-height: 1.5;
}

.ap-feed {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.ap-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  transition: background 0.1s;
}

.ap-item:hover {
  background: var(--bg);
}

.ap-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
  overflow: hidden;
  margin-top: 2px;
}

.ap-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ap-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ap-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ap-username {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

.ap-time {
  font-size: 11px;
  color: var(--text-light);
}

.ap-summary {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.5;
}

.ap-action-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  flex-shrink: 0;
  margin-top: 3px;
}

.aab-created          { background: #ECFDF5; color: #065F46; }
.aab-updated          { background: #EFF6FF; color: #1D4ED8; }
.aab-deleted          { background: #FFF1F2; color: #B91C1C; }
.aab-linked,
.aab-dependency_added { background: #F5F3FF; color: #6D28D9; }
.aab-unlinked,
.aab-dependency_removed { background: #FFF1F2; color: #B91C1C; }
.aab-member_added     { background: #ECFDF5; color: #065F46; }
.aab-member_removed   { background: #FFF1F2; color: #B91C1C; }
.aab-moved,
.aab-status_changed   { background: #FFFBEB; color: #92400E; }
.aab-assigned         { background: #EFF6FF; color: #1D4ED8; }

:global([data-theme="dark"]) .ap-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

:global([data-theme="dark"]) .ap-empty-icon {
  background: #253341;
  border-color: #38444D;
}

:global([data-theme="dark"]) .aab-created { background: rgba(0,186,124,0.15); color: #00BA7C; }
:global([data-theme="dark"]) .aab-updated { background: rgba(91,155,255,0.15); color: #5B9BFF; }
:global([data-theme="dark"]) .aab-deleted { background: rgba(255,107,120,0.15); color: #FF6B78; }
:global([data-theme="dark"]) .aab-linked,
:global([data-theme="dark"]) .aab-dependency_added { background: rgba(139,92,246,0.15); color: #A78BFA; }
:global([data-theme="dark"]) .aab-unlinked,
:global([data-theme="dark"]) .aab-dependency_removed { background: rgba(255,107,120,0.15); color: #FF6B78; }
:global([data-theme="dark"]) .aab-member_added { background: rgba(0,186,124,0.15); color: #00BA7C; }
:global([data-theme="dark"]) .aab-member_removed { background: rgba(255,107,120,0.15); color: #FF6B78; }
:global([data-theme="dark"]) .aab-moved,
:global([data-theme="dark"]) .aab-status_changed { background: rgba(255,179,0,0.15); color: #FFB300; }
:global([data-theme="dark"]) .aab-assigned { background: rgba(91,155,255,0.15); color: #5B9BFF; }
</style>
