<template>
  <div class="plan-detail">
    <div v-if="loading" class="loading-state">Loading plan…</div>

    <template v-else-if="plan">
      <!-- Back + breadcrumb -->
      <div class="pd-top">
        <button class="btn btn-ghost btn-sm" @click="$router.push('/plans')">
          <svg viewBox="0 0 12 12" fill="none" width="11" height="11"><path d="M7 2L3 6l4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
          All plans
        </button>
        <span class="breadcrumb-ws" v-if="workspaceTitle">{{ workspaceTitle }}</span>
        <span class="breadcrumb-project" v-if="plan.project_title">{{ plan.project_title }}</span>
      </div>

      <!-- Header -->
      <div class="pd-header">
        <div class="pd-header-left">
          <h2>{{ plan.title }}</h2>
          <p v-if="plan.description" class="pd-desc">{{ plan.description }}</p>
        </div>
        <div class="pd-header-right">
          <span class="plan-status-badge" :class="`psb-${plan.status}`">
            {{ STATUS_LABELS[plan.status] }}
          </span>
        </div>
      </div>

      <!-- Meta cards -->
      <div class="pd-meta">
        <div v-if="plan.start_date" class="pd-meta-card">
          <span class="pd-meta-label">Start</span>
          <span class="pd-meta-value">{{ formatDate(plan.start_date) }}</span>
        </div>
        <div v-if="plan.target_completion_date" class="pd-meta-card">
          <span class="pd-meta-label">Target</span>
          <span class="pd-meta-value">{{ formatDate(plan.target_completion_date) }}</span>
        </div>
        <div v-if="plan.estimated_budget != null" class="pd-meta-card">
          <span class="pd-meta-label">Est. Budget</span>
          <span class="pd-meta-value">${{ plan.estimated_budget }}</span>
        </div>
        <div v-if="plan.actual_budget != null" class="pd-meta-card">
          <span class="pd-meta-label">Actual</span>
          <span class="pd-meta-value">${{ plan.actual_budget }}</span>
        </div>
        <div class="pd-meta-card">
          <span class="pd-meta-label">Steps</span>
          <span class="pd-meta-value">{{ plan.steps.length }}</span>
        </div>
      </div>

      <!-- Progress -->
      <div class="pd-progress-row">
        <div class="pd-progress-track">
          <div class="pd-progress-fill" :style="{ width: progressPct + '%' }"></div>
        </div>
        <span class="pd-progress-label">{{ progressPct }}% complete</span>
      </div>
      <div class="pd-progress-stats">
        <span class="pds-done">{{ doneCount }} done</span>
        <span class="pds-prog">{{ progCount }} in progress</span>
        <span class="pds-pending">{{ pendingCount }} pending</span>
      </div>

      <!-- Steps -->
      <div class="pd-steps-heading">Steps</div>
      <div class="pd-steps">
        <div v-for="(step, i) in sortedSteps" :key="step.uuid" class="pd-step" :class="`pd-step--${step.status}`">
          <div class="pd-step-order">{{ i + 1 }}</div>
          <div class="pd-step-body">
            <div class="pd-step-title-row">
              <span class="pd-step-title">{{ step.title }}</span>
              <span class="step-status-chip" :class="`ssc-${step.status}`">{{ STATUS_LABELS[step.status] }}</span>
              <span class="step-priority-chip" :class="`spc-${step.priority}`">{{ step.priority }}</span>
            </div>
            <p v-if="step.description" class="pd-step-desc">{{ step.description }}</p>
            <div v-if="step.estimated_hours || step.actual_hours || step.cost_estimate" class="pd-step-extras">
              <span v-if="step.estimated_hours" class="pde-item">{{ step.estimated_hours }}h est.</span>
              <span v-if="step.actual_hours" class="pde-item">{{ step.actual_hours }}h actual</span>
              <span v-if="step.cost_estimate" class="pde-item">${{ step.cost_estimate }}</span>
            </div>
            <div v-if="step.linked_task_uuid" class="pd-step-task-link">
              <button class="btn btn-ghost btn-xs" @click="openTask(step.linked_task_uuid!)">
                <svg viewBox="0 0 10 10" fill="none" width="9" height="9"><rect x="0.5" y="0.5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/><path d="M3 5l1.5 1.5 3-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                View Task
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="loading-state">Plan not found.</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlanStore } from '../stores/plans'
import { get } from '../stores/client'
import type { Workspace } from '../types'

const route = useRoute()
const router = useRouter()
const planStore = usePlanStore()

const plan = computed(() => planStore.current)
const loading = ref(false)
const workspaceTitle = ref('')

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft', active: 'Active', completed: 'Completed', cancelled: 'Cancelled',
  pending: 'Pending', in_progress: 'In Progress', skipped: 'Skipped',
}

const sortedSteps = computed(() => {
  if (!plan.value) return []
  return [...plan.value.steps].sort((a, b) => a.step_order - b.step_order)
})

const doneCount = computed(() => plan.value?.steps.filter(s => s.status === 'completed' || s.status === 'skipped').length ?? 0)
const progCount = computed(() => plan.value?.steps.filter(s => s.status === 'in_progress').length ?? 0)
const pendingCount = computed(() => plan.value?.steps.filter(s => s.status === 'pending').length ?? 0)
const progressPct = computed(() => plan.value ? planStore.progress(plan.value) : 0)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

async function openTask(uuid: string) {
  router.push(`/projects/${plan.value?.project_id}?task=${uuid}`)
}

async function load() {
  const id = route.params.id as string
  if (!id) return
  loading.value = true
  try {
    const p = await planStore.fetchOne(id)
    if (p) {
      const ws = await get<{ title: string }>(`/workspaces?project_id=${p.project_id}`).catch(() => null)
      // try to get workspace via projects endpoint
      const proj = await get<{ workspace_title: string | null }>(`/projects/${p.project_id}`).catch(() => null)
      if (proj?.workspace_title) workspaceTitle.value = proj.workspace_title
    }
  } catch {
    // error handled by store
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.plan-detail { padding: 32px 40px 80px; max-width: 900px; }
.loading-state { text-align: center; padding: 60px; color: var(--text-muted); font-size: 14px; }
.pd-top { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; font-size: 12.5px; }
.breadcrumb-ws, .breadcrumb-project { color: var(--text-light); }
.breadcrumb-ws::before, .breadcrumb-project::before { content: '/'; margin-right: 10px; color: var(--border); }
.pd-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 20px; }
.pd-header-left h2 { font-size: 26px; font-weight: 800; color: var(--text); letter-spacing: -0.6px; }
.pd-desc { font-size: 13.5px; color: var(--text-muted); margin-top: 6px; line-height: 1.6; }
.pd-header-right { flex-shrink: 0; }
.plan-status-badge { display: inline-flex; align-items: center; gap: 4px; padding: 4px 12px; border-radius: 999px; font-size: 11.5px; font-weight: 600; }
.psb-active { background: #D5EDF0; color: #1A7068; }
.psb-draft { background: #E2E8F0; color: #475569; }
.psb-completed { background: #D8F0DC; color: #1A5820; }
.psb-cancelled { background: #F5DEDE; color: #601010; }
.pd-meta { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 24px; }
.pd-meta-card { background: var(--surface); border: 1.5px solid var(--border); border-radius: 10px; padding: 10px 16px; min-width: 100px; }
.pd-meta-label { display: block; font-size: 10.5px; font-weight: 500; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }
.pd-meta-value { font-size: 15px; font-weight: 700; color: var(--text); }
.pd-progress-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.pd-progress-track { flex: 1; height: 8px; background: var(--border); border-radius: 99px; overflow: hidden; }
.pd-progress-fill { height: 100%; background: #10B981; border-radius: 99px; transition: width 0.4s ease; }
.pd-progress-label { font-size: 12px; font-weight: 600; color: var(--text-muted); min-width: 100px; text-align: right; }
.pd-progress-stats { display: flex; gap: 16px; margin-bottom: 28px; font-size: 12px; color: var(--text-light); }
.pds-done { color: #10B981; }
.pds-prog { color: #2563EB; }
.pds-pending { color: var(--text-muted); }
.pd-steps-heading { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 12px; }
.pd-steps { display: flex; flex-direction: column; gap: 8px; }
.pd-step { display: flex; gap: 12px; background: var(--surface); border: 1.5px solid var(--border); border-radius: 12px; padding: 14px 16px; }
.pd-step-order { width: 28px; height: 28px; background: var(--border); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: var(--text-light); flex-shrink: 0; }
.pd-step-body { flex: 1; min-width: 0; }
.pd-step-title-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.pd-step-title { font-size: 14px; font-weight: 600; color: var(--text); }
.step-status-chip { display: inline-flex; padding: 1px 7px; border-radius: 999px; font-size: 10.5px; font-weight: 600; }
.ssc-pending { background: #F1F5F9; color: #64748B; }
.ssc-in_progress { background: #DBE6FE; color: #1D4ED8; }
.ssc-completed { background: #D8F0DC; color: #1A5820; }
.ssc-skipped { background: #F1F5F9; color: #64748B; }
.step-priority-chip { padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; }
.spc-low { background: #E2E8F0; color: #475569; }
.spc-medium { background: #FEF3C7; color: #92400E; }
.spc-high { background: #FEE2E2; color: #991B1B; }
.spc-urgent { background: #FEE2E2; color: #7F1D1D; }
.pd-step-desc { font-size: 12.5px; color: var(--text-muted); margin-top: 4px; line-height: 1.5; }
.pd-step-extras { display: flex; gap: 8px; margin-top: 6px; }
.pde-item { font-size: 11px; background: var(--bg); padding: 2px 8px; border-radius: 6px; color: var(--text-light); }
.pd-step-task-link { margin-top: 6px; }
.pd-step--completed { opacity: 0.7; }
.pd-step--completed .pd-step-title { text-decoration: line-through; }
:global([data-theme="dark"]) .pd-meta-card, :global([data-theme="dark"]) .pd-step { background: #1A2D42; border-color: rgba(91,155,255,0.20); }
</style>
