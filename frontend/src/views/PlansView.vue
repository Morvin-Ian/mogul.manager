<template>
  <div class="plans-page">
    <div class="page-head">
      <div>
        <h2>Plans</h2>
        <p>Turn a vague goal into a clear, prioritised action plan — powered by AI.</p>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" @click="showCreate = true">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          New plan
        </button>
      </div>
    </div>

    <!-- Explainer callout -->
    <div v-if="!dismissedExplainer" class="explainer-callout">
      <button class="explainer-dismiss" @click="dismissExplainer" title="Dismiss">×</button>
      <div class="explainer-body">
        <div class="explainer-col">
          <div class="explainer-icon explainer-icon--plan">
            <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
              <path d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 8l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <p class="explainer-label">Plans — the blueprint</p>
            <p class="explainer-text">You have a goal but no clear path. Describe it in plain language and the AI breaks it into ordered, prioritised steps. Use a plan when you're figuring out <em>what</em> needs doing.</p>
            <p class="explainer-example">"Build a university website proposal" → Research, Draft, Design, Quote…</p>
          </div>
        </div>

        <div class="explainer-arrow">
          <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
            <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>steps become</span>
        </div>

        <div class="explainer-col">
          <div class="explainer-icon explainer-icon--workspace">
            <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
              <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"/>
            </svg>
          </div>
          <div>
            <p class="explainer-label">Workspace → Tasks — the execution</p>
            <p class="explainer-text">You know what to do and you're doing it. Tasks live in projects inside a workspace and persist over time. Use this when you're in <em>execution mode</em>, tracking progress day to day.</p>
            <p class="explainer-example">Each completed plan step can create a task directly in your workspace.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.loading" class="plans-grid">
      <div v-for="n in 3" :key="n" class="plan-card sk-card">
        <div class="sk-line sk-title"></div>
        <div class="sk-line sk-desc"></div>
        <div class="sk-line sk-bar"></div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="!store.plans.length" class="empty">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <p class="empty-title">No plans yet</p>
      <p>Got a goal but not sure where to start? Describe it and the AI will generate a step-by-step action plan — then you can execute each step and track everything in your workspace.</p>
      <button class="btn btn-primary" @click="showCreate = true">Generate your first plan</button>
    </div>

    <!-- Grid -->
    <div v-else class="plans-grid">
      <div
        v-for="plan in store.plans"
        :key="plan.id"
        class="plan-card"
        @click="router.push(`/plans/${plan.id}`)"
      >
        <div class="plan-card-head">
          <span class="status-dot" :class="`dot-${plan.status}`"></span>
          <span class="plan-status-label">{{ plan.status }}</span>
          <button class="plan-delete" @click.stop="handleDelete(plan.id)" title="Delete plan">
            <svg viewBox="0 0 12 12" fill="none" width="12" height="12">
              <path d="M1.5 3h9M4.5 3V2a.5.5 0 01.5-.5h1a.5.5 0 01.5.5v1M3 3l.5 6.5a.5.5 0 00.5.5h4a.5.5 0 00.5-.5L9 3" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
        <h3 class="plan-title">{{ plan.title }}</h3>
        <p v-if="plan.description" class="plan-desc">{{ plan.description }}</p>

        <div class="plan-progress">
          <div class="progress-bar-wrap">
            <div class="progress-bar-fill" :style="{ width: store.progress(plan) + '%' }" :class="`fill-${plan.status}`"></div>
          </div>
          <span class="progress-label">{{ store.progress(plan) }}%</span>
        </div>

        <div class="plan-stats">
          <span class="stat">
            <svg viewBox="0 0 12 12" fill="none" width="11" height="11"><circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.2"/><path d="M6 4v2.5l1.5 1" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
            {{ plan.steps.length }} steps
          </span>
          <span class="stat">
            <svg viewBox="0 0 12 12" fill="none" width="11" height="11"><path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
            {{ plan.steps.filter(s => s.status === 'completed').length }} done
          </span>
          <span v-if="plan.steps.some(s => s.status === 'running')" class="stat stat-running">
            <span class="running-dot"></span> In progress
          </span>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h2>New plan</h2>
          <button class="modal-close" @click="showCreate = false">×</button>
        </div>
        <p class="modal-hint">Describe a goal in plain language — the AI will decompose it into prioritised, ordered steps automatically.</p>
        <form @submit.prevent="handleCreate" novalidate>
          <div class="form-group">
            <label for="plan-title">Goal</label>
            <input
              id="plan-title"
              v-model="form.title"
              type="text"
              placeholder="e.g. Build a university website proposal"
              required
              autofocus
            />
          </div>
          <div class="form-group">
            <label for="plan-desc">Extra context <span class="optional">(optional)</span></label>
            <textarea
              id="plan-desc"
              v-model="form.description"
              rows="3"
              placeholder="Any additional details that help the AI plan better…"
            ></textarea>
          </div>
          <p v-if="createError" class="form-error">{{ createError }}</p>
          <div class="form-actions">
            <button type="button" class="btn" @click="showCreate = false">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="creating || !form.title.trim()">
              <span v-if="creating" class="spinner spinner-white"></span>
              {{ creating ? 'Generating plan…' : 'Generate plan' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlanStore } from '../stores/plans'

const store = usePlanStore()
const router = useRouter()

const dismissedExplainer = ref(localStorage.getItem('plans_explainer_dismissed') === '1')
function dismissExplainer() {
  dismissedExplainer.value = true
  localStorage.setItem('plans_explainer_dismissed', '1')
}

onMounted(() => store.fetchAll())

const showCreate = ref(false)
const creating = ref(false)
const createError = ref<string | null>(null)
const form = ref({ title: '', description: '' })

async function handleCreate() {
  createError.value = null
  creating.value = true
  try {
    const plan = await store.create({
      title: form.value.title.trim(),
      description: form.value.description.trim() || null,
    })
    showCreate.value = false
    form.value = { title: '', description: '' }
    router.push(`/plans/${plan.id}`)
  } catch (e) {
    createError.value = (e as Error).message
  } finally {
    creating.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('Delete this plan?')) return
  await store.remove(id)
}
</script>

<style scoped>
.plans-page {
  padding: 36px 32px 80px;
  max-width: 960px;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 4px;
}

.plan-card {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.12s;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: var(--shadow-xs);
}

.plan-card:hover {
  border-color: var(--primary-border);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.plan-card-head {
  display: flex;
  align-items: center;
  gap: 7px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-active    { background: #3830A0; }
.dot-completed { background: #1A5820; }
.dot-draft     { background: var(--text-light); }
.dot-cancelled { background: #601010; }

.plan-status-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-light);
  flex: 1;
}

.plan-delete {
  opacity: 0;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-light);
  padding: 3px;
  border-radius: 5px;
  display: flex;
  transition: opacity 0.1s, color 0.1s;
}
.plan-card:hover .plan-delete { opacity: 1; }
.plan-delete:hover { color: var(--danger); }

.plan-title {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
  line-height: 1.3;
}

.plan-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.plan-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar-wrap {
  flex: 1;
  height: 5px;
  background: var(--bg);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}
.fill-active    { background: #3830A0; }
.fill-completed { background: #1A5820; }
.fill-draft     { background: var(--text-light); }
.fill-cancelled { background: #601010; }

.progress-label {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--text-muted);
  min-width: 30px;
  text-align: right;
}

.plan-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-light);
}

.stat-running { color: #3830A0; }

.running-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #3830A0;
  animation: pulse 1s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.75)} }

/* Explainer callout */
.explainer-callout {
  position: relative;
  background: #F4F4F6;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 24px;
}

.explainer-dismiss {
  position: absolute;
  top: 10px;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  color: var(--text-light);
  line-height: 1;
  padding: 2px 6px;
  border-radius: 4px;
  transition: color 0.1s, background 0.1s;
}
.explainer-dismiss:hover { color: var(--text); background: var(--border); }

.explainer-body {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
}

.explainer-col {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  flex: 1;
  min-width: 200px;
}

.explainer-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.explainer-icon--plan      { background: #F2E0CC; border: 1px solid #CFA070; color: #7A3410; }
.explainer-icon--workspace { background: #E5E2FF; border: 1px solid #B0A8E8; color: #3830A0; }

.explainer-label {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 4px;
}

.explainer-text {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.55;
  margin-bottom: 6px;
}

.explainer-example {
  font-size: 11.5px;
  color: #3830A0;
  font-style: italic;
}

.explainer-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-light);
  padding-top: 8px;
  flex-shrink: 0;
}
.explainer-arrow span {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* Empty */
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px 40px;
  text-align: center;
}

.empty-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  background: #E5E2FF;
  border: 1px solid #B0A8E8;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3830A0;
}

.empty p { font-size: 14px; color: var(--text-muted); max-width: 340px; line-height: 1.6; }

/* Modal extras */
.modal-hint {
  font-size: 13.5px;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 20px;
  margin-top: -8px;
}

.optional { font-weight: 400; color: var(--text-light); font-size: 12px; }

/* Spinner */
.spinner { display: inline-block; width: 13px; height: 13px; border: 2px solid rgba(0,0,0,.1); border-top-color: var(--primary); border-radius: 50%; animation: spin .65s linear infinite; }
.spinner-white { border-color: rgba(255,255,255,.3); border-top-color: #fff; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Skeleton */
.sk-card { cursor: default; pointer-events: none; }
@keyframes shimmer { 0% { background-position: -300px 0; } 100% { background-position: 300px 0; } }
.sk-line { background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%); background-size: 300px 100%; animation: shimmer 1.4s ease-in-out infinite; border-radius: 4px; }
.sk-title { height: 14px; width: 70%; }
.sk-desc  { height: 11px; width: 90%; }
.sk-bar   { height: 5px;  width: 100%; border-radius: 99px; }

@media (max-width: 600px) { .plans-page { padding: 24px 16px 60px; } }
</style>
