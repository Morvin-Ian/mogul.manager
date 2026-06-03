import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Document, SearchHit } from '../types'
import { get, del, patch, postFile, post } from './client'

export const useDocumentStore = defineStore('documents', () => {
  const documents = ref<Document[]>([])
  const current = ref<Document | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchByWorkspace(workspaceId: number): Promise<Document[]> {
    try {
      return await get<Document[]>(`/documents?workspace_id=${workspaceId}`)
    } catch {
      return []
    }
  }

  async function fetchByProject(projectId: number): Promise<Document[]> {
    try {
      return await get<Document[]>(`/documents?project_id=${projectId}`)
    } catch {
      return []
    }
  }

  async function fetchAll() {
    loading.value = true
    try {
      documents.value = await get<Document[]>('/documents')
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(uuid: string) {
    loading.value = true
    try {
      current.value = await get<Document>(`/documents/${uuid}`)
      _sync(current.value)
      return current.value
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function upload(
    file: File,
    ctx?: { workspace_id?: number | null; project_id?: number | null },
  ): Promise<Document> {
    const fd = new FormData()
    fd.append('file', file)
    if (ctx?.workspace_id) fd.append('workspace_id', String(ctx.workspace_id))
    if (ctx?.project_id) fd.append('project_id', String(ctx.project_id))
    const doc = await postFile<Document>('/documents', fd)
    documents.value.unshift(doc)
    _pollStatus(doc.uuid)
    return doc
  }

  async function updateProjectId(uuid: string, projectId: number | null): Promise<Document> {
    const doc = await patch<Document>(`/documents/${uuid}`, { project_id: projectId })
    _sync(doc)
    return doc
  }

  async function remove(uuid: string) {
    await del(`/documents/${uuid}`)
    documents.value = documents.value.filter((d) => d.uuid !== uuid)
    if (current.value?.uuid === uuid) current.value = null
  }

  async function reprocess(uuid: string) {
    const doc = await post<Document>(`/documents/${uuid}/reprocess`, undefined)
    _sync(doc)
    _pollStatus(doc.uuid)
    return doc
  }

  async function search(query: string, topK = 5): Promise<SearchHit[]> {
    const res = await post<{ results: SearchHit[]; count: number }>('/documents/search', {
      query,
      top_k: topK,
    })
    return res.results
  }

  async function getViewUrl(uuid: string): Promise<{ url: string; file_type: string; filename: string }> {
    return get(`/documents/${uuid}/view-url`)
  }

  async function getChunks(uuid: string): Promise<{ index: number; content: string }[]> {
    return get(`/documents/${uuid}/chunks`)
  }

  // ── internals ───────────────────────────────────────────────────

  function _sync(doc: Document) {
    const idx = documents.value.findIndex((d) => d.uuid === doc.uuid)
    if (idx !== -1) documents.value[idx] = doc
    else documents.value.unshift(doc)
    if (current.value?.uuid === doc.uuid) current.value = doc
  }

  async function _pollStatus(uuid: string, attempts = 0) {
    if (attempts > 60) return // give up after 5 minutes
    await new Promise((r) => setTimeout(r, 5000))
    try {
      const doc = await get<Document>(`/documents/${uuid}`)
      _sync(doc)
      if (doc.status === 'pending' || doc.status === 'processing') {
        _pollStatus(uuid, attempts + 1)
      }
    } catch {
      // silent
    }
  }

  return { documents, current, loading, error, fetchAll, fetchByWorkspace, fetchByProject, updateProjectId, fetchOne, upload, remove, reprocess, search, getViewUrl, getChunks }
})
