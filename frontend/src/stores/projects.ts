import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project, ProjectCreate, ProjectUpdate } from '../types'
import { get, post, patch, del } from './client'

export const useProjectStore = defineStore('projects', () => {
  const projects = ref<Project[]>([])
  const current = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchByWorkspace(workspaceId: number) {
    loading.value = true
    try {
      projects.value = await get<Project[]>(`/projects?workspace_id=${workspaceId}`)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id: number) {
    loading.value = true
    try {
      current.value = await get<Project>(`/projects/${id}`)
      return current.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(data: ProjectCreate) {
    const p = await post<Project>('/projects', data)
    projects.value.push(p)
    return p
  }

  async function update(id: number, data: ProjectUpdate) {
    const p = await patch<Project>(`/projects/${id}`, data)
    const idx = projects.value.findIndex((pr) => pr.id === id)
    if (idx !== -1) projects.value[idx] = p
    if (current.value?.id === id) current.value = p
    return p
  }

  async function remove(id: number) {
    await del(`/projects/${id}`)
    projects.value = projects.value.filter((p) => p.id !== id)
    if (current.value?.id === id) current.value = null
  }

  return { projects, current, loading, error, fetchByWorkspace, fetchOne, create, update, remove }
})
