import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification, UnreadCount } from '../types'
import { get, patch, post } from './client'
import { useAuthStore } from './auth'

export const useNotificationStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)

  const hasUnread = computed(() => unreadCount.value > 0)

  let eventSource: EventSource | null = null

  async function fetchNotifications(skip = 0, limit = 50) {
    loading.value = true
    try {
      notifications.value = await get<Notification[]>(`/notifications?skip=${skip}&limit=${limit}`)
    } finally {
      loading.value = false
    }
  }

  async function fetchUnreadCount() {
    try {
      const res = await get<UnreadCount>('/notifications/unread-count')
      unreadCount.value = res.count
    } catch {
      // non-critical
    }
  }

  async function markAsRead(id: number) {
    await patch<void>(`/notifications/${id}/read`)
    const n = notifications.value.find(n => n.id === id)
    if (n) n.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }

  async function markAllAsRead() {
    await post<void>('/notifications/read-all')
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
  }

  function connectSSE() {
    const auth = useAuthStore()
    if (!auth.token || eventSource) return

    eventSource = new EventSource(`/api/notifications/stream?token=${auth.token}`)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'notification') {
          unreadCount.value++
          // Prepend to the list
          notifications.value.unshift(data as unknown as Notification)
        }
      } catch {
        // ignore parse errors
      }
    }

    eventSource.onerror = () => {
      eventSource?.close()
      eventSource = null
      // Reconnect after 10 seconds
      setTimeout(() => connectSSE(), 10000)
    }
  }

  function disconnectSSE() {
    eventSource?.close()
    eventSource = null
  }

  return {
    notifications,
    unreadCount,
    loading,
    hasUnread,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    connectSSE,
    disconnectSSE,
  }
})
