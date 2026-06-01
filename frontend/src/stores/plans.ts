import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Plan, PlanCreate, PlanStep, StepStatus } from '../types'
import { get, post, patch, del } from './client'

export const usePlanStore = defineStore('plans', () => {
  const plans = ref<Plan[]>([])
  const current = ref<Plan | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      plans.value = await get<Plan[]>('/plans')
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(uuid: string) {
    loading.value = true
    try {
      current.value = await get<Plan>(`/plans/${uuid}`)
      const idx = plans.value.findIndex((p) => p.uuid === uuid)
      if (idx !== -1) plans.value[idx] = current.value
      return current.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(data: PlanCreate): Promise<Plan> {
    const plan = await post<Plan>('/plans', data)
    plans.value.unshift(plan)
    return plan
  }

  async function remove(uuid: string) {
    await del(`/plans/${uuid}`)
    plans.value = plans.value.filter((p) => p.uuid !== uuid)
    if (current.value?.uuid === uuid) current.value = null
  }

  async function updateStep(planUuid: string, stepUuid: string, status: StepStatus, notes?: string): Promise<PlanStep> {
    const step = await patch<PlanStep>(`/plans/${planUuid}/steps/${stepUuid}`, {
      status,
      agent_notes: notes ?? null,
    })
    // Patch step in local state
    const plan = plans.value.find((p) => p.uuid === planUuid) ?? current.value
    if (plan) {
      const i = plan.steps.findIndex((s) => s.uuid === stepUuid)
      if (i !== -1) plan.steps[i] = step
    }
    return step
  }

  function progress(plan: Plan): number {
    if (!plan.steps.length) return 0
    const done = plan.steps.filter((s) => s.status === 'completed' || s.status === 'skipped').length
    return Math.round((done / plan.steps.length) * 100)
  }

  return { plans, current, loading, error, fetchAll, fetchOne, create, remove, updateStep, progress }
})
