import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TaskAttachment, AttachmentList } from '../types'
import { del, get, postFile } from './client'

export const useAttachmentStore = defineStore('attachments', () => {
  const items = ref<TaskAttachment[]>([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchByTask(taskId: number | string) {
    loading.value = true
    try {
      const data = await get<AttachmentList>(`/tasks/${taskId}/attachments`)
      items.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function upload(taskId: number | string, file: File) {
    const form = new FormData()
    form.append('file', file)
    const att = await postFile<TaskAttachment>(`/tasks/${taskId}/attachments`, form)
    items.value.unshift(att)
    total.value++
    return att
  }

  async function remove(taskId: number | string, attachmentId: number) {
    await del(`/tasks/${taskId}/attachments/${attachmentId}`)
    items.value = items.value.filter((a) => a.id !== attachmentId)
    total.value--
  }

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return { items, total, loading, fetchByTask, upload, remove, formatSize }
})
