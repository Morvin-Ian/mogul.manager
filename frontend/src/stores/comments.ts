import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Comment, CommentCreate } from '../types'
import { get, post, patch, del } from './client'

export const useCommentStore = defineStore('comments', () => {
  const all = ref<Comment[]>([])
  const loading = ref(false)

  async function fetchForTask(taskId: number) {
    const items = await get<Comment[]>(`/comments?task_id=${taskId}`)
    const existingIds = new Set(all.value.map((c) => c.id))
    all.value.push(...items.filter((c) => !existingIds.has(c.id)))
    return items
  }

  // Comments that concern the current user (dashboard feed): on tasks
  // assigned to them, threads they joined, or their own.
  async function fetchRelevant(limit = 50) {
    const items = await get<Comment[]>(`/comments/relevant?limit=${limit}`)
    const existingIds = new Set(all.value.map((c) => c.id))
    all.value.push(...items.filter((c) => !existingIds.has(c.id)))
    return items
  }

  async function create(data: CommentCreate) {
    const c = await post<Comment>('/comments', data)
    all.value.unshift(c)
    return c
  }

  async function update(id: number, content: string) {
    const c = await patch<Comment>(`/comments/${id}`, { content })
    const idx = all.value.findIndex((x) => x.id === id)
    if (idx !== -1) all.value[idx] = c
    return c
  }

  async function remove(id: number) {
    await del(`/comments/${id}`)
    all.value = all.value.filter((c) => c.id !== id)
  }

  function clear() {
    all.value = []
  }

  return { all, loading, fetchForTask, fetchRelevant, create, update, remove, clear }
})
