<template>
  <div
    class="ws-card"
    :style="{
      background: pal.bg,
      borderColor: pal.border,
    }"
    @click="$router.push(`/workspaces/${workspace.id}`)"
  >
    <!-- Top row: initial avatar + status -->
    <div class="ws-top">
      <div class="ws-initial" :style="{ background: pal.initBg, color: pal.accent }">
        {{ workspace.title.slice(0, 1).toUpperCase() }}
      </div>
      <span class="ws-status" :class="workspace.is_archived ? 'ws-status--archived' : 'ws-status--active'">
        <span class="ws-dot"></span>
        {{ workspace.is_archived ? 'Archived' : 'Active' }}
      </span>
    </div>

    <!-- Body -->
    <div class="ws-body">
      <h3 class="ws-title">{{ workspace.title }}</h3>
      <p class="ws-desc">{{ workspace.description || 'No description added yet.' }}</p>
    </div>

    <!-- Footer -->
    <div class="ws-footer">
      <span class="ws-date">{{ formatDate(workspace.created_at) }}</span>
      <span class="ws-caret" :style="{ background: pal.initBg, color: pal.accent }">
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
  { bg: '#E5E2FF', border: '#B0A8E8', accent: '#3830A0', initBg: '#C0BAF0' },
  { bg: '#D5EDF0', border: '#80C4C0', accent: '#1A7068', initBg: '#80C8C4' },
  { bg: '#F2E0CC', border: '#CFA070', accent: '#7A3410', initBg: '#D4A878' },
  { bg: '#ECD8F8', border: '#C090DC', accent: '#6A2080', initBg: '#C090D8' },
  { bg: '#D8F0D8', border: '#70C878', accent: '#1A5820', initBg: '#68CC80' },
  { bg: '#DCEAF8', border: '#90B8E0', accent: '#1A4090', initBg: '#A0C4EC' },
]

const PALETTE_DARK = [
  { bg: 'rgba(56,48,160,0.2)', border: 'rgba(168,160,248,0.35)', accent: '#A8A0F8', initBg: 'rgba(192,186,240,0.2)' },
  { bg: 'rgba(26,112,104,0.2)', border: 'rgba(128,200,196,0.35)', accent: '#80C8C4', initBg: 'rgba(128,200,196,0.2)' },
  { bg: 'rgba(122,52,16,0.2)', border: 'rgba(212,168,120,0.35)', accent: '#D4A878', initBg: 'rgba(212,168,120,0.2)' },
  { bg: 'rgba(106,32,128,0.2)', border: 'rgba(192,144,216,0.35)', accent: '#C090D8', initBg: 'rgba(192,144,216,0.2)' },
  { bg: 'rgba(26,88,32,0.2)', border: 'rgba(104,204,128,0.35)', accent: '#68CC80', initBg: 'rgba(104,204,128,0.2)' },
  { bg: 'rgba(26,64,144,0.2)', border: 'rgba(160,196,236,0.35)', accent: '#A0C4EC', initBg: 'rgba(160,196,236,0.2)' },
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
  border: 1.5px solid transparent;
  border-radius: 20px;
  padding: 22px 22px 18px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 180px;
  transition: box-shadow 0.18s, transform 0.18s;
  position: relative;
  overflow: hidden;
}

.ws-card::before {
  content: '';
  position: absolute;
  top: -30px;
  right: -20px;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: rgba(255,255,255,0.18);
  pointer-events: none;
}

.ws-card:hover {
  box-shadow: 0 8px 28px rgba(10,11,13,0.13);
  transform: translateY(-3px);
}

.ws-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ws-initial {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.5px;
  flex-shrink: 0;
}

.ws-status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.55);
  letter-spacing: 0.1px;
}

.ws-status--active  { color: #1A5820; }
.ws-status--archived { color: #7A3410; }

.ws-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.ws-status--active  .ws-dot { background: #28A048; }
.ws-status--archived .ws-dot { background: #B06030; }

.ws-body { flex: 1; }

.ws-title {
  font-size: 17px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
  line-height: 1.25;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ws-desc {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ws-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}

.ws-date {
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-light);
}

.ws-caret {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.15s;
}
.ws-card:hover .ws-caret { transform: translateX(3px); }
</style>
