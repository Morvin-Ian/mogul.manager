<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2>{{ workspace ? 'Edit Workspace' : 'New Workspace' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="ws-title">Title</label>
          <input id="ws-title" v-model="form.title" required maxlength="255" />
        </div>
        <div class="form-group">
          <label for="ws-desc">Description</label>
          <textarea id="ws-desc" v-model="form.description" rows="3"></textarea>
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
