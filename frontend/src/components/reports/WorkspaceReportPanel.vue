<template>
  <div class="ws-reports-panel">
    <div v-if="loading" class="rp-loading">Loading workspace report…</div>

    <template v-else-if="report">
      <div class="rp-cards">
        <div class="rp-card">
          <div class="rp-card-icon rp-ci-projects">
            <font-awesome-icon :icon="['fas', 'folder']" />
          </div>
          <div class="rp-card-body">
            <span class="rp-card-value">{{ report.total_projects }}</span>
            <span class="rp-card-label">Projects</span>
          </div>
        </div>
        <div class="rp-card">
          <div class="rp-card-icon rp-ci-total">
            <font-awesome-icon :icon="['fas', 'list-check']" />
          </div>
          <div class="rp-card-body">
            <span class="rp-card-value">{{ report.total_tasks }}</span>
            <span class="rp-card-label">Total tasks</span>
          </div>
        </div>
        <div class="rp-card">
          <div class="rp-card-icon rp-ci-done">
            <font-awesome-icon :icon="['fas', 'check']" />
          </div>
          <div class="rp-card-body">
            <span class="rp-card-value">{{ report.completed_tasks }}</span>
            <span class="rp-card-label">Completed</span>
          </div>
        </div>
        <div class="rp-card">
          <div class="rp-card-icon rp-ci-overdue">
            <font-awesome-icon :icon="['fas', 'exclamation']" />
          </div>
          <div class="rp-card-body">
            <span class="rp-card-value">{{ report.overdue_tasks }}</span>
            <span class="rp-card-label">Overdue</span>
          </div>
        </div>
        <div class="rp-card">
          <div class="rp-card-icon rp-ci-pct">
            <font-awesome-icon :icon="['fas', 'percent']" />
          </div>
          <div class="rp-card-body">
            <span class="rp-card-value">{{ Math.round(report.completion_pct) }}%</span>
            <span class="rp-card-label">Complete</span>
          </div>
        </div>
        <div class="rp-card">
          <div class="rp-card-icon rp-ci-members">
            <font-awesome-icon :icon="['fas', 'users']" />
          </div>
          <div class="rp-card-body">
            <span class="rp-card-value">{{ report.member_count }}</span>
            <span class="rp-card-label">Members</span>
          </div>
        </div>
      </div>

      <div class="rp-section">
        <h4 class="rp-section-title">Tasks by status</h4>
        <div class="rp-bars">
          <div v-for="s in report.by_status" :key="s.status" class="rp-bar-row">
            <span class="rp-bar-label">{{ statusLabel(s.status) }}</span>
            <div class="rp-bar-track">
              <div
                class="rp-bar-fill"
                :class="`rp-bf-${s.status}`"
                :style="{ width: pct(s.count) + '%' }"
              ></div>
            </div>
            <span class="rp-bar-count">{{ s.count }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import type { WorkspaceReport as WorkspaceReportType } from '../../types'
import { useReportStore } from '../../stores/reports'

const props = defineProps<{ workspaceId: number }>()

const store = useReportStore()
const report = computed(() => store.workspaceReport)
const loading = computed(() => store.loading)

const maxCount = computed(() => {
  if (!report.value) return 1
  return Math.max(...report.value.by_status.map((s) => s.count), 1)
})

function pct(count: number): number {
  if (maxCount.value === 0) return 0
  return (count / maxCount.value) * 100
}

const STATUS_LABELS: Record<string, string> = {
  todo: 'Pending', in_progress: 'In Progress', review: 'Review',
  blocked: 'In Revision', completed: 'Completed',
}
function statusLabel(s: string) { return STATUS_LABELS[s] || s }

onMounted(() => { store.fetchWorkspaceReport(props.workspaceId) })
onUnmounted(() => { store.clear() })
</script>

<style scoped>
.ws-reports-panel { padding-top: 24px; }
.rp-loading { text-align: center; padding: 40px; color: var(--text-light); font-size: 13px; }
.rp-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; margin-bottom: 28px; }
.rp-card { display: flex; align-items: center; gap: 14px; padding: 18px; background: var(--surface); border: 1.5px solid var(--border); border-radius: 12px; }
.rp-card-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 17px; flex-shrink: 0; }
.rp-ci-projects { background: #F0F9FF; color: #0369A1; }
.rp-ci-total   { background: #EFF6FF; color: #1D4ED8; }
.rp-ci-done    { background: #ECFDF5; color: #065F46; }
.rp-ci-overdue { background: #FFF1F2; color: #B91C1C; }
.rp-ci-pct     { background: #F5F3FF; color: #6D28D9; }
.rp-ci-members { background: #FFF7ED; color: #C2410C; }
.rp-card-body { display: flex; flex-direction: column; gap: 2px; }
.rp-card-value { font-size: 22px; font-weight: 800; color: var(--text); letter-spacing: -0.5px; line-height: 1; }
.rp-card-label { font-size: 12px; color: var(--text-muted); font-weight: 500; }
.rp-section { margin-bottom: 24px; }
.rp-section-title { font-size: 14px; font-weight: 700; color: var(--text); margin-bottom: 12px; }
.rp-bars { display: flex; flex-direction: column; gap: 8px; }
.rp-bar-row { display: flex; align-items: center; gap: 12px; }
.rp-bar-label { width: 100px; font-size: 13px; font-weight: 600; color: var(--text-muted); flex-shrink: 0; }
.rp-bar-track { flex: 1; height: 20px; background: var(--bg); border-radius: 10px; overflow: hidden; }
.rp-bar-fill { height: 100%; border-radius: 10px; transition: width 0.4s ease; min-width: 4px; }
.rp-bf-todo         { background: #94A3B8; }
.rp-bf-in_progress  { background: #3B82F6; }
.rp-bf-review       { background: #F59E0B; }
.rp-bf-blocked      { background: #EF4444; }
.rp-bf-completed    { background: #10B981; }
.rp-bar-count { width: 36px; font-size: 13px; font-weight: 700; color: var(--text); text-align: right; flex-shrink: 0; }
:global([data-theme="dark"]) .rp-card { background: #1A2D42; border-color: rgba(91, 155, 255, 0.20); }
:global([data-theme="dark"]) .rp-bar-track { background: #253341; }
:global([data-theme="dark"]) .rp-ci-projects { background: rgba(14,165,233,0.15); color: #38BDF8; }
:global([data-theme="dark"]) .rp-ci-total   { background: rgba(91,155,255,0.15); color: #5B9BFF; }
:global([data-theme="dark"]) .rp-ci-done    { background: rgba(0,186,124,0.15); color: #00BA7C; }
:global([data-theme="dark"]) .rp-ci-overdue { background: rgba(255,107,120,0.15); color: #FF6B78; }
:global([data-theme="dark"]) .rp-ci-pct     { background: rgba(139,92,246,0.15); color: #A78BFA; }
:global([data-theme="dark"]) .rp-ci-members { background: rgba(251,146,60,0.15); color: #FB923C; }
</style>
