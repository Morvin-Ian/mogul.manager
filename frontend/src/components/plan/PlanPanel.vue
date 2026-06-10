<template>
  <div class="plan-panel">
    <Loading v-if="planStore.loading" label="Loading plan…" />

    <template v-else>
      <!-- ── Empty state ── -->
      <div v-if="!activePlan" class="plan-empty">
        <div class="plan-empty-icon">
          <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
            <path d="M12 2l2 6h6l-5 3.5 2 6L12 14l-5 3.5 2-6L4 8h6l2-6z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
          </svg>
        </div>
        <p class="plan-empty-title">No plan yet</p>
        <p class="plan-empty-sub">AI will break your goal into ordered steps and create linked tasks automatically.</p>
        <button class="btn btn-primary" @click="showCreate = true">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
            <path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          Generate Plan
        </button>
      </div>

      <!-- ── Plan view ── -->
      <div v-else class="plan-view">

        <!-- Plan header -->
        <div class="plan-header">
          <div class="plan-header-left">
            <div class="plan-title-row">
              <h3 class="plan-title">{{ activePlan.title }}</h3>
              <span class="plan-status-badge" :class="`psb-${activePlan.status}`">
                <span class="psb-dot"></span>
                {{ STATUS_LABELS[activePlan.status] }}
              </span>
            </div>
            <p v-if="activePlan.description" class="plan-description">{{ activePlan.description }}</p>
          </div>
          <div class="plan-header-right">
            <button class="btn btn-sm btn-ghost" @click="showCreate = true">
              <svg viewBox="0 0 14 14" fill="none" width="11" height="11">
                <path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
              New plan
            </button>
            <button class="btn btn-sm btn-danger" @click="handleDeletePlan">Delete</button>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="plan-progress-row">
          <div class="plan-progress-track">
            <div class="plan-progress-fill" :style="{ width: `${progressPct}%` }" />
          </div>
          <span class="plan-progress-label">
            {{ doneCount }} / {{ activePlan.steps.length }} steps
            <span v-if="progressPct === 100" class="plan-complete-badge">Complete</span>
          </span>
        </div>

        <!-- Step notice (error / warning) -->
        <Transition name="notice-fade">
          <div v-if="stepNotice" class="step-notice" :class="`step-notice--${stepNotice.type}`">
            <svg viewBox="0 0 14 14" fill="none" width="13" height="13" style="flex-shrink:0">
              <circle v-if="stepNotice.type === 'warning'" cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.3"/>
              <path v-if="stepNotice.type === 'warning'" d="M7 4.5v3M7 9.5v.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              <path v-else d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>{{ stepNotice.message }}</span>
            <button class="notice-close" @click="stepNotice = null">✕</button>
          </div>
        </Transition>

        <!-- Steps list -->
        <div class="plan-steps">
          <PlanStepItem
            v-for="(step, i) in sortedSteps"
            :key="step.uuid"
            :step="step"
            :index="i"
            :is-admin="isAdmin || isSolo"
            @status-change="onStatusChange"
            @edit="onEditStep"
            @delete="onDeleteStep"
            @open-task="onOpenTask"
          />

          <!-- Add step row -->
          <div v-if="!addingStep" class="step-add-row" @click="addingStep = true">
            <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
              <path d="M6 1v10M1 6h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
            </svg>
            Add step
          </div>

          <div v-else class="step-add-form">
            <input
              ref="addStepInput"
              v-model="newStepTitle"
              class="step-add-input"
              placeholder="Step title…"
              maxlength="255"
              @keydown.enter.prevent="submitAddStep"
              @keydown.escape="addingStep = false"
            />
            <div class="step-add-actions">
              <button class="btn btn-sm btn-primary" :disabled="!newStepTitle.trim()" @click="submitAddStep">Add</button>
              <button class="btn btn-sm btn-ghost" @click="addingStep = false">Cancel</button>
            </div>
          </div>
        </div>

        <!-- Multiple plans selector (if more than one) -->
        <div v-if="planStore.plans.length > 1" class="plan-switcher">
          <span class="plan-switcher-label">Other plans:</span>
          <button
            v-for="p in planStore.plans"
            :key="p.uuid"
            class="plan-switcher-btn"
            :class="{ active: p.uuid === activePlan.uuid }"
            @click="activePlanUuid = p.uuid"
          >
            {{ p.title }}
          </button>
        </div>
      </div>
    </template>

    <!-- Inline step edit modal -->
    <div v-if="editingStep" class="modal-overlay" @click.self="editingStep = null">
      <div class="modal-dialog step-edit-dialog">
        <div class="modal-header">
          <h3>Edit Step</h3>
          <button class="modal-close" aria-label="Close dialog" @click="editingStep = null">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label class="field-label">Title</label>
            <input v-model="editForm.title" class="field-input" maxlength="255" />
          </div>
          <div class="field">
            <label class="field-label">Description</label>
            <textarea v-model="editForm.description" class="field-input field-textarea" rows="3" />
          </div>
          <div class="field-row-2">
            <div class="field">
              <label class="field-label">Priority</label>
              <select v-model="editForm.priority" class="field-input">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Status</label>
              <select v-model="editForm.status" class="field-input">
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="skipped">Skipped</option>
              </select>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn" @click="editingStep = null">Cancel</button>
          <button class="btn btn-primary" @click="submitEditStep">Save changes</button>
        </div>
      </div>
    </div>

    <CreatePlanModal
      v-if="showCreate"
      :project-id="projectId"
      @close="showCreate = false"
      @created="onPlanCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { usePlanStore } from '../../stores/plans'
import { useTaskStore } from '../../stores/tasks'
import { useProjectStore } from '../../stores/projects'
import { useMembersStore } from '../../stores/members'
import { useConfirm } from '../../composables/useConfirm'
import type { Plan, PlanStep, StepStatus, StepPriority, StepUpdate } from '../../types'
import PlanStepItem from './PlanStepItem.vue'
import CreatePlanModal from './CreatePlanModal.vue'
import Loading from '../common/Loading.vue'

const props = defineProps<{ projectId: number }>()

const planStore = usePlanStore()
const taskStore = useTaskStore()
const projectStore = useProjectStore()
const membersStore = useMembersStore()

const isAdmin = computed(() => {
  const role = membersStore.myMembership?.role
  return role === 'owner' || role === 'admin'
})
const isSolo = computed(() => membersStore.members.length <= 1)
const router = useRouter()
const route = useRoute()
const { confirm } = useConfirm()

function onOpenTask(taskUuid: string) {
  const projectUuid = projectStore.current?.uuid ?? (route.params.id as string)
  router.push({ path: `/projects/${projectUuid}`, query: { task: taskUuid } })
}

const showCreate = ref(false)
const activePlanUuid = ref<string | null>(null)
const addingStep = ref(false)
const newStepTitle = ref('')
const addStepInput = ref<HTMLInputElement>()
const stepNotice = ref<{ type: 'error' | 'warning'; message: string } | null>(null)
let noticeTimer: ReturnType<typeof setTimeout> | null = null

function showNotice(type: 'error' | 'warning', message: string) {
  if (noticeTimer) clearTimeout(noticeTimer)
  stepNotice.value = { type, message }
  noticeTimer = setTimeout(() => { stepNotice.value = null }, 6000)
}

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft', active: 'Active', completed: 'Completed', cancelled: 'Cancelled',
}

const activePlan = computed<Plan | null>(() => {
  if (!planStore.plans.length) return null
  if (activePlanUuid.value) {
    return planStore.plans.find((p) => p.uuid === activePlanUuid.value) ?? planStore.plans[0]
  }
  return planStore.plans[0]
})

const sortedSteps = computed(() =>
  activePlan.value ? [...activePlan.value.steps].sort((a, b) => a.step_order - b.step_order) : []
)

const doneCount = computed(() =>
  activePlan.value?.steps.filter((s) => s.status === 'completed' || s.status === 'skipped').length ?? 0
)

const progressPct = computed(() =>
  activePlan.value ? planStore.progress(activePlan.value) : 0
)

watch(() => props.projectId, async (id) => {
  activePlanUuid.value = null
  addingStep.value = false
  newStepTitle.value = ''
  await planStore.fetchByProject(id)
  if (planStore.plans.length) activePlanUuid.value = planStore.plans[0].uuid
}, { immediate: true })

watch(addingStep, async (val) => {
  if (val) {
    await nextTick()
    addStepInput.value?.focus()
  }
})

async function onStatusChange(step: PlanStep, status: StepStatus) {
  if (!activePlan.value) return
  try {
    const updated = await planStore.updateStep(activePlan.value.uuid, step.uuid, { status })
    // Show warning if backend flagged an unassigned linked task
    const updatedStep = updated?.steps?.find((s: PlanStep) => s.uuid === step.uuid)
    if (updatedStep?.warning) showNotice('warning', updatedStep.warning)
    // Refresh tasks so the Board tab reflects the synced status
    if (step.linked_task_id) await taskStore.fetchByProject(props.projectId)
  } catch (e: any) {
    const msg = e?.response?.data?.detail ?? e?.message ?? 'Could not update step.'
    showNotice('error', msg)
  }
}

async function submitAddStep() {
  if (!newStepTitle.value.trim() || !activePlan.value) return
  await planStore.addStep(activePlan.value.uuid, {
    title: newStepTitle.value.trim(),
    step_order: activePlan.value.steps.length,
  })
  newStepTitle.value = ''
  addingStep.value = false
}

async function handleDeletePlan() {
  if (!activePlan.value) return
  const ok = await confirm({
    title: 'Delete plan?',
    message: `"${activePlan.value.title}" will be removed. Tasks created by this plan will not be deleted.`,
    confirmLabel: 'Yes, delete plan',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await planStore.remove(activePlan.value.uuid)
  activePlanUuid.value = planStore.plans[0]?.uuid ?? null
}

function onPlanCreated(plan: Plan) {
  showCreate.value = false
  activePlanUuid.value = plan.uuid
}

// ── Step edit ────────────────────────────────────────────────────────────────

const editingStep = ref<PlanStep | null>(null)
const editForm = ref<{ title: string; description: string; priority: StepPriority; status: StepStatus }>({
  title: '', description: '', priority: 'medium', status: 'pending',
})

function onEditStep(step: PlanStep) {
  editingStep.value = step
  editForm.value = {
    title: step.title,
    description: step.description ?? '',
    priority: step.priority,
    status: step.status,
  }
}

async function submitEditStep() {
  if (!editingStep.value || !activePlan.value) return
  const data: StepUpdate = {
    title: editForm.value.title.trim() || undefined,
    description: editForm.value.description.trim() || null,
    priority: editForm.value.priority,
    status: editForm.value.status,
  }
  try {
    const updated = await planStore.updateStep(activePlan.value.uuid, editingStep.value.uuid, data)
    const updatedStep = updated?.steps?.find((s: PlanStep) => s.uuid === editingStep.value?.uuid)
    if (updatedStep?.warning) showNotice('warning', updatedStep.warning)
    if (editingStep.value?.linked_task_id && 'status' in data) {
      await taskStore.fetchByProject(props.projectId)
    }
    editingStep.value = null
  } catch (e: any) {
    const msg = e?.response?.data?.detail ?? e?.message ?? 'Could not update step.'
    showNotice('error', msg)
  }
}

async function onDeleteStep(step: PlanStep) {
  if (!activePlan.value) return
  const ok = await confirm({
    title: 'Delete step?',
    message: `"${step.title}" will be removed. The linked task will not be deleted.`,
    confirmLabel: 'Delete step',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await planStore.deleteStep(activePlan.value.uuid, step.uuid)
}
</script>

<style scoped>
.plan-panel {
  padding-top: 24px;
}

/* ── Step notice ── */
.step-notice {
  display: flex;
  align-items: flex-start;
  gap: 9px;
  padding: 11px 14px;
  border-radius: var(--radius);
  border: 1.5px solid;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 12px;
}
.step-notice--warning {
  background: rgba(255, 179, 0, 0.08);
  border-color: rgba(255, 179, 0, 0.35);
  color: #92400E;
}
.step-notice--error {
  background: var(--danger-bg);
  border-color: var(--danger-border);
  color: var(--danger);
}
:global([data-theme="dark"]) .step-notice--warning {
  background: rgba(255, 179, 0, 0.12);
  border-color: rgba(255, 179, 0, 0.3);
  color: #FFB300;
}
:global([data-theme="dark"]) .step-notice--error {
  background: rgba(255, 107, 120, 0.12);
  border-color: rgba(255, 107, 120, 0.3);
  color: #FF6B78;
}
.step-notice span { flex: 1; }
.notice-close {
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
  font-size: 11px;
  padding: 0;
  flex-shrink: 0;
  line-height: 1;
}
.notice-close:hover { opacity: 1; }

.notice-fade-enter-active, .notice-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.notice-fade-enter-from, .notice-fade-leave-to { opacity: 0; transform: translateY(-4px); }

/* ── Empty state ── */
.plan-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 64px 20px;
  text-align: center;
}

.plan-empty-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  color: var(--text-light);
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-empty-title { font-size: 15px; font-weight: 700; color: var(--text); }
.plan-empty-sub { font-size: 13.5px; color: var(--text-muted); max-width: 360px; line-height: 1.6; }

/* ── Plan view ── */
.plan-view {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.plan-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.plan-header-left { flex: 1; min-width: 0; }

.plan-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 5px;
}

.plan-title {
  font-size: 17px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
}

.plan-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: var(--radius-full);
}
.psb-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.psb-active    { background: rgba(0,186,124,0.14); color: #00845A; }
.psb-active .psb-dot { background: #00BA7C; }
.psb-draft     { background: rgba(100,116,139,0.12); color: #475569; }
.psb-draft .psb-dot { background: #94A3B8; }
.psb-completed { background: rgba(104,204,128,0.18); color: #1A5820; }
.psb-completed .psb-dot { background: #68CC80; }
.psb-cancelled { background: rgba(207,32,47,0.1); color: var(--danger); }
.psb-cancelled .psb-dot { background: var(--danger); }

.plan-description {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
}

.plan-header-right { display: flex; gap: 8px; flex-shrink: 0; }

/* ── Progress ── */
.plan-progress-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.plan-progress-track {
  flex: 1;
  height: 5px;
  background: var(--border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.plan-progress-fill {
  height: 100%;
  background: #1c1c1e;
  border-radius: var(--radius-full);
  transition: width 0.4s ease;
}
:global([data-theme="dark"]) .plan-progress-fill { background: #F7F9F9; }

.plan-progress-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 6px;
}

.plan-complete-badge {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: rgba(0, 186, 124, 0.14);
  color: #00845A;
}
:global([data-theme="dark"]) .plan-complete-badge { background: rgba(0,186,124,0.18); color: #00BA7C; }

/* ── Steps container ── */
.plan-steps {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* ── Add step ── */
.step-add-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 11px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-light);
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.step-add-row:hover { background: var(--bg); color: var(--text); }

.step-add-form {
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-top: 1px solid var(--border);
}

.step-add-input {
  flex: 1;
  padding: 7px 11px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-family: inherit;
  color: var(--text);
  outline: none;
}
.step-add-input:focus {
  border-color: var(--border-strong);
  box-shadow: 0 0 0 3px rgba(10, 11, 13, 0.06);
}
:global([data-theme="dark"]) .step-add-input:focus {
  border-color: #6E7D8C;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.06);
}

.step-add-actions { display: flex; gap: 6px; }

/* ── Plan switcher ── */
.plan-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.plan-switcher-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.plan-switcher-btn {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--border);
  background: var(--surface);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.plan-switcher-btn:hover { border-color: var(--border-strong); color: var(--text); }
.plan-switcher-btn.active { background: var(--text); color: var(--surface); border-color: var(--text); }

/* ── Step edit modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 11, 13, 0.55);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal-dialog {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 480px;
  box-shadow: var(--shadow-lg);
}

.step-edit-dialog { max-width: 440px; }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}
.modal-header h3 { font-size: 15px; font-weight: 700; color: var(--text); letter-spacing: -0.3px; }
.modal-close {
  width: 28px; height: 28px;
  border-radius: var(--radius-sm);
  background: var(--bg); border: 1.5px solid var(--border);
  color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background 0.12s;
}
.modal-close:hover { background: var(--border); }

.modal-body {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 12.5px; font-weight: 600; color: var(--text); }
.field-input {
  width: 100%; padding: 9px 12px;
  background: var(--bg); border: 1.5px solid var(--border);
  border-radius: var(--radius-sm); font-size: 13.5px;
  font-family: inherit; color: var(--text);
  transition: border-color 0.14s, box-shadow 0.14s; outline: none; resize: none;
}
.field-input:focus {
  border-color: var(--border-strong);
  box-shadow: 0 0 0 3px rgba(10, 11, 13, 0.06);
}
:global([data-theme="dark"]) .field-input:focus {
  border-color: #6E7D8C;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.06);
}
.field-textarea { resize: vertical; min-height: 72px; line-height: 1.5; }
.field-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 24px 20px;
  border-top: 1.5px solid var(--border);
}
</style>
