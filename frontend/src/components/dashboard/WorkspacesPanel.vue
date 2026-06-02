<template>
  <div class="panel">
    <div class="panel-hdr">
      <span class="panel-title">Workspaces</span>
      <button class="create-new-btn" @click="$emit('create')">
        <svg viewBox="0 0 16 16" fill="none" width="11" height="11">
          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        Create new
      </button>
    </div>

    <div v-if="workspaces.length === 0" class="ws-empty-state">
      <svg viewBox="0 0 48 48" fill="none" width="36" height="36">
        <rect x="8" y="6" width="32" height="36" rx="4" stroke="#C8C5DC" stroke-width="2"/>
        <path d="M8 18h32M18 6v8M30 6v8" stroke="#C8C5DC" stroke-width="2" stroke-linecap="round"/>
        <path d="M18 28h12M18 33h8" stroke="#C8C5DC" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <p>No workspaces yet</p>
      <button class="create-new-btn" @click="$emit('create')">Get started</button>
    </div>

    <div v-else class="ws-grid">
      <div
        v-for="(ws, idx) in workspaces"
        :key="ws.id"
        class="ws-card"
        :style="{
          background: palette(idx).bg,
          borderColor: palette(idx).border,
        }"
        @click="$router.push(`/workspaces/${ws.uuid}`)"
      >
        <div class="ws-card-top">
          <span class="ws-card-count" :style="{ color: palette(idx).accent }">
            {{ wsProjectCount(ws.id) }} project{{ wsProjectCount(ws.id) !== 1 ? 's' : '' }}
          </span>
          <div class="ws-menu-wrap">
            <button
              class="ws-card-menu"
              :style="{ color: palette(idx).accent }"
              @click.stop="wsMenuOpenId = wsMenuOpenId === ws.id ? null : ws.id"
            >⋯</button>
            <div v-if="wsMenuOpenId === ws.id" class="ws-dropdown">
              <button class="ws-dd-item" @click.stop="handleEdit(ws)">
                <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
                  <path d="M11.5 2.5a2.121 2.121 0 013 3L5 15H2v-3L11.5 2.5z" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Edit
              </button>
              <button class="ws-dd-item ws-dd-danger" @click.stop="handleDelete(ws.id)">
                <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
                  <path d="M2 4h12M5 4V3a1 1 0 011-1h4a1 1 0 011 1v1M6 7v5M10 7v5M3 4l1 9a1 1 0 001 1h6a1 1 0 001-1l1-9" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Delete
              </button>
            </div>
          </div>
        </div>

        <div class="ws-card-body">
          <p class="ws-card-name">{{ ws.title }}</p>
          <p class="ws-card-sub">{{ ws.description || 'No description' }}</p>
        </div>

        <div class="ws-card-footer">
          <div
            class="ws-card-initial"
            :style="{ background: palette(idx).initBg, color: palette(idx).accent }"
          >
            {{ ws.title.slice(0, 1).toUpperCase() }}
          </div>
          <span class="ws-card-meta" :style="{ color: palette(idx).accent }">{{ timeAgo(ws.updated_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { timeAgo } from '../../utils/time'
import type { Workspace, Project } from '../../types'
import { useTheme } from '../../composables/useTheme'
import { useConfirm } from '../../composables/useConfirm'

const props = defineProps<{ workspaces: Workspace[]; projects: Project[] }>()
const emit = defineEmits<{ 'create': []; 'edit': [ws: Workspace]; 'delete': [id: number] }>()

const { isDark } = useTheme()
const { confirm } = useConfirm()
const wsMenuOpenId = ref<number | null>(null)

const WS_PALETTE = [
  { bg: '#FCE7F3', border: '#F9A8D4', accent: '#9D174D', initBg: '#F472B6' },
  { bg: '#D5EDF0', border: '#80C4C0', accent: '#1A7068', initBg: '#80C8C4' },
  { bg: '#F2E0CC', border: '#CFA070', accent: '#7A3410', initBg: '#D4A878' },
  { bg: '#ECD8F8', border: '#C090DC', accent: '#6A2080', initBg: '#C090D8' },
  { bg: '#D8F0D8', border: '#70C878', accent: '#1A5820', initBg: '#68CC80' },
  { bg: '#DCEAF8', border: '#90B8E0', accent: '#1A4090', initBg: '#A0C4EC' },
]

const WS_PALETTE_DARK = [
  { bg: 'rgba(157,23,77,0.22)', border: 'rgba(249,168,212,0.38)', accent: '#F9A8D4', initBg: 'rgba(244,114,182,0.22)' },
  { bg: 'rgba(26,112,104,0.22)', border: 'rgba(128,200,196,0.38)', accent: '#80C8C4', initBg: 'rgba(128,200,196,0.22)' },
  { bg: 'rgba(122,52,16,0.22)', border: 'rgba(212,168,120,0.38)', accent: '#D4A878', initBg: 'rgba(212,168,120,0.22)' },
  { bg: 'rgba(106,32,128,0.22)', border: 'rgba(192,144,216,0.38)', accent: '#C090D8', initBg: 'rgba(192,144,216,0.22)' },
  { bg: 'rgba(26,88,32,0.22)', border: 'rgba(104,204,128,0.38)', accent: '#68CC80', initBg: 'rgba(104,204,128,0.22)' },
  { bg: 'rgba(26,64,144,0.22)', border: 'rgba(160,196,236,0.38)', accent: '#A0C4EC', initBg: 'rgba(160,196,236,0.22)' },
]

function palette(idx: number) {
  const arr = isDark.value ? WS_PALETTE_DARK : WS_PALETTE
  return arr[idx % arr.length]
}

function wsProjectCount(wsId: number): number {
  return props.projects.filter(p => p.workspace_id === wsId).length
}

function handleEdit(ws: Workspace) {
  wsMenuOpenId.value = null
  emit('edit', ws)
}

async function handleDelete(id: number) {
  const ws = props.workspaces.find((w) => w.id === id)
  const projectCount = wsProjectCount(id)
  const ok = await confirm({
    title: 'Delete workspace?',
    message: `"${ws?.title || 'This workspace'}" will be permanently deleted.`,
    consequences: [
      `All ${projectCount} project${projectCount !== 1 ? 's' : ''} inside will be deleted`,
      'All tasks, comments, and files will be lost',
      'Team members will lose access',
      'This action cannot be undone',
    ],
    confirmLabel: 'Yes, delete workspace',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  wsMenuOpenId.value = null
  emit('delete', id)
}
</script>

<style scoped>
.create-new-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
  font-family: inherit;
}
.create-new-btn:hover { opacity: 0.8; }

.ws-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 28px 0;
  color: var(--text-muted);
  font-size: 13.5px;
}

/* ── Grid: wraps cleanly for any number of workspaces ── */
.ws-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(168px, 1fr));
  gap: 10px;
  max-height: 320px;
  overflow-y: auto;
  padding-right: 2px;
}
.ws-grid::-webkit-scrollbar { width: 4px; }
.ws-grid::-webkit-scrollbar-track { background: transparent; }
.ws-grid::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

.ws-card {
  border-radius: 16px;
  border: 1.5px solid transparent;
  padding: 16px 16px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 130px;
  cursor: pointer;
  transition: box-shadow 0.15s, transform 0.15s;
}
.ws-card:hover {
  box-shadow: 0 6px 20px rgba(10,11,13,0.10);
  transform: translateY(-2px);
}

.ws-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ws-card-count {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.2px;
  opacity: 0.75;
}

.ws-card-menu {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
  opacity: 0.6;
  transition: opacity 0.12s;
  font-family: inherit;
}
.ws-card-menu:hover { opacity: 1; }

.ws-card-body { flex: 1; }

.ws-card-name {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.3;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ws-card-sub {
  font-size: 12px;
  color: rgba(0,0,0,0.45);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ws-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
}

.ws-card-initial {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
}

.ws-card-meta {
  font-size: 11px;
  font-weight: 500;
  opacity: 0.7;
}

/* ── Dropdown ── */
.ws-menu-wrap { position: relative; }

.ws-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background: #ffffff;
  border: 1.5px solid var(--border);
  border-radius: 12px;
  padding: 4px;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(10,11,13,0.14);
  min-width: 130px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ws-dd-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border: none;
  background: none;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  cursor: pointer;
  transition: background 0.1s;
  text-align: left;
  width: 100%;
  font-family: inherit;
}
.ws-dd-item:hover { background: var(--bg); }
.ws-dd-danger { color: #A06060; }
.ws-dd-danger:hover { background: #F8EEEE; color: #7A3A3A; }
</style>
