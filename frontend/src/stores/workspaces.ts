import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Workspace, WorkspaceCreate, WorkspaceUpdate } from '../types'
import { get, post, patch, del } from './client'

export const useWorkspaceStore = defineStore('workspaces', () => {
  const workspaces = ref<Workspace[]>([])
  const current = ref<Workspace | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    try {
      workspaces.value = await get<Workspace[]>('/workspaces')
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: number) {
    loading.value = true
    try {
      current.value = await get<Workspace>(`/workspaces/${id}`)
      return current.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(data: WorkspaceCreate) {
    const ws = await post<Workspace>('/workspaces', data)
    workspaces.value.push(ws)
    return ws
  }

  async function update(id: number, data: WorkspaceUpdate) {
    const ws = await patch<Workspace>(`/workspaces/${id}`, data)
    const idx = workspaces.value.findIndex((w) => w.id === id)
    if (idx !== -1) workspaces.value[idx] = ws
    if (current.value?.id === id) current.value = ws
    return ws
  }

  async function remove(id: number) {
    await del(`/workspaces/${id}`)
    workspaces.value = workspaces.value.filter((w) => w.id !== id)
    if (current.value?.id === id) current.value = null
  }

  return { workspaces, current, loading, error, fetchAll, fetchOne, create, update, remove }
})
