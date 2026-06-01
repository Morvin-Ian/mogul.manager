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

  async function fetchOne(uuid: string) {
    loading.value = true
    try {
      current.value = await get<Workspace>(`/workspaces/${uuid}`)
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

  async function update(uuid: string, data: WorkspaceUpdate) {
    const ws = await patch<Workspace>(`/workspaces/${uuid}`, data)
    const idx = workspaces.value.findIndex((w) => w.uuid === uuid)
    if (idx !== -1) workspaces.value[idx] = ws
    if (current.value?.uuid === uuid) current.value = ws
    return ws
  }

  async function remove(uuid: string) {
    await del(`/workspaces/${uuid}`)
    workspaces.value = workspaces.value.filter((w) => w.uuid !== uuid)
    if (current.value?.uuid === uuid) current.value = null
  }

  return { workspaces, current, loading, error, fetchAll, fetchOne, create, update, remove }
})
