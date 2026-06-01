<template>
  <div class="plan-detail" v-if="plan">
    <!-- Header -->
    <div class="plan-header">
      <div class="plan-header-left">
        <button class="btn btn-sm btn-ghost back-btn" @click="router.push('/plans')">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M8.5 2.5L4 7l4.5 4.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Plans
        </button>
        <div class="plan-title-row">
          <h2>{{ plan.title }}</h2>
          <span class="status-badge" :class="`badge-${plan.status}`">{{ plan.status }}</span>
        </div>
        <p v-if="plan.description" class="plan-desc">{{ plan.description }}</p>
      </div>
      <div class="plan-header-right">
        <div class="overall-progress">
          <div class="progress-ring-wrap">
            <svg viewBox="0 0 48 48" width="48" height="48">
              <circle cx="24" cy="24" r="20" fill="none" stroke="var(--bg)" stroke-width="5"/>
              <circle
                cx="24" cy="24" r="20" fill="none"
                :stroke="progressColor"
                stroke-width="5"
                stroke-linecap="round"
                :stroke-dasharray="`${2 * Math.PI * 20}`"
                :stroke-dashoffset="`${2 * Math.PI * 20 * (1 - pct / 100)}`"
                transform="rotate(-90 24 24)"
                style="transition: stroke-dashoffset 0.4s ease"
              />
            </svg>
            <span class="ring-label">{{ pct }}%</span>
          </div>
          <div class="progress-meta">
            <span class="progress-fraction">{{ completedCount }} / {{ plan.steps.length }} steps</span>
            <span class="progress-sub">{{ remainingCount }} remaining</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Steps -->
    <div class="steps-list">
      <div
        v-for="(step, idx) in plan.steps"
        :key="step.id"
        class="step-row"
        :class="`step-${step.status}`"
      >
        <!-- Order + status indicator -->
        <div class="step-indicator">
          <div class="step-number" :class="`num-${step.status}`">
            <svg v-if="step.status === 'completed'" viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M2.5 7l3 3 6-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="step.status === 'failed'" viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M4 4l6 6M10 4l-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <svg v-else-if="step.status === 'skipped'" viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M4 7h6M8.5 5l2 2-2 2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span v-else-if="step.status === 'running'" class="running-dot-sm"></span>
            <span v-else>{{ idx + 1 }}</span>
          </div>
          <div v-if="idx < plan.steps.length - 1" class="step-line" :class="`line-${step.status}`"></div>
        </div>

        <!-- Content -->
        <div class="step-content">
          <div class="step-head">
            <span class="step-title" :class="{ 'step-done-text': step.status === 'completed' || step.status === 'skipped' }">
              {{ step.title }}
            </span>
            <span class="priority-chip" :class="`priority-${step.priority}`">{{ step.priority }}</span>
          </div>

          <p v-if="step.description" class="step-desc">{{ step.description }}</p>

          <div class="step-meta-row">
            <span v-if="step.dependencies.length" class="dep-badge">
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M2 6h4M6 4l2 2-2 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
              After step{{ step.dependencies.length > 1 ? 's' : '' }}
              {{ step.dependencies.map(id => getStepOrder(id)).join(', ') }}
            </span>
            <a
              v-if="step.linked_task_id"
              class="linked-task"
              @click.prevent="router.push(`/tasks/${step.linked_task_uuid ?? step.linked_task_id}`)"
            >
              <svg viewBox="0 0 12 12" fill="none" width="10" height="10"><path d="M5 2H2.5A.5.5 0 002 2.5v7a.5.5 0 00.5.5h7a.5.5 0 00.5-.5V7M7 2h3v3M5 7l5-5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              Linked task
            </a>
          </div>

          <p v-if="step.agent_notes" class="agent-notes">{{ step.agent_notes }}</p>

          <!-- Actions — only show for non-terminal states -->
          <div v-if="step.status !== 'completed' && step.status !== 'skipped'" class="step-actions">
            <template v-if="step.status === 'pending'">
              <button class="btn btn-sm" @click="setStatus(step, 'running')" :disabled="isBlocked(step)">
                Start
              </button>
              <button class="btn btn-sm btn-ghost" @click="setStatus(step, 'skipped')">Skip</button>
              <span v-if="isBlocked(step)" class="blocked-hint">Waiting on {{ step.dependencies.length }} step{{ step.dependencies.length > 1 ? 's' : '' }}</span>
            </template>
            <template v-if="step.status === 'running'">
              <button class="btn btn-sm btn-primary" @click="setStatus(step, 'completed')">Mark complete</button>
              <button class="btn btn-sm btn-ghost" @click="setStatus(step, 'failed')">Mark failed</button>
            </template>
            <template v-if="step.status === 'failed'">
              <button class="btn btn-sm" @click="setStatus(step, 'pending')">Retry</button>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="store.loading" class="loading-state">
    <div class="spinner spinner-lg"></div>
  </div>

  <div v-else class="empty">Plan not found.</div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { PlanStep, StepStatus } from '../types'
import { usePlanStore } from '../stores/plans'

const route = useRoute()
const router = useRouter()
const store = usePlanStore()

const planId = computed(() => route.params.id as string)
const plan = computed(() => store.current)

onMounted(() => store.fetchOne(planId.value))

const pct = computed(() => store.progress(plan.value!))
const completedCount = computed(() => plan.value?.steps.filter(s => s.status === 'completed' || s.status === 'skipped').length ?? 0)
const remainingCount = computed(() => plan.value?.steps.filter(s => s.status === 'pending' || s.status === 'running').length ?? 0)
const progressColor = computed(() => {
  if (pct.value === 100) return 'var(--success)'
  if (pct.value > 50) return 'var(--primary)'
  return '#F59E0B'
})

function getStepOrder(stepId: number): number {
  const idx = plan.value?.steps.findIndex(s => s.id === stepId) ?? -1
  return idx + 1
}

function isBlocked(step: PlanStep): boolean {
  if (!step.dependencies.length) return false
  return step.dependencies.some(depId => {
    const dep = plan.value?.steps.find(s => s.id === depId)
    return dep && dep.status !== 'completed' && dep.status !== 'skipped'
  })
}

async function setStatus(step: PlanStep, status: StepStatus) {
  await store.updateStep(plan.value!.uuid, step.uuid, status)
}
</script>

<style scoped>
.plan-detail {
  padding: 32px 32px 80px;
  max-width: 800px;
}

/* ── Header ── */
.plan-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 40px;
}

.plan-header-left { flex: 1; min-width: 0; }

.back-btn {
  margin-bottom: 14px;
  color: var(--text-muted);
  padding-left: 6px;
}

.plan-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.plan-title-row h2 {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.6px;
  color: var(--text);
  line-height: 1.2;
}

.status-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  border: 1px solid;
}
.badge-active    { background: #E5E2FF; color: #3830A0; border-color: #B0A8E8; }
.badge-completed { background: #D8F0DC; color: #1A5820; border-color: #70C878; }
.badge-draft     { background: var(--bg); color: var(--text-muted); border-color: var(--border); }
.badge-cancelled { background: var(--danger-bg); color: var(--danger); border-color: var(--danger-border); }

.plan-desc {
  font-size: 13.5px;
  color: var(--text-muted);
  line-height: 1.6;
}

/* Progress ring */
.overall-progress {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.progress-ring-wrap {
  position: relative;
  width: 48px;
  height: 48px;
  flex-shrink: 0;
}

.ring-label {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  color: var(--text);
}

.progress-fraction {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  display: block;
}

.progress-sub {
  font-size: 12px;
  color: var(--text-muted);
  display: block;
  margin-top: 2px;
}

/* ── Steps ── */
.steps-list {
  display: flex;
  flex-direction: column;
}

.step-row {
  display: flex;
  gap: 0;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 40px;
  flex-shrink: 0;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  border: 2px solid;
  transition: all 0.2s;
}
.num-pending   { background: var(--surface); border-color: var(--border); color: var(--text-muted); }
.num-running   { background: #E5E2FF; border-color: #B0A8E8; color: #3830A0; }
.num-completed { background: #D8F0DC; border-color: #70C878; color: #1A5820; }
.num-failed    { background: var(--danger-bg); border-color: var(--danger-border); color: var(--danger); }
.num-skipped   { background: var(--bg); border-color: var(--border); color: var(--text-light); }

.step-line {
  width: 2px;
  flex: 1;
  min-height: 16px;
  margin: 4px 0;
}
.line-completed { background: #70C878; }
.line-running   { background: #B0A8E8; }
.line-pending, .line-failed, .line-skipped { background: var(--border); }

.running-dot-sm {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3830A0;
  animation: pulse 1s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.75)} }

/* Step content */
.step-content {
  flex: 1;
  padding: 0 0 28px 16px;
  min-width: 0;
}

.step-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 6px;
  min-height: 30px;
}

.step-title {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.2px;
  line-height: 1.3;
}
.step-done-text {
  color: var(--text-muted);
  text-decoration: line-through;
  text-decoration-color: var(--border-strong);
}

.priority-chip {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid;
}
.priority-low    { background: var(--bg); color: var(--text-light); border-color: var(--border); }
.priority-medium { background: #E5E2FF; color: #3830A0; border-color: #B0A8E8; }
.priority-high   { background: #F2E0CC; color: #7A3410; border-color: #CFA070; }
.priority-urgent { background: #F5DEDE; color: #601010; border-color: #D07878; }

.step-desc {
  font-size: 13.5px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 8px;
}

.step-meta-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.dep-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--text-light);
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.linked-task {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: #3830A0;
  cursor: pointer;
  font-weight: 500;
}

.agent-notes {
  font-size: 12.5px;
  color: var(--text-muted);
  font-style: italic;
  background: var(--bg);
  border-left: 3px solid var(--border-strong);
  padding: 8px 12px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  margin: 8px 0;
  line-height: 1.5;
}

.step-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.blocked-hint {
  font-size: 12px;
  color: var(--text-light);
  font-style: italic;
}

/* Loading / empty */
.loading-state { display: flex; justify-content: center; padding: 80px; }
.empty { text-align: center; padding: 80px; color: var(--text-muted); }

.spinner { display: inline-block; width: 22px; height: 22px; border: 3px solid var(--border); border-top-color: #3830A0; border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 600px) {
  .plan-detail { padding: 20px 16px 60px; }
  .plan-header { flex-direction: column; }
}
</style>
