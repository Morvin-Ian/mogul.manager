<template>
  <div class="ws-card" @click="$router.push(`/workspaces/${workspace.uuid}`)">
    <!-- Top row: folder icon + status -->
    <div class="card-top">
      <div class="card-folder" :style="{ color: pal.accent }">
        <svg viewBox="0 0 20 20" fill="none" width="20" height="20">
          <path d="M2 5.5A1.5 1.5 0 013.5 4h3.586a1 1 0 01.707.293L9.5 5.5H16.5A1.5 1.5 0 0118 7v8.5A1.5 1.5 0 0116.5 17h-13A1.5 1.5 0 012 15.5v-10z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="card-status-pill">
        <span class="status-dot" :style="{ background: workspace.is_archived ? '#8B98A5' : '#00BA7C' }"></span>
        <span class="status-text" :style="{ color: workspace.is_archived ? '#8B98A5' : '#00845A' }">
          {{ workspace.is_archived ? 'Archived' : 'Active' }}
        </span>
      </div>
    </div>

    <!-- Title -->
    <h3 class="card-title">{{ workspace.title }}</h3>

    <!-- Description -->
    <p class="card-desc">{{ workspace.description || 'No description added yet.' }}</p>

    <!-- Divider -->
    <div class="card-divider" :style="{ background: pal.border }"></div>

    <!-- Footer: date + arrow -->
    <div class="card-footer">
      <span class="card-date">
        <svg viewBox="0 0 14 14" fill="none" width="11" height="11">
          <rect x="1" y="2" width="12" height="10.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M1 5.5h12M5 1v2.5M9 1v2.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        {{ formatDate(workspace.created_at) }}
      </span>
      <span class="card-caret" :style="{ background: pal.initBg, color: pal.accent }">
        <svg viewBox="0 0 12 12" fill="none" width="10" height="10">
          <path d="M4 2l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from '../../composables/useTheme'
import type { Workspace } from '../../types'

const props = defineProps<{ workspace: Workspace }>()
const { isDark } = useTheme()

const PALETTE = [
  { bg: '#FCE7F3', border: '#F9A8D4', accent: '#9D174D', initBg: '#F472B6' },
  { bg: '#E6F4F3', border: '#A8D8D4', accent: '#1A7068', initBg: '#A8D8D4' },
  { bg: '#FDF3E7', border: '#F0CB96', accent: '#92400E', initBg: '#F0CB96' },
  { bg: '#FEF3C7', border: '#FDE68A', accent: '#92400E', initBg: '#F59E0B' },
  { bg: '#E8F8ED', border: '#96DCA8', accent: '#1A5820', initBg: '#96DCA8' },
  { bg: '#E6F0FB', border: '#A8CAEE', accent: '#1E3A7A', initBg: '#A8CAEE' },
]
const PALETTE_DARK = [
  { bg: 'rgba(157,23,77,0.22)', border: 'rgba(249,168,212,0.38)', accent: '#F9A8D4', initBg: 'rgba(244,114,182,0.22)' },
  { bg: 'rgba(26,112,104,0.15)', border: 'rgba(128,200,196,0.3)', accent: '#80C8C4', initBg: 'rgba(128,200,196,0.2)' },
  { bg: 'rgba(146,64,14,0.15)', border: 'rgba(240,203,150,0.3)', accent: '#F0CB96', initBg: 'rgba(240,203,150,0.2)' },
  { bg: 'rgba(146,64,14,0.22)', border: 'rgba(245,158,11,0.4)', accent: '#F59E0B', initBg: 'rgba(245,158,11,0.25)' },
  { bg: 'rgba(26,88,32,0.15)',  border: 'rgba(150,220,168,0.3)', accent: '#96DCA8', initBg: 'rgba(150,220,168,0.2)' },
  { bg: 'rgba(30,58,122,0.15)', border: 'rgba(168,202,238,0.3)', accent: '#A8CAEE', initBg: 'rgba(168,202,238,0.2)' },
]

const pal = computed(() => {
  const arr = isDark.value ? PALETTE_DARK : PALETTE
  return arr[props.workspace.id % arr.length]
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.ws-card {
  background: v-bind('pal.bg');
  border: 1px solid v-bind('pal.border');
  border-radius: 16px;
  padding: 20px 22px 18px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0;
  transition: box-shadow 0.2s, transform 0.18s;
  box-shadow: 0 4px 16px rgba(10,11,13,0.08), 0 1px 4px rgba(10,11,13,0.04);
}
.ws-card:hover {
  box-shadow: 0 16px 48px rgba(10,11,13,0.16), 0 4px 12px rgba(10,11,13,0.08);
  transform: translateY(-4px);
}

/* Top row */
.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.card-folder { display: flex; align-items: center; }
.card-status-pill { display: inline-flex; align-items: center; gap: 5px; }
.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-text { font-size: 12px; font-weight: 600; letter-spacing: 0.1px; }

/* Title */
.card-title {
  font-size: 16.5px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
  line-height: 1.25;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Description */
.card-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 16px;
  flex: 1;
}

/* Divider */
.card-divider {
  height: 1px;
  margin-bottom: 14px;
  opacity: 0.6;
}

/* Footer */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-date {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-muted);
}
.card-caret {
  width: 26px; height: 26px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: transform 0.15s;
}
.ws-card:hover .card-caret { transform: translateX(3px); }
</style>
