<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ task ? 'Edit Task' : 'New Task' }}</h2>
        <button type="button" class="modal-close" @click="$emit('close')">
          <svg viewBox="0 0 16 16" fill="none" width="16" height="16"><path d="M12 4L4 12M4 4l8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </button>
      </div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="t-title">Title</label>
          <input id="t-title" v-model="form.title" required maxlength="255" />
        </div>
        <div class="form-group">
          <div class="label-row">
            <label for="t-desc">Description</label>
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
          <textarea id="t-desc" v-model="form.description" rows="3" placeholder="What needs to be done?"></textarea>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="t-status">Status</label>
            <select id="t-status" v-model="form.status">
              <option value="todo">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="review">Review</option>
              <option value="blocked">In Revision</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="form-group">
            <label for="t-priority">Priority</label>
            <select id="t-priority" v-model.number="form.priority">
              <option :value="1">Low</option>
              <option :value="2">Medium</option>
              <option :value="3">High</option>
              <option :value="4">Urgent</option>
            </select>
          </div>
        </div>
        <div v-if="isTeamMode" class="form-group">
          <label>Assign to</label>
          <div class="assignee-picker" :class="{ 'picker-open': showAssigneePicker }">
            <button type="button" class="picker-trigger" @click="showAssigneePicker = !showAssigneePicker">
              <template v-if="selectedAssignee">
                <div class="pa-avatar" :style="selectedAssignee.user?.profile_path ? {} : { background: memberGradient(selectedAssignee.user?.username || '') }">
                  <img v-if="selectedAssignee.user?.profile_path" :src="selectedAssignee.user.profile_path" :alt="selectedAssignee.user?.username" class="pa-avatar-img" />
                  <span v-else>{{ selectedAssignee.user?.id === auth.user?.id ? 'Me' : (selectedAssignee.user?.username || '?').charAt(0).toUpperCase() }}</span>
                </div>
                <span class="pa-name">{{ selectedAssignee.user?.id === auth.user?.id ? 'You' : (selectedAssignee.user?.username || selectedAssignee.user?.email) }}</span>
                <span class="pa-role-badge" :class="`role-${selectedAssignee.role}`">{{ selectedAssignee.role }}</span>
              </template>
              <template v-else>
                <div class="pa-unassigned-icon">
                  <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
                    <circle cx="8" cy="5.5" r="3" stroke="currentColor" stroke-width="1.4"/>
                    <path d="M2 13.5c0-3 2.5-5 6-5s6 2 6 5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                  </svg>
                </div>
                <span class="pa-unassigned-text">Unassigned</span>
              </template>
              <svg class="pa-chevron" viewBox="0 0 12 12" fill="none" width="10" height="10">
                <path d="M3 4.5l3 3 3-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>

            <template v-if="showAssigneePicker">
              <div class="picker-backdrop" @click="showAssigneePicker = false"></div>
              <div class="picker-dropdown">
                <div class="picker-option picker-unassigned" @click="selectAssignee(null)">
                  <div class="pa-unassigned-icon">
                    <svg viewBox="0 0 16 16" fill="none" width="13" height="13">
                      <circle cx="8" cy="5.5" r="3" stroke="currentColor" stroke-width="1.4"/>
                      <path d="M2 13.5c0-3 2.5-5 6-5s6 2 6 5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                    </svg>
                  </div>
                  <span class="po-name">Unassigned</span>
                  <svg v-if="!form.assigned_to_id" class="po-check" viewBox="0 0 12 12" fill="none" width="12" height="12">
                    <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div
                  v-for="m in assignableMembers"
                  :key="m.user_id"
                  class="picker-option"
                  @click="selectAssignee(m.user_id)"
                >
                  <div class="pa-avatar pa-avatar--sm" :style="m.user?.profile_path ? {} : { background: memberGradient(m.user?.username || '') }">
                    <img v-if="m.user?.profile_path" :src="m.user.profile_path" :alt="m.user?.username" class="pa-avatar-img" />
                    <span v-else>{{ (m.user?.username || '?').charAt(0).toUpperCase() }}</span>
                  </div>
                  <div class="po-info">
                    <span class="po-name">{{ m.user?.username }}</span>
                    <span class="po-email">{{ m.user?.email }}</span>
                  </div>
                  <span class="pa-role-badge" :class="`role-${m.role}`">{{ m.role }}</span>
                  <svg v-if="form.assigned_to_id === m.user_id" class="po-check" viewBox="0 0 12 12" fill="none" width="12" height="12">
                    <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
            </template>
          </div>
          <span v-if="!isAdminUser" class="field-hint">You can only assign tasks to yourself.</span>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="t-est">Est. Hours</label>
            <input id="t-est" v-model.number="form.estimated_hours" type="number" min="0" />
          </div>
          <div class="form-group">
            <label for="t-due">Due Date</label>
            <input id="t-due" v-model="form.due_date" type="date" />
          </div>
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <div class="form-actions">
          <button type="button" class="btn" @click="$emit('close')">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Saving...' : task ? 'Update' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import type { Task, TaskPriority, TaskStatus, WorkspaceMember } from '../../types'
import { useAiSuggest } from '../../composables/useAiSuggest'
import { get } from '../../stores/client'
import { useAuthStore } from '../../stores/auth'

const props = defineProps<{
  task?: Task | null
  projectId?: number | null
}>()

const emit = defineEmits<{
  close: []
  saved: [data: Record<string, any>]
}>()

interface TaskForm {
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority | number
  assigned_to_id: number | null
  estimated_hours: number | null
  due_date: string
}

const form = reactive<TaskForm>({
  title: '',
  description: '',
  status: 'todo',
  priority: 2,
  assigned_to_id: null,
  estimated_hours: null,
  due_date: '',
})
const auth = useAuthStore()
const members = ref<WorkspaceMember[]>([])
const saving = ref(false)
const error = ref<string | null>(null)
const showAssigneePicker = ref(false)
const { suggest, loading: aiLoading } = useAiSuggest()

async function suggestDescription() {
  const result = await suggest('task', form.title)
  if (result) form.description = result
}

// Team mode: workspace has more than just the owner
const isTeamMode = computed(() => members.value.length > 1)

// Current user's membership in this workspace
const myMember = computed(() => members.value.find((m) => m.user_id === auth.user?.id))
const isAdminUser = computed(() => {
  const role = myMember.value?.role
  return role === 'admin' || role === 'owner'
})

// Members the current user may assign to
const assignableMembers = computed(() =>
  isAdminUser.value
    ? members.value
    : members.value.filter((m) => m.user_id === auth.user?.id)
)

const selectedAssignee = computed(() =>
  form.assigned_to_id ? members.value.find((m) => m.user_id === form.assigned_to_id) ?? null : null
)

const MEMBER_GRADIENTS = [
  'linear-gradient(135deg, #6366F1, #8B5CF6)',
  'linear-gradient(135deg, #0EA5E9, #2563EB)',
  'linear-gradient(135deg, #10B981, #059669)',
  'linear-gradient(135deg, #F59E0B, #D97706)',
  'linear-gradient(135deg, #EF4444, #DC2626)',
  'linear-gradient(135deg, #EC4899, #DB2777)',
]

function memberGradient(name: string): string {
  let hash = 0
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffffffff
  return MEMBER_GRADIENTS[Math.abs(hash) % MEMBER_GRADIENTS.length]
}

function selectAssignee(userId: number | null) {
  form.assigned_to_id = userId
  showAssigneePicker.value = false
}

onMounted(async () => {
  const pid = props.task?.project_id ?? props.projectId
  if (!pid) return
  try {
    const project = await get<{ workspace_id: number }>(`/projects/${pid}`)
    members.value = await get<WorkspaceMember[]>(`/workspaces/${project.workspace_id}/members`)
  } catch { /* noop */ }
})

watch(() => props.task, (t) => {
  if (t) {
    form.title = t.title
    form.description = t.description || ''
    form.status = t.status
    form.priority = t.priority
    form.assigned_to_id = t.assigned_to_id
    form.estimated_hours = t.estimated_hours
    form.due_date = t.due_date ? t.due_date.slice(0, 10) : ''
  } else {
    form.title = ''
    form.description = ''
    form.status = 'todo'
    form.priority = 2
    form.assigned_to_id = null
    form.estimated_hours = null
    form.due_date = ''
  }
}, { immediate: true })

async function handleSubmit() {
  saving.value = true
  error.value = null
  const payload: Record<string, any> = { ...form }
  if (!payload.due_date) delete payload.due_date
  if (!payload.estimated_hours) delete payload.estimated_hours
  if (!payload.assigned_to_id) payload.assigned_to_id = null
  if (props.projectId && !props.task) {
    payload.project_id = props.projectId
  }
  emit('saved', payload)
  saving.value = false
}
</script>

<style scoped>
.field-hint {
  display: block;
  font-size: 11px;
  color: var(--text-light);
  margin-top: 4px;
}

/* ── Assignee custom picker ── */
.assignee-picker { position: relative; }

.picker-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  font-size: 13.5px;
  color: var(--text);
  text-align: left;
  transition: border-color 0.12s;
}
.picker-trigger:hover { border-color: var(--border-strong); }
.picker-open .picker-trigger { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-muted); }

.pa-avatar {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
  overflow: hidden;
}
.pa-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: inherit; }

.pa-avatar--sm {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  font-size: 13px;
}

.pa-unassigned-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--surface);
  border: 1.5px dashed var(--border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-light);
  flex-shrink: 0;
}

.pa-name { flex: 1; font-weight: 600; font-size: 13.5px; color: var(--text); }
.pa-unassigned-text { flex: 1; color: var(--text-light); font-size: 13.5px; }

.pa-role-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: capitalize;
  flex-shrink: 0;
}
.role-owner { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.role-admin { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
.role-member { background: #F0F2F5; color: #374151; border: 1px solid #E2E8F0; }

.pa-chevron { margin-left: auto; color: var(--text-light); flex-shrink: 0; }

/* Dropdown backdrop */
.picker-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
}

.picker-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.14);
  z-index: 51;
  overflow: hidden;
  max-height: 260px;
  overflow-y: auto;
}

.picker-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.1s;
}
.picker-option:hover { background: var(--bg); }
.picker-unassigned { border-bottom: 1px solid var(--border); }

.po-info { flex: 1; display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.po-name { font-size: 13.5px; font-weight: 600; color: var(--text); }
.po-email { font-size: 11.5px; color: var(--text-light); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.po-check { flex-shrink: 0; color: var(--primary); margin-left: auto; }
</style>
