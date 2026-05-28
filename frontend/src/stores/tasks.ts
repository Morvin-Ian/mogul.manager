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

  async function fetchOne(id: number) {
    loading.value = true
    try {
      current.value = await get<Task>(`/tasks/${id}`)
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

  async function update(id: number, data: TaskUpdate) {
    const t = await patch<Task>(`/tasks/${id}`, data)
    const idx = tasks.value.findIndex((tk) => tk.id === id)
    if (idx !== -1) tasks.value[idx] = t
    if (current.value?.id === id) current.value = t
    return t
  }

  async function remove(id: number) {
    await del(`/tasks/${id}`)
    tasks.value = tasks.value.filter((t) => t.id !== id)
    if (current.value?.id === id) current.value = null
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

  return {
    tasks, current, loading, error,
    fetchByProject, fetchReviewTasks, fetchOne, create, update, remove,
    fetchComments, createComment, deleteComment,
  }
})
