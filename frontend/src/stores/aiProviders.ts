import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { AIProvider, AIKeyTestResult } from '../types'
import { get, put, post, del } from './client'

const BASE = '/users/me/ai/providers'

export const useAiProvidersStore = defineStore('aiProviders', () => {
  const providers = ref<AIProvider[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const active = computed(() => providers.value.find(p => p.is_active) ?? null)

  async function fetchProviders() {
    loading.value = true
    error.value = null
    try {
      providers.value = await get<AIProvider[]>(BASE)
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  /** Save a key and/or model. `apiKey` may be omitted to keep the stored one. */
  async function saveProvider(
    slug: string,
    data: { api_key?: string; model?: string | null; activate?: boolean },
  ) {
    await put(`${BASE}/${slug}`, data)
    await fetchProviders()
  }

  async function activateProvider(slug: string) {
    await post(`${BASE}/${slug}/activate`, {})
    await fetchProviders()
  }

  async function removeProvider(slug: string) {
    await del<void>(`${BASE}/${slug}`)
    await fetchProviders()
  }

  /** Check credentials with the vendor. Omit `api_key` to test the stored one. */
  function testProvider(slug: string, data: { api_key?: string; model?: string | null }) {
    return post<AIKeyTestResult>(`${BASE}/${slug}/test`, data)
  }

  return {
    providers,
    loading,
    error,
    active,
    fetchProviders,
    saveProvider,
    activateProvider,
    removeProvider,
    testProvider,
  }
})
