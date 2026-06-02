import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Task, TaskCreate, TaskUpdate, Comment, CommentCreate } from '../types'
import { get, post, patch, del } from './client'

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const current = ref<Task | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchByProject(projectId: number) {
    loading.value = true
    try {
      tasks.value = await get<Task[]>(`/tasks?project_id=${projectId}`)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchReviewTasks(workspaceId: number): Promise<Task[]> {
    return get<Task[]>(`/tasks?workspace_id=${workspaceId}&status=review`)
  }

  async function fetchOne(uuid: string) {
    loading.value = true
    try {
      current.value = await get<Task>(`/tasks/${uuid}`)
      return current.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function create(data: TaskCreate) {
    const t = await post<Task>('/tasks', data)
    tasks.value.push(t)
    return t
  }

  async function update(uuid: string, data: TaskUpdate) {
    const t = await patch<Task>(`/tasks/${uuid}`, data)
    const idx = tasks.value.findIndex((tk) => tk.uuid === uuid)
    if (idx !== -1) tasks.value[idx] = t
    if (current.value?.uuid === uuid) current.value = t
    return t
  }

  async function remove(uuid: string) {
    await del(`/tasks/${uuid}`)
    tasks.value = tasks.value.filter((t) => t.uuid !== uuid)
    if (current.value?.uuid === uuid) current.value = null
  }

  async function fetchComments(taskId: number) {
    return get<Comment[]>(`/comments?task_id=${taskId}`)
  }

  async function createComment(data: CommentCreate) {
    return post<Comment>('/comments', data)
  }

  async function deleteComment(id: number) {
    await del(`/comments/${id}`)
  }

  async function reorder(uuid: string, position: number, status: string) {
    await post('/tasks/reorder', { uuid, position, status })
  }

  return {
    tasks, current, loading, error,
    fetchByProject, fetchReviewTasks, fetchOne, create, update, remove,
    fetchComments, createComment, deleteComment, reorder,
  }
})
