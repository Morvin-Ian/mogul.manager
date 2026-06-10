import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Milestone, MilestoneCreate, MilestoneUpdate } from '../types'
import { get, post, patch, del } from './client'

export const useMilestoneStore = defineStore('milestones', () => {
  const milestones = ref<Milestone[]>([])
  const loading = ref(false)

  async function fetchByProject(projectId: number) {
    loading.value = true
    try {
      milestones.value = await get<Milestone[]>(`/projects/${projectId}/milestones`)
    } finally {
      loading.value = false
    }
  }

  async function create(projectId: number, data: MilestoneCreate) {
    const m = await post<Milestone>(`/projects/${projectId}/milestones`, data)
    milestones.value.push(m)
    return m
  }

  async function update(projectId: number, milestoneId: number, data: MilestoneUpdate) {
    const m = await patch<Milestone>(`/projects/${projectId}/milestones/${milestoneId}`, data)
    const idx = milestones.value.findIndex((x) => x.id === milestoneId)
    if (idx !== -1) milestones.value[idx] = m
    return m
  }

  async function remove(projectId: number, milestoneId: number) {
    await del(`/projects/${projectId}/milestones/${milestoneId}`)
    milestones.value = milestones.value.filter((x) => x.id !== milestoneId)
  }

  return {
    milestones,
    loading,
    fetchByProject,
    create,
    update,
    remove,
  }
})
