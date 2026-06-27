<template>
  <div class="plans-view">
    <div class="page-head">
      <div class="page-head-text">
        <h2>Plans Overview</h2>
        <p>AI-generated project plans across all your workspaces.</p>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading plans…</div>

    <template v-else-if="plansByWorkspace.length === 0">
      <div class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" width="32" height="32">
            <path d="M12 2l2 6h6l-5 3.5 2 6L12 14l-5 3.5 2-6L4 8h6l2-6z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>No plans yet</h3>
        <p>Open a project and generate an AI plan to break goals into actionable steps.</p>
      </div>
    </template>

    <div v-else class="plans-list">
      <div v-for="group in plansByWorkspace" :key="group.workspace.id" class="ws-group">
        <h3 class="ws-group-title">{{ group.workspace.title }}</h3>
        <div class="plan-cards">
          <div
            v-for="plan in group.plans"
            :key="plan.uuid"
            class="plan-card"
            @click="$router.push(`/plans/${plan.uuid}`)"
          >
            <div class="plan-card-header">
              <span class="plan-card-title">{{ plan.title }}</span>
              <span class="plan-status-badge" :class="`psb-${plan.status}`">{{ plan.status }}</span>
            </div>
            <p v-if="plan.description" class="plan-card-desc">{{ plan.description }}</p>
            <div class="plan-card-meta">
              <span class="plan-card-project">{{ plan.project_title }}</span>
              <div class="plan-card-progress">
                <div class="plan-card-bar">
                  <div class="plan-card-fill" :style="{ width: progress(plan) + '%' }"></div>
                </div>
                <span class="plan-card-pct">{{ progress(plan) }}%</span>
              </div>
            </div>
            <div class="plan-card-steps">
              {{ plan.steps.filter(s => s.status === 'completed' || s.status === 'skipped').length }}/{{ plan.steps.length }} steps done
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useWorkspaceStore } from '../stores/workspaces'
import { usePlanStore } from '../stores/plans'
import { get } from '../stores/client'
import type { Plan, Workspace, Project } from '../types'

const workspaceStore = useWorkspaceStore()
const planStore = usePlanStore()
const loading = ref(false)
const allPlans = ref<Plan[]>([])
const projects = ref<Project[]>([])

async function load() {
  loading.value = true
  try {
    await workspaceStore.fetchAll()
    const wsIds = workspaceStore.workspaces.map(ws => ws.id)
    const projectArrays = await Promise.all(wsIds.map(id => get<Project[]>(`/projects?workspace_id=${id}`)))
    projects.value = projectArrays.flat()
    const projIds = projects.value.map(p => p.id)
    const planArrays = await Promise.all(projIds.map(id => get<Plan[]>(`/plans?project_id=${id}`)))
    allPlans.value = planArrays.flat()
  } catch (e) {
    console.error('Failed to load plans', e)
  } finally {
    loading.value = false
  }
}

const plansByWorkspace = computed(() => {
  const wsMap = new Map(workspaceStore.workspaces.map(ws => [ws.id, ws]))
  const projMap = new Map(projects.value.map(p => [p.id, p]))
  const groups: { workspace: Workspace; plans: Plan[] }[] = []
  for (const ws of workspaceStore.workspaces) {
    const wsProjects = projects.value.filter(p => p.workspace_id === ws.id)
    const wsPlans = allPlans.value.filter(p => wsProjects.some(pr => pr.id === p.project_id))
    if (wsPlans.length > 0) {
      groups.push({ workspace: ws, plans: wsPlans })
    }
  }
  return groups
})

function progress(plan: Plan): number {
  return planStore.progress(plan)
}

onMounted(load)
</script>

<style scoped>
.plans-view { padding: 36px 40px 80px; }
.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; margin-bottom: 28px; }
.page-head-text h2 { font-size: 26px; font-weight: 800; color: var(--text); letter-spacing: -0.6px; line-height: 1.2; }
.page-head-text p { font-size: 13.5px; color: var(--text-muted); margin-top: 4px; }
.loading-state { text-align: center; padding: 60px; color: var(--text-muted); font-size: 14px; }
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 80px 20px; text-align: center; }
.empty-state h3 { font-size: 18px; font-weight: 700; color: var(--text); }
.empty-state p { color: var(--text-muted); font-size: 14px; max-width: 320px; line-height: 1.6; }
.empty-icon { width: 64px; height: 64px; background: #EDE9FE; border: 1.5px solid #C4B5FD; border-radius: 18px; display: flex; align-items: center; justify-content: center; color: #6D28D9; }
.ws-group { margin-bottom: 32px; }
.ws-group-title { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1.5px solid var(--border); }
.plan-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 14px; }
.plan-card { background: var(--surface); border: 1.5px solid var(--border); border-radius: 14px; padding: 18px; cursor: pointer; transition: box-shadow 0.15s, transform 0.15s; }
.plan-card:hover { box-shadow: 0 6px 20px rgba(10,11,13,0.08); transform: translateY(-1px); }
.plan-card-header { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.plan-card-title { font-size: 15px; font-weight: 600; color: var(--text); }
.plan-card-desc { font-size: 12.5px; color: var(--text-muted); line-height: 1.5; margin-bottom: 10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.plan-card-meta { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.plan-card-project { font-size: 11.5px; color: var(--text-light); font-weight: 500; }
.plan-card-progress { display: flex; align-items: center; gap: 6px; flex: 1; max-width: 140px; }
.plan-card-bar { flex: 1; height: 5px; background: var(--border); border-radius: 99px; overflow: hidden; }
.plan-card-fill { height: 100%; background: #10B981; border-radius: 99px; transition: width 0.4s ease; }
.plan-card-pct { font-size: 11px; font-weight: 600; color: var(--text-muted); min-width: 30px; text-align: right; }
.plan-card-steps { font-size: 11px; color: var(--text-light); margin-top: 8px; }
.plan-status-badge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 999px; font-size: 10.5px; font-weight: 600; }
.psb-active { background: #D5EDF0; color: #1A7068; }
.psb-draft { background: #E2E8F0; color: #475569; }
.psb-completed { background: #D8F0DC; color: #1A5820; }
.psb-cancelled { background: #F5DEDE; color: #601010; }
:global([data-theme="dark"]) .plan-card { background: #1A2D42; border-color: rgba(91,155,255,0.20); }
:global([data-theme="dark"]) .plan-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
</style>
