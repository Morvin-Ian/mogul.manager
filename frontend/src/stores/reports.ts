import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ProjectReport, WorkspaceReport } from '../types'
import { get } from './client'

export const useReportStore = defineStore('reports', () => {
  const projectReport = ref<ProjectReport | null>(null)
  const workspaceReport = ref<WorkspaceReport | null>(null)
  const loading = ref(false)

  async function fetchProjectReport(projectId: number) {
    loading.value = true
    try {
      projectReport.value = await get<ProjectReport>(`/reports/project/${projectId}`)
    } finally {
      loading.value = false
    }
  }

  async function fetchWorkspaceReport(workspaceId: number) {
    loading.value = true
    try {
      workspaceReport.value = await get<WorkspaceReport>(`/reports/workspace/${workspaceId}`)
    } finally {
      loading.value = false
    }
  }

  function clear() {
    projectReport.value = null
    workspaceReport.value = null
  }

  return { projectReport, workspaceReport, loading, fetchProjectReport, fetchWorkspaceReport, clear }
})
