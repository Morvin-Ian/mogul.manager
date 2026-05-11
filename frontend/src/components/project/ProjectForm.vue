<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2>{{ project ? 'Edit Project' : 'New Project' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="p-title">Title</label>
          <input id="p-title" v-model="form.title" required maxlength="255" />
        </div>
        <div class="form-group">
          <label for="p-desc">Description</label>
          <textarea id="p-desc" v-model="form.description" rows="3"></textarea>
        </div>
        <div class="form-group">
          <label for="p-status">Status</label>
          <select id="p-status" v-model="form.status">
            <option value="planning">Planning</option>
            <option value="active">Active</option>
            <option value="on_hold">On Hold</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
          </select>
        </div>
        <div class="form-group">
          <label for="p-due">Due Date</label>
          <input id="p-due" v-model="form.due_date" type="date" />
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <div class="form-actions">
          <button type="button" class="btn" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : project ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import type { Project } from '../../types'

const props = defineProps<{
  project?: Project | null
}>()

const emit = defineEmits<{
  close: []
  saved: [data: Record<string, any>]
}>()

const form = reactive({
  title: '',
  description: '',
  status: 'planning' as string,
  due_date: '',
})
const saving = ref(false)
const error = ref<string | null>(null)

watch(() => props.project, (p) => {
  if (p) {
    form.title = p.title
    form.description = p.description || ''
    form.status = p.status
    form.due_date = p.due_date ? p.due_date.slice(0, 10) : ''
  } else {
    form.title = ''
    form.description = ''
    form.status = 'planning'
    form.due_date = ''
  }
}, { immediate: true })

async function handleSubmit() {
  saving.value = true
  error.value = null
  const payload = { ...form }
  if (!payload.due_date) delete (payload as any).due_date
  emit('saved', payload)
  saving.value = false
}
</script>
