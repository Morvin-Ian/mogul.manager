import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TaskDependencyList, TaskDependencyRead } from '../types'
import { get, post, del } from './client'

export const useDependencyStore = defineStore('dependencies', () => {
  const dependsOn = ref<TaskDependencyRead[]>([])
  const blockedBy = ref<TaskDependencyRead[]>([])
  const loading = ref(false)

  async function fetch(taskUuid: string) {
    loading.value = true
    try {
      const data = await get<TaskDependencyList>(`/tasks/${taskUuid}/dependencies`)
      dependsOn.value = data.depends_on
      blockedBy.value = data.blocked_by
    } finally {
      loading.value = false
    }
  }

  async function add(taskUuid: string, dependencyUuid: string) {
    await post(`/tasks/${taskUuid}/dependencies/${dependencyUuid}`)
    await fetch(taskUuid)
  }

  async function remove(taskUuid: string, dependencyUuid: string) {
    await del(`/tasks/${taskUuid}/dependencies/${dependencyUuid}`)
    await fetch(taskUuid)
  }

  function clear() {
    dependsOn.value = []
    blockedBy.value = []
  }

  return { dependsOn, blockedBy, loading, fetch, add, remove, clear }
})
