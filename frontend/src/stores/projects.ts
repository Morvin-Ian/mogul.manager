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

  async function fetchOne(uuid: string) {
    loading.value = true
    try {
      current.value = await get<Project>(`/projects/${uuid}`)
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

  async function update(uuid: string, data: ProjectUpdate) {
    const p = await patch<Project>(`/projects/${uuid}`, data)
    const idx = projects.value.findIndex((pr) => pr.uuid === uuid)
    if (idx !== -1) projects.value[idx] = p
    if (current.value?.uuid === uuid) current.value = p
    return p
  }

  async function remove(uuid: string) {
    await del(`/projects/${uuid}`)
    projects.value = projects.value.filter((p) => p.uuid !== uuid)
    if (current.value?.uuid === uuid) current.value = null
  }

  return { projects, current, loading, error, fetchByWorkspace, fetchOne, create, update, remove }
})
