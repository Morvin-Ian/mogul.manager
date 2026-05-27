import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Document, SearchHit } from '../types'
import { get, del, postFile, post } from './client'

export const useDocumentStore = defineStore('documents', () => {
  const documents = ref<Document[]>([])
  const current = ref<Document | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

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

  async function fetchOne(id: number) {
    loading.value = true
    try {
      current.value = await get<Document>(`/documents/${id}`)
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
    _pollStatus(doc.id)
    return doc
  }

  async function remove(id: number) {
    await del(`/documents/${id}`)
    documents.value = documents.value.filter((d) => d.id !== id)
    if (current.value?.id === id) current.value = null
  }

  async function reprocess(id: number) {
    const doc = await post<Document>(`/documents/${id}/reprocess`, undefined)
    _sync(doc)
    _pollStatus(id)
    return doc
  }

  async function search(query: string, topK = 5): Promise<SearchHit[]> {
    const res = await post<{ results: SearchHit[]; count: number }>('/documents/search', {
      query,
      top_k: topK,
    })
    return res.results
  }

  // ── internals ───────────────────────────────────────────────────

  function _sync(doc: Document) {
    const idx = documents.value.findIndex((d) => d.id === doc.id)
    if (idx !== -1) documents.value[idx] = doc
    else documents.value.unshift(doc)
    if (current.value?.id === doc.id) current.value = doc
  }

  async function _pollStatus(id: number, attempts = 0) {
    if (attempts > 60) return // give up after 5 minutes
    await new Promise((r) => setTimeout(r, 5000))
    try {
      const doc = await get<Document>(`/documents/${id}`)
      _sync(doc)
      if (doc.status === 'pending' || doc.status === 'processing') {
        _pollStatus(id, attempts + 1)
      }
    } catch {
      // silent
    }
  }

  return { documents, current, loading, error, fetchAll, fetchOne, upload, remove, reprocess, search }
})
