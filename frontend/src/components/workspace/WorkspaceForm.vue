<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ workspace ? 'Edit Workspace' : 'New Workspace' }}</h2>
        <button type="button" class="modal-close" aria-label="Close dialog" @click="$emit('close')">
          <svg viewBox="0 0 16 16" fill="none" width="16" height="16"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </button>
      </div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="ws-title">Title</label>
          <input id="ws-title" v-model="form.title" required maxlength="255" />
        </div>
        <div class="form-group">
          <div class="label-row">
            <label for="ws-desc">Description</label>
            <button
              type="button"
              class="ai-btn"
              :disabled="!form.title.trim() || aiLoading"
              :title="!form.title.trim() ? 'Enter a title first' : 'Generate a description with AI'"
              @click="suggestDescription"
            >
              <span v-if="aiLoading" class="ai-spinner" />
              <template v-else>
                <svg viewBox="0 0 16 16" fill="none" width="12" height="12" aria-hidden="true">
                  <path d="M8 1.5l1.4 4.1L13.5 7l-4.1 1.4L8 12.5 6.6 8.4 2.5 7l4.1-1.4L8 1.5z" fill="currentColor"/>
                  <path d="M13 10.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2z" fill="currentColor" opacity="0.55"/>
                </svg>
                AI
              </template>
            </button>
          </div>
          <textarea id="ws-desc" v-model="form.description" rows="3" placeholder="What does this workspace cover?"></textarea>
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <div class="form-actions">
          <button type="button" class="btn" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : workspace ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { Workspace } from '../../types'
import { useAiSuggest } from '../../composables/useAiSuggest'

const props = defineProps<{
  workspace?: Workspace | null
}>()

const emit = defineEmits<{
  close: []
  saved: [data: { title: string; description: string }]
}>()

const form = reactive({
  title: '',
  description: '',
})
const saving = ref(false)
const error = ref<string | null>(null)
const { suggest, loading: aiLoading } = useAiSuggest()

async function suggestDescription() {
  const result = await suggest('workspace', form.title)
  if (result) form.description = result
}

watch(() => props.workspace, (ws) => {
  if (ws) {
    form.title = ws.title
    form.description = ws.description || ''
  } else {
    form.title = ''
    form.description = ''
  }
}, { immediate: true })

async function handleSubmit() {
  saving.value = true
  error.value = null
  emit('saved', { ...form })
  saving.value = false
}
</script>
