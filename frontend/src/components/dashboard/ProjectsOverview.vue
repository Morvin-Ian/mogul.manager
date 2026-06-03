<template>
  <div class="panel">
    <div class="panel-hdr">
      <span class="panel-title">Projects Overview</span>
      <button class="hdr-link" @click="$router.push('/projects')">View all →</button>
    </div>

    <!-- Stat strip -->
    <div class="ov-stats">
      <div class="ov-stat" @click="$router.push('/projects')">
        <span class="ov-num">{{ projects.length }}</span>
        <span class="ov-lbl">Total</span>
      </div>
      <div class="ov-stat-divider"/>
      <div class="ov-stat" @click="$router.push('/projects?status=active')">
        <span class="ov-num" style="color:#F59E0B">{{ activeCount }}</span>
        <span class="ov-lbl">Active</span>
      </div>
      <div class="ov-stat-divider"/>
      <div class="ov-stat" @click="$router.push('/projects?status=completed')">
        <span class="ov-num" style="color:#3B82F6">{{ completedCount }}</span>
        <span class="ov-lbl">Done</span>
      </div>
      <div class="ov-stat-divider"/>
      <div class="ov-stat" @click="$router.push('/projects?status=planning')">
        <span class="ov-num" style="color:#9CA3AF">{{ notStartedCount }}</span>
        <span class="ov-lbl">Planned</span>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="ov-progress-wrap" v-if="projects.length > 0">
      <div class="ov-progress-bar">
        <div class="ov-progress-fill" :style="{ width: completionPct + '%' }"/>
      </div>
      <span class="ov-progress-label">{{ completionPct }}% complete</span>
    </div>

    <!-- Donut + legend -->
    <div class="overview-body">
      <div class="donut-wrap">
        <svg class="donut-svg" viewBox="0 0 200 200">
          <circle cx="100" cy="100" r="72" fill="none" stroke="#F0F1F6" stroke-width="26"/>
          <circle cx="100" cy="100" r="72" fill="none" stroke="#F59E0B" stroke-width="26"
            :stroke-dasharray="`${ipArc} ${circumference}`"
            stroke-dashoffset="0"
            transform="rotate(-90 100 100)" stroke-linecap="round"/>
          <circle cx="100" cy="100" r="72" fill="none" stroke="#3B82F6" stroke-width="26"
            :stroke-dasharray="`${compArc} ${circumference}`"
            :stroke-dashoffset="`${-ipArc}`"
            transform="rotate(-90 100 100)" stroke-linecap="round"/>
          <circle cx="100" cy="100" r="72" fill="none" stroke="#E5E7EB" stroke-width="26"
            :stroke-dasharray="`${nsArc} ${circumference}`"
            :stroke-dashoffset="`${-(ipArc + compArc)}`"
            transform="rotate(-90 100 100)" stroke-linecap="round"/>
          <text x="100" y="93" text-anchor="middle" font-size="34" font-weight="800"
            fill="#0A0B0D" font-family="Outfit, sans-serif">{{ projects.length }}</text>
          <text x="100" y="114" text-anchor="middle" font-size="13" fill="#5B616E"
            font-family="Outfit, sans-serif">projects</text>
        </svg>
      </div>
      <div class="donut-legend">
        <div class="legend-row">
          <span class="legend-dot" style="background:#F59E0B"/>
          <span class="legend-text">Active <strong>{{ activeCount }}</strong></span>
        </div>
        <div class="legend-row">
          <span class="legend-dot" style="background:#3B82F6"/>
          <span class="legend-text">Completed <strong>{{ completedCount }}</strong></span>
        </div>
        <div class="legend-row">
          <span class="legend-dot" style="background:#E5E7EB"/>
          <span class="legend-text">Planned <strong>{{ notStartedCount }}</strong></span>
        </div>
      </div>
    </div>

    <!-- Recent projects -->
    <div v-if="projects.length > 0" class="ov-recent">
      <span class="ov-recent-hdr">Recent</span>
      <div
        v-for="(p, idx) in projects.slice(0, 5)"
        :key="p.id"
        class="ov-proj-row"
        @click="$router.push(`/projects/${p.uuid}`)"
      >
        <span class="ov-proj-dot" :style="{ background: PROJECT_COLORS[idx % PROJECT_COLORS.length] }"/>
        <span class="ov-proj-name">{{ p.title }}</span>
        <span class="badge" :class="`badge-${p.status}`">{{ (p.status ?? 'todo').replace('_',' ') }}</span>
      </div>
    </div>
    <div v-else class="ov-empty">
      <p>No projects yet — create one to get started.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Project } from '../../types'

const props = defineProps<{ projects: Project[] }>()

const PROJECT_COLORS = [
  '#F59E0B', '#6B7280', '#0D9488', '#6366F1',
  '#10B981', '#EF4444', '#F97316', '#3B82F6',
]

const activeCount = computed(() => props.projects.filter(p => p.status === 'active').length)
const completedCount = computed(() => props.projects.filter(p => p.status === 'completed').length)
const notStartedCount = computed(() => props.projects.filter(p => p.status === 'planning' || p.status === 'on_hold').length)

const completionPct = computed(() => {
  const total = props.projects.length
  return total > 0 ? Math.round((completedCount.value / total) * 100) : 0
})

const circumference = 2 * Math.PI * 72
const ipArc = computed(() => {
  const total = props.projects.length
  return total > 0 ? (activeCount.value / total) * circumference : 0
})
const compArc = computed(() => {
  const total = props.projects.length
  return total > 0 ? (completedCount.value / total) * circumference : 0
})
const nsArc = computed(() => {
  const total = props.projects.length
  return total > 0 ? (notStartedCount.value / total) * circumference : 0
})
</script>

<style scoped>
/* ── Projects Overview ──────────────── */
.ov-stats {
  display: flex;
  align-items: stretch;
  border: 1.5px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 14px;
}

.ov-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 14px 10px;
  cursor: pointer;
  transition: background 0.12s;
  border-radius: 4px;
}
.ov-stat:hover { background: var(--bg); }

.ov-stat-divider {
  width: 1px;
  background: var(--border);
  flex-shrink: 0;
}

.ov-num {
  font-size: 26px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
  line-height: 1;
}

.ov-lbl {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: 0.1px;
}

.ov-progress-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  padding: 0 4px;
}

.ov-progress-bar {
  flex: 1;
  height: 6px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
}

.ov-progress-fill {
  height: 100%;
  background: #10B981;
  border-radius: 99px;
  transition: width 0.4s ease;
}

.ov-progress-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.overview-body {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}

.donut-wrap { flex-shrink: 0; }

.donut-svg {
  width: 148px;
  height: 148px;
  display: block;
}

.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-text strong { color: var(--text); }

.ov-recent {
  margin-top: 16px;
  border-top: 1.5px solid var(--border);
  padding-top: 14px;
}

.ov-recent-hdr {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  display: block;
  margin-bottom: 10px;
}

.ov-proj-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.12s;
}
.ov-proj-row:hover { background: var(--bg); }

.ov-proj-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.ov-proj-name {
  flex: 1;
  font-size: 13.5px;
  font-weight: 500;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ov-empty {
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 12px 0;
}
</style>
