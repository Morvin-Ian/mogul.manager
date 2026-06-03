<template>
  <div class="step-row" :class="[`step-row--${step.status}`, { 'step-row--expanded': expanded }]">
    <!-- Order + status toggle -->
    <div class="step-left">
      <span class="step-order">{{ index + 1 }}</span>
      <button
        class="step-status-btn"
        :class="{ 'step-status-btn--locked': isLocked }"
        :title="nextStatusLabel"
        @click="cycleStatus"
      >
        <!-- completed -->
        <svg v-if="step.status === 'completed'" viewBox="0 0 16 16" fill="none" width="16" height="16">
          <circle cx="8" cy="8" r="7" fill="var(--step-done-bg)" stroke="var(--step-done-stroke)" stroke-width="1.5"/>
          <path d="M5 8.5l2 2 4-4" stroke="var(--step-done-color)" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <!-- in_progress -->
        <svg v-else-if="step.status === 'in_progress'" viewBox="0 0 16 16" fill="none" width="16" height="16">
          <circle cx="8" cy="8" r="7" fill="var(--step-prog-bg)" stroke="var(--step-prog-stroke)" stroke-width="1.5"/>
          <circle cx="8" cy="8" r="2.5" fill="var(--step-prog-color)"/>
        </svg>
        <!-- skipped -->
        <svg v-else-if="step.status === 'skipped'" viewBox="0 0 16 16" fill="none" width="16" height="16">
          <circle cx="8" cy="8" r="7" fill="var(--step-skip-bg)" stroke="var(--step-skip-stroke)" stroke-width="1.5"/>
          <path d="M5.5 8h5" stroke="var(--step-skip-color)" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        <!-- pending -->
        <svg v-else viewBox="0 0 16 16" fill="none" width="16" height="16">
          <circle cx="8" cy="8" r="7" stroke="var(--border-strong)" stroke-width="1.5" fill="transparent"/>
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="step-content" @click="expanded = !expanded">
      <div class="step-main-row">
        <span class="step-title" :class="{ 'step-title--done': step.status === 'completed' || step.status === 'skipped' }">
          {{ step.title }}
        </span>
        <div class="step-chips">
          <span class="step-status-badge" :class="`ssb-${step.status}`">
            {{ STATUS_LABELS[step.status] }}
          </span>
          <span class="step-priority" :class="`sp-${step.priority}`">{{ step.priority }}</span>
          <button
            v-if="step.linked_task_uuid"
            class="step-task-chip"
            @click.stop="$emit('open-task', step.linked_task_uuid)"
          >
            <svg viewBox="0 0 10 10" fill="none" width="9" height="9">
              <rect x="0.5" y="0.5" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
              <path d="M3 5l1.5 1.5 3-3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            {{ step.linked_task_title ?? 'Task' }}
          </button>
          <span v-else class="step-no-task">No task</span>
        </div>
      </div>

      <!-- Expanded description -->
      <div v-if="expanded && step.description" class="step-description">
        {{ step.description }}
      </div>
      <div v-if="expanded && step.agent_notes" class="step-agent-notes">
        <span class="notes-label">AI notes</span> {{ step.agent_notes }}
      </div>
    </div>

    <!-- Hover actions -->
    <div class="step-actions">
      <button class="step-action-btn" title="Edit step" @click.stop="$emit('edit', step)">
        <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
          <path d="M8 1.5l2.5 2.5L4 10.5H1.5V8L8 1.5z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <button class="step-action-btn step-action-btn--danger" title="Delete step" @click.stop="$emit('delete', step)">
        <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
          <path d="M2 3h8M5 3V1.5h2V3M4 3v6.5h4V3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { PlanStep, StepStatus } from '../../types'

const props = defineProps<{ step: PlanStep; index: number; isAdmin?: boolean }>()
const emit = defineEmits<{
  'status-change': [step: PlanStep, status: StepStatus]
  'edit': [step: PlanStep]
  'delete': [step: PlanStep]
  'open-task': [taskUuid: string]
}>()

const expanded = ref(false)

const STATUS_LABELS: Record<StepStatus, string> = {
  pending: 'Pending',
  in_progress: 'In Progress',
  completed: 'Completed',
  skipped: 'Skipped',
}

// Admin full cycle: pending → in_progress → completed → skipped → pending
// Member restricted: pending ↔ in_progress only; completed/skipped are read-only
const ADMIN_CYCLE: Record<StepStatus, StepStatus> = {
  pending: 'in_progress',
  in_progress: 'completed',
  completed: 'skipped',
  skipped: 'pending',
}

const MEMBER_CYCLE: Record<StepStatus, StepStatus> = {
  pending: 'in_progress',
  in_progress: 'pending',   // can only go back, not forward to completed
  completed: 'completed',   // locked — clicking does nothing
  skipped: 'skipped',       // locked — clicking does nothing
}

const STATUS_NEXT_LABEL_ADMIN: Record<StepStatus, string> = {
  pending: 'Mark in progress',
  in_progress: 'Mark completed',
  completed: 'Mark skipped',
  skipped: 'Reset to pending',
}

const STATUS_NEXT_LABEL_MEMBER: Record<StepStatus, string> = {
  pending: 'Mark in progress',
  in_progress: 'Mark pending',
  completed: 'Only admins can change this',
  skipped: 'Only admins can change this',
}

const nextStatusLabel = computed(() =>
  props.isAdmin
    ? STATUS_NEXT_LABEL_ADMIN[props.step.status]
    : STATUS_NEXT_LABEL_MEMBER[props.step.status]
)

const isLocked = computed(() =>
  !props.isAdmin && (props.step.status === 'completed' || props.step.status === 'skipped')
)

function cycleStatus() {
  if (isLocked.value) return
  const cycle = props.isAdmin ? ADMIN_CYCLE : MEMBER_CYCLE
  emit('status-change', props.step, cycle[props.step.status])
}
</script>

<style scoped>
/* ── Status color tokens ── */
.step-row {
  --step-done-bg:     rgba(0, 186, 124, 0.14);
  --step-done-stroke: rgba(0, 186, 124, 0.5);
  --step-done-color:  #00845A;
  --step-prog-bg:     rgba(245, 158, 11, 0.12);
  --step-prog-stroke: rgba(245, 158, 11, 0.45);
  --step-prog-color:  #A87800;
  --step-skip-bg:     rgba(138, 145, 158, 0.12);
  --step-skip-stroke: rgba(138, 145, 158, 0.4);
  --step-skip-color:  #8A919E;
}

:global([data-theme="dark"]) .step-row {
  --step-done-bg:     rgba(0, 186, 124, 0.18);
  --step-done-stroke: rgba(0, 186, 124, 0.55);
  --step-done-color:  #00BA7C;
  --step-prog-bg:     rgba(255, 179, 0, 0.15);
  --step-prog-stroke: rgba(255, 179, 0, 0.45);
  --step-prog-color:  #FFB300;
  --step-skip-bg:     rgba(110, 125, 140, 0.15);
  --step-skip-stroke: rgba(110, 125, 140, 0.4);
  --step-skip-color:  #6E7D8C;
}

.step-row {
  display: flex;
  align-items: flex-start;
  gap: 0;
  padding: 13px 16px;
  border-bottom: 1px solid var(--border);
  transition: background 0.12s;
  position: relative;
}
.step-row:last-child { border-bottom: none; }
.step-row:hover { background: var(--bg); }
.step-row:hover .step-actions { opacity: 1; }

.step-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding-top: 1px;
}

.step-order {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-light);
  width: 16px;
  text-align: right;
  letter-spacing: -0.2px;
  flex-shrink: 0;
}

.step-status-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: opacity 0.12s, transform 0.1s;
  flex-shrink: 0;
}
.step-status-btn:hover:not(.step-status-btn--locked) { opacity: 0.75; transform: scale(1.1); }
.step-status-btn--locked { cursor: not-allowed; opacity: 0.5; }

.step-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
  padding: 0 10px;
}

.step-main-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.step-title {
  font-size: 14.5px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.2px;
  line-height: 1.4;
  flex: 1;
  min-width: 0;
}
.step-title--done {
  color: var(--text-light);
  text-decoration: line-through;
  text-decoration-color: var(--border-strong);
  text-decoration-thickness: 1px;
}
:global([data-theme="dark"]) .step-title--done {
  /* In dark mode --text-light and --border-strong are the same #6E7D8C,
     making the line invisible or harsh depending on rendering.
     Use a very subtle translucent overlay instead. */
  text-decoration-color: rgba(110, 125, 140, 0.35);
}

.step-chips {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* ── Status badge ── */
.step-status-badge {
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  text-transform: capitalize;
  white-space: nowrap;
}
.ssb-pending     { background: rgba(100,116,139,0.12); color: #475569; }
.ssb-in_progress { background: rgba(245,158,11,0.12);  color: #A87800; }
.ssb-completed   { background: rgba(0,186,124,0.14);   color: #00845A; }
.ssb-skipped     { background: rgba(138,145,158,0.12); color: #8A919E; text-decoration: line-through; }

:global([data-theme="dark"]) .ssb-pending     { background: rgba(148,163,184,0.12); color: #94A3B8; }
:global([data-theme="dark"]) .ssb-in_progress { background: rgba(255,179,0,0.14);   color: #FFB300; }
:global([data-theme="dark"]) .ssb-completed   { background: rgba(0,186,124,0.18);   color: #00BA7C; }
:global([data-theme="dark"]) .ssb-skipped     { background: rgba(110,125,140,0.15); color: #6E7D8C; text-decoration: line-through; text-decoration-color: rgba(110,125,140,0.35); text-decoration-thickness: 1px; }

.step-priority {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.sp-low    { background: rgba(5, 177, 105, 0.12);  color: #047857; }
.sp-medium { background: rgba(255, 179, 0, 0.14);  color: #A87800; }
.sp-high   { background: rgba(239, 68, 68, 0.12);  color: #DC2626; }
.sp-urgent { background: rgba(207, 32, 47, 0.15);  color: #CF202F; }

:global([data-theme="dark"]) .sp-low    { background: rgba(0, 186, 124, 0.15); color: #00BA7C; }
:global([data-theme="dark"]) .sp-medium { background: rgba(255, 179, 0, 0.15); color: #FFB300; }
:global([data-theme="dark"]) .sp-high   { background: rgba(239, 68, 68, 0.15); color: #F87171; }
:global([data-theme="dark"]) .sp-urgent { background: rgba(255, 107, 120, 0.18); color: #FF6B78; }

.step-task-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  background: var(--bg);
  color: var(--text-muted);
  border: 1px solid var(--border);
  text-decoration: none;
  white-space: nowrap;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
}
.step-task-chip:hover { background: var(--surface); border-color: var(--border-strong); color: var(--text); text-decoration: none; }

.step-no-task {
  font-size: 11px;
  color: var(--text-light);
  font-style: italic;
}

.step-description {
  margin-top: 6px;
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.6;
}

.step-agent-notes {
  margin-top: 4px;
  font-size: 11.5px;
  color: var(--text-light);
  line-height: 1.5;
}
.notes-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-light);
  margin-right: 4px;
}

/* ── Hover actions ── */
.step-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.14s;
  padding-top: 1px;
}

.step-action-btn {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  background: var(--surface);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s;
}
.step-action-btn:hover { background: var(--bg); color: var(--text); border-color: var(--border-strong); }
.step-action-btn--danger:hover { background: var(--danger-bg); color: var(--danger); border-color: var(--danger-border); }
</style>
