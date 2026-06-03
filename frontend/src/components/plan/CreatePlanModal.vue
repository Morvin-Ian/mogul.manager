<template>
  <div class="modal-overlay" @click.self="!generating && $emit('close')">
    <!-- Form state -->
    <div v-if="!generating" class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title-row">
          <span class="modal-icon">
            <svg viewBox="0 0 16 16" fill="none" width="15" height="15">
              <path d="M8 1l1.5 4.5H14l-3.5 2.5 1.5 4.5L8 10l-4 2.5 1.5-4.5L2 5.5h4.5L8 1z" fill="currentColor"/>
            </svg>
          </span>
          <h3>Generate a Plan</h3>
        </div>
        <button class="modal-close" @click="$emit('close')">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
            <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <p class="modal-sub">AI will break your goal into ordered steps and create linked tasks automatically.</p>
        <div class="field">
          <label class="field-label">Plan goal <span class="required">*</span></label>
          <input
            ref="titleRef"
            v-model="form.title"
            class="field-input"
            placeholder="e.g. Launch the beta version by end of month"
            maxlength="255"
            @keydown.enter.prevent="submit"
          />
        </div>
        <div class="field">
          <label class="field-label">Additional context <span class="field-optional">(optional)</span></label>
          <textarea
            v-model="form.description"
            class="field-input field-textarea"
            placeholder="Any constraints, team details, or priorities to consider…"
            rows="3"
          />
        </div>
        <p v-if="errorMsg" class="field-error">{{ errorMsg }}</p>
      </div>
      <div class="modal-footer">
        <button class="btn" @click="$emit('close')">Cancel</button>
        <button class="btn btn-primary" :disabled="!form.title.trim()" @click="submit">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
            <path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          Generate Plan
        </button>
      </div>
    </div>

    <!-- AI generation panel (inspired by image) -->
    <div v-else class="gen-panel">
      <div class="gen-header">
        <div class="gen-title">
          <span class="gen-spark">✦</span>
          <span>AI is generating your plan</span>
        </div>
        <span class="gen-timer">{{ timerDisplay }}</span>
      </div>

      <div class="gen-steps">
        <div
          v-for="(step, i) in analysisSteps"
          :key="i"
          class="gen-step"
          :class="{
            'gen-step--done': checkedCount > i,
            'gen-step--active': checkedCount === i,
          }"
        >
          <span class="gen-step-icon">
            <svg v-if="checkedCount > i" viewBox="0 0 14 14" fill="none" width="10" height="10">
              <path d="M2.5 7l3 3 6-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="checkedCount === i" viewBox="0 0 14 14" fill="none" width="10" height="10">
              <circle cx="7" cy="7" r="2.5" fill="currentColor"/>
            </svg>
          </span>
          <span class="gen-step-label">{{ step }}</span>
        </div>
      </div>

      <div class="gen-stream">
        <p class="gen-stream-text">{{ streamText }}</p>
      </div>

      <div class="gen-footer">
        <button class="gen-cancel-btn" @click="cancel">Cancel generation</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import type { Plan } from '../../types'

const props = defineProps<{
  projectId: number
}>()

const emit = defineEmits<{
  close: []
  created: [plan: Plan]
}>()

const form = ref({ title: '', description: '' })
const errorMsg = ref('')
const generating = ref(false)
const titleRef = ref<HTMLInputElement>()

onMounted(() => titleRef.value?.focus())

// ── Generation panel state ──────────────────────────────────────────────────

const analysisSteps = [
  'Analysing project goals',
  'Reviewing existing tasks',
  'Building step sequence',
  'Linking tasks to steps',
]

const streamMessages = [
  'Breaking down the goal into executable steps. Considering dependencies to ensure logical sequencing…',
  'Identifying which existing tasks align with planned steps. Preparing to link where coverage exists…',
  'Ordering steps by priority and dependency. Generating task descriptions for new work items…',
  'Finalising the plan structure. Creating tasks and establishing links between steps…',
]

const checkedCount = ref(0)
const streamText = ref(streamMessages[0])
const elapsedSeconds = ref(0)

let timerInterval: ReturnType<typeof setInterval> | null = null
let stepInterval: ReturnType<typeof setInterval> | null = null
let cancelled = false
let apiResolve: (() => void) | null = null

const timerDisplay = computed(() => {
  const m = Math.floor(elapsedSeconds.value / 60)
  const s = elapsedSeconds.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

function startAnimations() {
  timerInterval = setInterval(() => { elapsedSeconds.value++ }, 1000)

  let step = 0
  stepInterval = setInterval(() => {
    if (step < analysisSteps.length) {
      checkedCount.value = step + 1
      streamText.value = streamMessages[Math.min(step + 1, streamMessages.length - 1)]
      step++
    }
  }, 1800)
}

function stopAnimations() {
  if (timerInterval) clearInterval(timerInterval)
  if (stepInterval) clearInterval(stepInterval)
}

onUnmounted(stopAnimations)

// ── Submit ──────────────────────────────────────────────────────────────────

import { usePlanStore } from '../../stores/plans'
const planStore = usePlanStore()

async function submit() {
  if (!form.value.title.trim()) return
  errorMsg.value = ''
  generating.value = true
  cancelled = false
  checkedCount.value = 0
  elapsedSeconds.value = 0
  streamText.value = streamMessages[0]
  startAnimations()

  try {
    const plan = await planStore.create({
      title: form.value.title.trim(),
      description: form.value.description.trim() || null,
      project_id: props.projectId,
    })
    if (!cancelled) {
      checkedCount.value = analysisSteps.length
      // Brief pause so user sees all steps checked
      await new Promise((r) => setTimeout(r, 600))
      emit('created', plan)
    }
  } catch (e: any) {
    generating.value = false
    stopAnimations()
    errorMsg.value = e?.message ?? 'Something went wrong. Please try again.'
  } finally {
    stopAnimations()
  }
}

function cancel() {
  cancelled = true
  stopAnimations()
  generating.value = false
  emit('close')
}
</script>

<style scoped>
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

/* ── Form dialog ── */
.modal-dialog {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 480px;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}

.modal-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-icon {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--bg);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-header h3 {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.modal-close {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--bg);
  border: 1.5px solid var(--border);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.modal-close:hover { background: var(--border); color: var(--text); }

.modal-body {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.modal-sub {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
}

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text);
  letter-spacing: -0.1px;
}
.required { color: var(--danger); }
.field-optional { font-weight: 400; color: var(--text-light); font-size: 12px; }
.field-input {
  width: 100%;
  padding: 9px 12px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 13.5px;
  font-family: inherit;
  color: var(--text);
  transition: border-color 0.14s, box-shadow 0.14s;
  outline: none;
  resize: none;
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
.field-error { font-size: 12.5px; color: var(--danger); font-weight: 500; }

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 24px 20px;
  border-top: 1.5px solid var(--border);
}

/* ── AI generation panel ── */
.gen-panel {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 460px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  font-family: 'Outfit', -apple-system, system-ui, sans-serif;
}

.gen-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1.5px solid var(--border);
}

.gen-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
}

.gen-spark {
  color: var(--text-muted);
  font-size: 16px;
  animation: pulse-spark 1.6s ease-in-out infinite;
}

@keyframes pulse-spark {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.35; }
}

.gen-timer {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-light);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.5px;
  font-family: 'Fira Mono', monospace;
}

.gen-steps {
  padding: 14px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.gen-step {
  display: flex;
  align-items: center;
  gap: 10px;
}

.gen-step-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: transparent;
  border: 1.5px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.3s, border-color 0.3s, color 0.3s;
}

.gen-step--done .gen-step-icon {
  background: rgba(0, 186, 124, 0.14);
  border-color: rgba(0, 186, 124, 0.45);
  color: #00845A;
}
:global([data-theme="dark"]) .gen-step--done .gen-step-icon {
  background: rgba(0, 186, 124, 0.18);
  border-color: rgba(0, 186, 124, 0.5);
  color: #00BA7C;
}

.gen-step--active .gen-step-icon {
  background: var(--bg);
  border-color: var(--border-strong);
  color: var(--text-muted);
}

.gen-step-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-light);
  transition: color 0.3s;
  letter-spacing: -0.1px;
}
.gen-step--done .gen-step-label {
  color: var(--text);
  font-weight: 600;
}
.gen-step--active .gen-step-label {
  color: var(--text-muted);
}

.gen-stream {
  margin: 0 20px 16px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 14px;
  min-height: 64px;
}

.gen-stream-text {
  font-size: 13px;
  font-family: 'Outfit', -apple-system, system-ui, sans-serif;
  font-style: italic;
  color: var(--text-muted);
  line-height: 1.65;
  transition: opacity 0.4s;
}

.gen-footer {
  padding: 12px 20px 18px;
  display: flex;
  justify-content: flex-end;
  border-top: 1.5px solid var(--border);
}

.gen-cancel-btn {
  padding: 8px 16px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 9px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 600;
  font-family: 'Outfit', inherit;
  cursor: pointer;
  transition: background 0.14s, color 0.14s, border-color 0.14s;
  box-shadow: 0 1px 2px rgba(10,11,13,0.06);
}
.gen-cancel-btn:hover {
  background: var(--bg);
  color: var(--text);
  border-color: var(--border-strong);
}
</style>
