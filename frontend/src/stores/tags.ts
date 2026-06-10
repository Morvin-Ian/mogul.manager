import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Tag } from '../types'
import { get, post, patch, del } from './client'

export const useTagStore = defineStore('tags', () => {
  const tags = ref<Tag[]>([])
  const loading = ref(false)

  async function fetchByProject(projectId: number) {
    loading.value = true
    try {
      tags.value = await get<Tag[]>(`/projects/${projectId}/tags`)
    } finally {
      loading.value = false
    }
  }

  async function create(projectId: number, name: string, color: string) {
    const t = await post<Tag>(`/projects/${projectId}/tags`, { name, color })
    tags.value.push(t)
    return t
  }

  async function update(tag: Tag, data: { name?: string; color?: string }) {
    const t = await patch<Tag>(`/projects/${tag.project_id}/tags/${tag.id}`, data)
    const idx = tags.value.findIndex((x) => x.id === tag.id)
    if (idx !== -1) tags.value[idx] = t
    return t
  }

  async function remove(tag: Tag) {
    await del(`/projects/${tag.project_id}/tags/${tag.id}`)
    tags.value = tags.value.filter((x) => x.id !== tag.id)
  }

  async function attachToTask(taskId: number, tagId: number) {
    await post<void>(`/tasks/${taskId}/tags/${tagId}`)
  }

  async function detachFromTask(taskId: number, tagId: number) {
    await del(`/tasks/${taskId}/tags/${tagId}`)
  }

  async function fetchTaskTags(taskId: number): Promise<Tag[]> {
    return get<Tag[]>(`/tasks/${taskId}/tags`)
  }

  return {
    tags,
    loading,
    fetchByProject,
    create,
    update,
    remove,
    attachToTask,
    detachFromTask,
    fetchTaskTags,
  }
})
