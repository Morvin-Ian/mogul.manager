import { ref } from 'vue'
import { post } from '../stores/client'

export type AiContextType = 'workspace' | 'project' | 'task'

export function useAiSuggest() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function suggest(
    contextType: AiContextType,
    title: string,
    field: string = 'description',
  ): Promise<string | null> {
    if (!title.trim()) return null
    loading.value = true
    error.value = null
    try {
      const res = await post<{ suggestion: string }>('/chat/suggest', {
        context_type: contextType,
        title: title.trim(),
        field,
      })
      return res.suggestion ?? null
    } catch (e: any) {
      error.value = e.message ?? 'Suggestion failed'
      return null
    } finally {
      loading.value = false
    }
  }

  return { suggest, loading, error }
}
