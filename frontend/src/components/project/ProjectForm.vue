<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ project ? 'Edit Project' : 'New Project' }}</h2>
        <button type="button" class="modal-close" @click="$emit('close')">
          <svg viewBox="0 0 16 16" fill="none" width="16" height="16">
            <path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <form @submit.prevent="handleSubmit">

        <!-- Workspace selector — only shown when creating and multiple workspaces exist -->
        <div v-if="showWorkspacePicker" class="form-group">
          <label for="p-workspace">Workspace</label>
          <select id="p-workspace" v-model="form.workspace_id" required>
            <option disabled value="">Select a workspace</option>
            <option v-for="ws in workspaces" :key="ws.id" :value="ws.id">
              {{ ws.title }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="p-title">Title</label>
          <input id="p-title" v-model="form.title" required maxlength="255" placeholder="Project name" />
        </div>

        <div class="form-group">
          <div class="label-row">
            <label for="p-desc">Description</label>
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
          <textarea id="p-desc" v-model="form.description" rows="3" placeholder="What is this project about?"></textarea>
        </div>

        <div class="form-row-2">
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
        </div>

        <p v-if="error" class="form-error">{{ error }}</p>

        <div class="form-actions">
          <button type="button" class="btn" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="saving || (showWorkspacePicker && !form.workspace_id)">
            {{ saving ? 'Saving…' : project ? 'Update' : 'Create Project' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useWorkspaceStore } from '../../stores/workspaces'
import type { Project } from '../../types'
import { useAiSuggest } from '../../composables/useAiSuggest'

const props = defineProps<{
  project?: Project | null
  workspaceId?: number
}>()

const emit = defineEmits<{
  close: []
  saved: [data: Record<string, any>]
}>()

const workspaceStore = useWorkspaceStore()
const workspaces = computed(() => workspaceStore.workspaces)

// Show workspace picker only when: creating (not editing) AND no fixed workspaceId AND >1 workspaces
const showWorkspacePicker = computed(() =>
  !props.project && !props.workspaceId && workspaces.value.length > 1
)

const form = reactive({
  title: '',
  description: '',
  status: 'planning' as string,
  due_date: '',
  workspace_id: '' as number | '',
})

const saving = ref(false)
const error = ref<string | null>(null)
const { suggest, loading: aiLoading } = useAiSuggest()

async function suggestDescription() {
  const result = await suggest('project', form.title)
  if (result) form.description = result
}

onMounted(async () => {
  if (workspaces.value.length === 0) {
    await workspaceStore.fetchAll()
  }
})

watch(() => props.project, (p) => {
  if (p) {
    form.title = p.title
    form.description = p.description || ''
    form.status = p.status
    form.due_date = p.due_date ? p.due_date.slice(0, 10) : ''
    form.workspace_id = p.workspace_id
  } else {
    form.title = ''
    form.description = ''
    form.status = 'planning'
    form.due_date = ''
    // Pre-select: use fixed prop, or first workspace if only one, or empty for picker
    if (props.workspaceId) {
      form.workspace_id = props.workspaceId
    } else if (workspaces.value.length === 1) {
      form.workspace_id = workspaces.value[0].id
    } else {
      form.workspace_id = ''
    }
  }
}, { immediate: true })

// Re-check default once workspaces load (in case they weren't ready on mount)
watch(workspaces, (list) => {
  if (!props.project && !props.workspaceId && form.workspace_id === '' && list.length === 1) {
    form.workspace_id = list[0].id
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = null

  const payload: Record<string, any> = {
    title: form.title,
    description: form.description,
    status: form.status,
  }
  if (form.due_date) payload.due_date = form.due_date
  if (form.workspace_id) payload.workspace_id = form.workspace_id

  emit('saved', payload)
  saving.value = false
}
</script>

<style scoped>
.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
</style>
