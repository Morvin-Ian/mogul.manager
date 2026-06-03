import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Plan, PlanCreate, PlanUpdate, PlanStep, StepUpdate, StepCreate } from '../types'
import { get, post, patch, del } from './client'

export const usePlanStore = defineStore('plans', () => {
  const plans = ref<Plan[]>([])
  const current = ref<Plan | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchByProject(projectId: number) {
    plans.value = []          // clear immediately — prevents stale data while loading
    current.value = null
    loading.value = true
    try {
      plans.value = await get<Plan[]>(`/plans?project_id=${projectId}`)
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

  async function update(uuid: string, data: PlanUpdate): Promise<Plan> {
    const plan = await patch<Plan>(`/plans/${uuid}`, data)
    const idx = plans.value.findIndex((p) => p.uuid === uuid)
    if (idx !== -1) plans.value[idx] = plan
    if (current.value?.uuid === uuid) current.value = plan
    return plan
  }

  async function remove(uuid: string) {
    await del(`/plans/${uuid}`)
    plans.value = plans.value.filter((p) => p.uuid !== uuid)
    if (current.value?.uuid === uuid) current.value = null
  }

  async function updateStep(planUuid: string, stepUuid: string, data: StepUpdate): Promise<Plan> {
    const step = await patch<PlanStep>(`/plans/${planUuid}/steps/${stepUuid}`, data)
    const plan = plans.value.find((p) => p.uuid === planUuid)
    if (plan) {
      const idx = plan.steps.findIndex((s) => s.uuid === stepUuid)
      if (idx !== -1) plan.steps[idx] = step
    }
    if (current.value?.uuid === planUuid) {
      const idx = current.value.steps.findIndex((s) => s.uuid === stepUuid)
      if (idx !== -1) current.value.steps[idx] = step
    }
    return plan || current.value!
  }

  async function addStep(planUuid: string, data: StepCreate): Promise<Plan> {
    const plan = await post<Plan>(`/plans/${planUuid}/steps`, data)
    const idx = plans.value.findIndex((p) => p.uuid === planUuid)
    if (idx !== -1) plans.value[idx] = plan
    if (current.value?.uuid === planUuid) current.value = plan
    return plan
  }

  async function deleteStep(planUuid: string, stepUuid: string): Promise<void> {
    await del(`/plans/${planUuid}/steps/${stepUuid}`)
    const plan = plans.value.find((p) => p.uuid === planUuid)
    if (plan) plan.steps = plan.steps.filter((s) => s.uuid !== stepUuid)
    if (current.value?.uuid === planUuid) {
      current.value.steps = current.value.steps.filter((s) => s.uuid !== stepUuid)
    }
  }

  function progress(plan: Plan): number {
    if (!plan.steps.length) return 0
    const done = plan.steps.filter((s) => s.status === 'completed' || s.status === 'skipped').length
    return Math.round((done / plan.steps.length) * 100)
  }

  return {
    plans, current, loading, error,
    fetchByProject, fetchOne, create, update, remove,
    updateStep, addStep, deleteStep, progress,
  }
})
