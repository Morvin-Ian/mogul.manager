import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ActivityLog } from '../types'
import { get } from './client'

export const useActivityStore = defineStore('activity', () => {
  const entries = ref<ActivityLog[]>([])
  const loading = ref(false)

  async function fetchByProject(projectId: number, skip = 0, limit = 50) {
    loading.value = true
    try {
      entries.value = await get<ActivityLog[]>(`/projects/${projectId}/activity?skip=${skip}&limit=${limit}`)
    } finally {
      loading.value = false
    }
  }

  async function fetchByWorkspace(workspaceId: number, skip = 0, limit = 50) {
    loading.value = true
    try {
      entries.value = await get<ActivityLog[]>(`/workspaces/${workspaceId}/activity?skip=${skip}&limit=${limit}`)
    } finally {
      loading.value = false
    }
  }

  function clear() {
    entries.value = []
  }

  return { entries, loading, fetchByProject, fetchByWorkspace, clear }
})
