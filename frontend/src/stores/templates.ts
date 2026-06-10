import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project, ProjectTemplate, CreateFromTemplate } from '../types'
import { del, get, post } from './client'

export const useTemplateStore = defineStore('templates', () => {
  const templates = ref<ProjectTemplate[]>([])
  const loading = ref(false)

  async function fetchByWorkspace(workspaceId: number) {
    loading.value = true
    try {
      templates.value = await get<ProjectTemplate[]>(`/templates?workspace_id=${workspaceId}`)
    } finally {
      loading.value = false
    }
  }

  async function createFromProject(projectId: number, name: string, description?: string | null) {
    const t = await post<ProjectTemplate>('/templates', {
      project_id: projectId,
      name,
      description,
    })
    templates.value.push(t)
    return t
  }

  async function createProjectFromTemplate(
    templateId: number,
    data: CreateFromTemplate,
  ): Promise<Project> {
    return post<Project>(`/templates/from-template/${templateId}`, data)
  }

  async function remove(templateId: number) {
    await del(`/templates/${templateId}`)
    templates.value = templates.value.filter((t) => t.id !== templateId)
  }

  return { templates, loading, fetchByWorkspace, createFromProject, createProjectFromTemplate, remove }
})
