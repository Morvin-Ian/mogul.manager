<template>
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div v-if="task" class="drawer-backdrop" @click="emit('close')"></div>
    </Transition>

    <Transition name="drawer-slide">
      <div v-if="task" class="drawer" tabindex="-1">

        <!-- ── Header ── -->
        <div class="drawer-header">
          <button class="drawer-close" @click="emit('close')" title="Close">
            <font-awesome-icon :icon="['fas', 'xmark']" />
          </button>
          <div class="drawer-header-actions">
            <button v-if="isAdmin" class="hdr-btn" :class="{ 'hdr-btn--active': editMode }" @click="editMode = !editMode">
              <font-awesome-icon :icon="['fas', 'pen']" />
              {{ editMode ? 'Editing' : 'Edit' }}
            </button>
            <button v-if="isAdmin" class="hdr-btn hdr-btn--danger" @click="handleDelete">
              <font-awesome-icon :icon="['fas', 'trash']" />
              Delete
            </button>
          </div>
        </div>

        <!-- ── Title ── -->
        <div class="drawer-title-wrap">
          <textarea
            v-if="editMode"
            v-model="form.title"
            class="title-textarea"
            rows="2"
            placeholder="Task title"
          ></textarea>
          <h2 v-else class="drawer-title">{{ task.title }}</h2>
        </div>

        <!-- ── Status pills ── -->
        <div class="status-row">
          <button
            v-for="s in statuses"
            :key="s.key"
            class="status-pill"
            :class="[`sp-${s.key}`, { 'sp-active': form.status === s.key, 'sp-dimmed': !isAdmin && !canMemberChangeToStatus(s.key) }]"
            :title="!isAdmin && !canMemberChangeToStatus(s.key) ? 'Not allowed for your role' : s.label"
            @click="handleStatusChange(s.key)"
          >
            <span class="sp-dot"></span>
            {{ s.label }}
          </button>
        </div>

        <div class="drawer-divider"></div>

        <!-- ── Properties table ── -->
        <div class="props-table">
          <!-- Created -->
          <div class="prop-row">
            <div class="prop-label">
              <font-awesome-icon :icon="['far', 'clock']" />
              Created
            </div>
            <div class="prop-val">{{ formatDateTime(task.created_at) }}</div>
          </div>

          <!-- Status -->
          <div class="prop-row">
            <div class="prop-label">
              <font-awesome-icon :icon="['fas', 'circle-dot']" />
              Status
            </div>
            <div class="prop-val">
              <span class="status-val-pill" :class="`svp-${form.status}`">
                <span class="svp-dot"></span>
                {{ statusLabel(form.status) }}
              </span>
            </div>
          </div>

          <!-- Priority -->
          <div class="prop-row">
            <div class="prop-label">
              <font-awesome-icon :icon="['fas', 'arrow-down-wide-short']" />
              Priority
            </div>
            <div class="prop-val">
              <select v-if="editMode" v-model.number="form.priority" class="prop-select">
                <option :value="1">Low</option>
                <option :value="2">Medium</option>
                <option :value="3">High</option>
                <option :value="4">Urgent</option>
              </select>
              <span v-else class="priority-pill" :class="`pp-${form.priority}`">
                {{ priorityLabel(form.priority) }}
              </span>
            </div>
          </div>

          <!-- Due Date -->
          <div class="prop-row">
            <div class="prop-label">
              <font-awesome-icon :icon="['far', 'calendar']" />
              Due Date
            </div>
            <div class="prop-val">
              <input v-if="editMode" type="date" v-model="form.due_date" class="prop-input" />
              <span v-else class="prop-text">
                <template v-if="task.due_date">
                  {{ formatDate(task.created_at) }}
                  <font-awesome-icon :icon="['fas', 'arrow-right']" style="margin: 0 3px; opacity: 0.5; font-size: 10px;" />
                  {{ formatDate(task.due_date) }}
                </template>
                <span v-else class="prop-empty">—</span>
              </span>
            </div>
          </div>

          <!-- Estimated hours -->
          <div class="prop-row">
            <div class="prop-label">
              <font-awesome-icon :icon="['far', 'hourglass-half']" />
              Est. Hours
            </div>
            <div class="prop-val">
              <input v-if="editMode" type="number" v-model.number="form.estimated_hours" min="0" step="0.5" class="prop-input prop-input--sm" />
              <span v-else class="prop-text">{{ task.estimated_hours != null ? task.estimated_hours + 'h' : '' }}<span v-if="task.estimated_hours == null" class="prop-empty">—</span></span>
            </div>
          </div>

          <!-- Assignee -->
          <div class="prop-row">
            <div class="prop-label">
              <font-awesome-icon :icon="['fas', 'user']" />
              Assignee
            </div>
            <div class="prop-val">
              <!-- Edit mode picker -->
              <div v-if="editMode && isAdmin" class="assignee-picker" :class="{ 'picker-open': showAssigneePicker }">
                <button type="button" class="picker-trigger" @click="showAssigneePicker = !showAssigneePicker">
                  <template v-if="selectedAssignee">
                    <div class="av-circle" :style="{ background: memberGradient(selectedAssignee.user?.username || '') }">
                      {{ (selectedAssignee.user?.username || '?').charAt(0).toUpperCase() }}
                    </div>
                    <span class="av-name">{{ selectedAssignee.user?.username }}</span>
                  </template>
                  <template v-else>
                    <div class="av-empty">
                      <font-awesome-icon :icon="['fas', 'user']" style="font-size: 10px;" />
                    </div>
                    <span class="av-empty-label">Unassigned</span>
                  </template>
                  <font-awesome-icon :icon="['fas', 'chevron-down']" class="av-chevron" />
                </button>
                <template v-if="showAssigneePicker">
                  <div class="picker-backdrop" @click="showAssigneePicker = false"></div>
                  <div class="picker-dropdown">
                    <div class="picker-option picker-unassigned" @click="selectAssignee(null)">
                      <div class="av-empty">
                        <font-awesome-icon :icon="['fas', 'user']" style="font-size: 9px;" />
                      </div>
                      <span class="po-name">Unassigned</span>
                      <font-awesome-icon v-if="!form.assigned_to_id" :icon="['fas', 'check']" class="po-check" />
                    </div>
                    <div v-for="m in workspaceMembers" :key="m.user_id" class="picker-option" @click="selectAssignee(m.user_id)">
                      <div class="av-circle av-circle--sm" :style="{ background: memberGradient(m.user?.username || '') }">
                        {{ (m.user?.username || '?').charAt(0).toUpperCase() }}
                      </div>
                      <div class="po-info">
                        <span class="po-name">{{ m.user?.username }}</span>
                        <span class="po-email">{{ m.user?.email }}</span>
                      </div>
                      <font-awesome-icon v-if="form.assigned_to_id === m.user_id" :icon="['fas', 'check']" class="po-check" />
                    </div>
                  </div>
                </template>
              </div>
              <!-- Read-only -->
              <div v-else-if="task.assignee_name" class="av-read">
                <div class="av-circle av-circle--sm" :style="{ background: memberGradient(task.assignee_name) }">
                  {{ task.assignee_name.charAt(0).toUpperCase() }}
                </div>
                <span class="prop-text">{{ task.assignee_name }}</span>
              </div>
              <span v-else class="prop-empty">Unassigned</span>
            </div>
          </div>
        </div>

        <div class="drawer-divider"></div>

        <!-- ── Save row (edit mode) ── -->
        <div v-if="editMode" class="save-row">
          <button class="btn-save" :disabled="saving" @click="handleSave">
            {{ saving ? 'Saving…' : 'Save changes' }}
          </button>
          <button class="btn-cancel" @click="editMode = false">Cancel</button>
        </div>

        <!-- ── Tabs ── -->
        <div class="drawer-tabs">
          <button class="tab-btn" :class="{ 'tab-active': activeTab === 'description' }" @click="activeTab = 'description'">Description</button>
          <button class="tab-btn" :class="{ 'tab-active': activeTab === 'comments' }" @click="activeTab = 'comments'">
            Comments
            <span v-if="comments.length" class="tab-badge">{{ comments.length }}</span>
          </button>
          <button
            v-if="task.status === 'review'"
            class="tab-btn tab-btn--review"
            :class="{ 'tab-active': activeTab === 'review' }"
            @click="activeTab = 'review'"
          >
            <font-awesome-icon :icon="['fas', 'link']" />
            Review Links
            <span v-if="currentReviewLinks.length" class="tab-badge">{{ currentReviewLinks.length }}</span>
          </button>
        </div>

        <!-- ── Description tab ── -->
        <div v-if="activeTab === 'description'" class="tab-content">
          <textarea
            v-if="editMode"
            v-model="form.description"
            class="desc-textarea"
            rows="5"
            placeholder="Add a description…"
          ></textarea>
          <p v-else-if="task.description" class="desc-text">{{ task.description }}</p>
          <p v-else class="desc-empty">No description added yet.</p>
        </div>

        <!-- ── Comments tab ── -->
        <div v-if="activeTab === 'comments'" class="tab-content">
          <!-- New comment -->
          <div class="comment-compose">
            <div class="compose-avatar" :style="{ background: memberGradient(auth.user?.username || 'U') }">
              {{ (auth.user?.username || 'U').charAt(0).toUpperCase() }}
            </div>
            <div class="compose-field" :class="{ 'compose-field--focused': commentFocused }">
              <textarea
                v-model="newComment"
                rows="2"
                placeholder="Write a comment…"
                class="compose-textarea"
                @focus="commentFocused = true"
                @blur="commentFocused = false"
              ></textarea>
              <div class="compose-actions">
                <button
                  class="btn-post"
                  :disabled="!newComment.trim() || postingComment"
                  @click="addComment"
                >
                  {{ postingComment ? 'Posting…' : 'Post' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="loadingComments" class="feed-empty">Loading comments…</div>
          <div v-else-if="comments.length === 0" class="feed-empty">No comments yet. Be the first!</div>
          <div v-else class="comments-feed">
            <div v-for="c in comments" :key="c.id" class="feed-item">
              <div class="feed-avatar" :style="{ background: memberGradient(c.user?.username || auth.user?.username || 'U') }">
                {{ (c.user?.username || auth.user?.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <div class="feed-body">
                <div class="feed-meta">
                  <span class="feed-author">{{ c.user?.username || auth.user?.username }}</span>
                  <span class="feed-time">{{ timeAgo(c.created_at) }}</span>
                  <button
                    v-if="c.user_id === auth.user?.id"
                    class="feed-delete"
                    @click="handleDeleteComment(c.id)"
                    title="Delete comment"
                  >
                    <font-awesome-icon :icon="['fas', 'trash']" style="font-size: 10px;" />
                  </button>
                </div>
                <p class="feed-text">{{ c.content }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Review Links tab ── -->
        <div v-if="activeTab === 'review'" class="tab-content">
          <div v-if="currentReviewLinks.length" class="rv-links-list">
            <div v-for="(link, i) in currentReviewLinks" :key="i" class="rv-link-row">
              <span class="rv-link-icon" :class="`rvli-${link.type}`">
                <font-awesome-icon :icon="reviewLinkIcon(link.type)" />
              </span>
              <div class="rv-link-info">
                <a :href="link.url" target="_blank" rel="noopener noreferrer" class="rv-link-label" @click.stop>
                  {{ link.label || link.url }}
                </a>
                <span class="rv-link-url">{{ link.url }}</span>
              </div>
              <button class="rv-link-del" @click="removeReviewLink(i)" title="Remove link">
                <font-awesome-icon :icon="['fas', 'xmark']" />
              </button>
            </div>
          </div>
          <p v-else class="desc-empty">No review links added yet.</p>

          <div class="rv-add-form">
            <p class="rv-add-title">Add a link</p>
            <select v-model="newLink.type" class="rv-type-select">
              <option value="repo">Repo / PR</option>
              <option value="doc">Document</option>
              <option value="design">Design</option>
              <option value="link">Other link</option>
            </select>
            <input v-model="newLink.url" class="rv-input" placeholder="https://…" type="url" @keydown.enter="addReviewLink" />
            <input v-model="newLink.label" class="rv-input" placeholder="Label (optional)" @keydown.enter="addReviewLink" />
            <button class="rv-add-btn" :disabled="!newLink.url.trim() || savingLinks" @click="addReviewLink">
              <font-awesome-icon :icon="['fas', 'plus']" />
              {{ savingLinks ? 'Saving…' : 'Add link' }}
            </button>
          </div>
        </div>

      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useConfirm } from '../../composables/useConfirm'
import { useTaskStore } from '../../stores/tasks'
import { useMembersStore } from '../../stores/members'
import { useAuthStore } from '../../stores/auth'
import { get, patch } from '../../stores/client'
import type { Task, TaskStatus, TaskPriority, WorkspaceMember, Comment } from '../../types'

const props = defineProps<{
  task: Task | null
  workspaceId: number | null
  projectId: number
}>()

const emit = defineEmits<{
  close: []
  deleted: []
  updated: [task: Task]
}>()

const taskStore = useTaskStore()
const membersStore = useMembersStore()
const auth = useAuthStore()
const { confirm } = useConfirm()

const editMode = ref(false)
const saving = ref(false)
const activeTab = ref<'description' | 'comments' | 'review'>('description')
const showAssigneePicker = ref(false)
const commentFocused = ref(false)

const comments = ref<Comment[]>([])
const newComment = ref('')
const postingComment = ref(false)
const loadingComments = ref(false)

const workspaceMembers = ref<WorkspaceMember[]>([])

const isAdmin = computed(() => {
  const role = membersStore.myMembership?.role
  return role === 'owner' || role === 'admin'
})

interface DrawerForm {
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority | number
  assigned_to_id: number | null
  due_date: string
  estimated_hours: number | null
  actual_hours: number | null
}

const form = reactive<DrawerForm>({
  title: '',
  description: '',
  status: 'todo',
  priority: 2,
  assigned_to_id: null,
  due_date: '',
  estimated_hours: null,
  actual_hours: null,
})

const statuses: { key: TaskStatus; label: string }[] = [
  { key: 'todo',        label: 'To Do' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'review',      label: 'Review' },
  { key: 'blocked',     label: 'Blocked' },
  { key: 'completed',   label: 'Done' },
]

const STATUS_LABELS: Record<TaskStatus, string> = {
  todo: 'To Do', in_progress: 'In Progress', review: 'Review', blocked: 'Blocked', completed: 'Done',
}
function statusLabel(s: TaskStatus) { return STATUS_LABELS[s] ?? s }

const MEMBER_ALLOWED: Record<string, Set<TaskStatus>> = {
  todo: new Set(['in_progress']),
  in_progress: new Set(['review']),
}

function canMemberChangeToStatus(toStatus: TaskStatus): boolean {
  if (isAdmin.value) return true
  if (!props.task) return false
  if (props.task.assigned_to_id !== auth.user?.id) return false
  return MEMBER_ALLOWED[props.task.status]?.has(toStatus) ?? false
}

const selectedAssignee = computed(() =>
  form.assigned_to_id
    ? workspaceMembers.value.find((m) => m.user_id === form.assigned_to_id) ?? null
    : null
)

const GRADIENTS = [
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
  return GRADIENTS[Math.abs(hash) % GRADIENTS.length]
}

function selectAssignee(userId: number | null) {
  form.assigned_to_id = userId
  showAssigneePicker.value = false
}

function priorityLabel(p: number): string {
  const labels: Record<number, string> = { 1: 'Low', 2: 'Medium', 3: 'High', 4: 'Urgent' }
  return labels[p] || ''
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function formatDateTime(d: string) {
  return new Date(d).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function timeAgo(d: string): string {
  const diff = Date.now() - new Date(d).getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return 'just now'
  if (min < 60) return `${min}m ago`
  const hr = Math.floor(min / 60)
  if (hr < 24) return `${hr}h ago`
  const day = Math.floor(hr / 24)
  if (day < 7) return `${day}d ago`
  return formatDate(d)
}

watch(
  () => props.task,
  (t) => {
    if (!t) return
    form.title = t.title
    form.description = t.description || ''
    form.status = t.status
    form.priority = t.priority
    form.assigned_to_id = t.assigned_to_id
    form.due_date = t.due_date ? t.due_date.slice(0, 10) : ''
    form.estimated_hours = t.estimated_hours
    form.actual_hours = t.actual_hours
    editMode.value = false
    activeTab.value = 'description'
    loadDrawerData(t)
  },
  { immediate: true }
)

async function loadDrawerData(t: Task) {
  loadingComments.value = true
  try {
    comments.value = await taskStore.fetchComments(t.id)
  } catch { /* noop */ } finally {
    loadingComments.value = false
  }
  if (props.workspaceId) {
    try {
      workspaceMembers.value = await get<WorkspaceMember[]>(`/workspaces/${props.workspaceId}/members`)
    } catch { /* noop */ }
  }
}

async function handleStatusChange(toStatus: TaskStatus) {
  if (!props.task) return
  if (form.status === toStatus) return
  if (!isAdmin.value && !canMemberChangeToStatus(toStatus)) return
  form.status = toStatus
  try {
    const updated = await patch<Task>(`/tasks/${props.task.id}`, { status: toStatus })
    emit('updated', updated)
  } catch (e) {
    form.status = props.task.status
    console.error(e)
  }
}

async function handleSave() {
  if (!props.task) return
  saving.value = true
  try {
    const payload: Record<string, any> = {
      title: form.title,
      description: form.description || null,
      status: form.status,
      priority: form.priority,
      assigned_to_id: form.assigned_to_id,
      estimated_hours: form.estimated_hours,
      actual_hours: form.actual_hours,
      due_date: form.due_date || null,
    }
    const updated = await patch<Task>(`/tasks/${props.task.id}`, payload)
    editMode.value = false
    emit('updated', updated)
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!props.task) return
  const ok = await confirm({
    title: 'Delete task?',
    message: `"${props.task.title}" will be permanently removed along with all its comments.`,
    confirmLabel: 'Yes, delete task',
    cancelLabel: 'Keep it',
    danger: true,
  })
  if (!ok) return
  await taskStore.remove(props.task.id)
  emit('deleted')
}

async function addComment() {
  if (!newComment.value.trim() || !props.task) return
  postingComment.value = true
  try {
    const c = await taskStore.createComment({ task_id: props.task.id, content: newComment.value.trim() })
    comments.value.push(c)
    newComment.value = ''
  } catch (e) {
    console.error(e)
  } finally {
    postingComment.value = false
  }
}

async function handleDeleteComment(id: number) {
  const ok = await confirm({
    title: 'Delete comment?',
    message: 'This comment will be permanently deleted.',
    confirmLabel: 'Delete comment',
    danger: true,
  })
  if (!ok) return
  await taskStore.deleteComment(id)
  comments.value = comments.value.filter((c) => c.id !== id)
}

onMounted(() => {
  const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') emit('close') }
  window.addEventListener('keydown', handler)
  return () => window.removeEventListener('keydown', handler)
})

// ── Review links ──────────────────────────────────────────
interface ReviewLink { url: string; label: string; type: string }

const newLink = reactive<ReviewLink>({ url: '', label: '', type: 'link' })
const savingLinks = ref(false)

const currentReviewLinks = computed<ReviewLink[]>(() => {
  const meta = props.task?.metadata_json as Record<string, any> | null
  return (meta?.review_links as ReviewLink[]) ?? []
})

function reviewLinkIcon(type: string): string[] {
  if (type === 'repo') return ['fas', 'code-branch']
  if (type === 'doc') return ['fas', 'file-lines']
  if (type === 'design') return ['fas', 'pen-ruler']
  return ['fas', 'link']
}

async function saveLinks(links: ReviewLink[]) {
  if (!props.task) return
  savingLinks.value = true
  try {
    const meta = { ...(props.task.metadata_json as Record<string, any> ?? {}), review_links: links }
    const updated = await patch<Task>(`/tasks/${props.task.id}`, { metadata_json: meta })
    emit('updated', updated)
  } finally {
    savingLinks.value = false
  }
}

async function addReviewLink() {
  if (!newLink.url.trim()) return
  await saveLinks([...currentReviewLinks.value, { url: newLink.url.trim(), label: newLink.label.trim(), type: newLink.type }])
  newLink.url = ''
  newLink.label = ''
  newLink.type = 'link'
}

async function removeReviewLink(index: number) {
  await saveLinks(currentReviewLinks.value.filter((_, i) => i !== index))
}
</script>

<style scoped>
/* ── Backdrop & panel ── */
.drawer-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 499;
  backdrop-filter: blur(2px);
}

.drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 520px;
  height: 100vh;
  background: var(--surface);
  border-left: 1px solid var(--border);
  z-index: 500;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  box-shadow: -12px 0 50px rgba(0,0,0,0.1);
}

/* ── Transitions ── */
.drawer-fade-enter-active, .drawer-fade-leave-active { transition: opacity 0.22s; }
.drawer-fade-enter-from, .drawer-fade-leave-to { opacity: 0; }

.drawer-slide-enter-active { transition: transform 0.28s cubic-bezier(0.34,1.1,0.64,1); }
.drawer-slide-leave-active  { transition: transform 0.22s ease; }
.drawer-slide-enter-from, .drawer-slide-leave-to { transform: translateX(100%); }

/* ── Header ── */
.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

.drawer-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  cursor: pointer;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: inherit;
  transition: all 0.12s;
}
.drawer-close:hover { background: #FFF1F2; border-color: #FECDD3; color: #BE123C; }

.drawer-header-actions {
  display: flex;
  align-items: center;
  gap: 7px;
}

.hdr-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  padding: 5px 11px;
  border-radius: 7px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  transition: all 0.12s;
}
.hdr-btn:hover { background: var(--surface); color: var(--text); border-color: var(--border-strong); }
.hdr-btn--active { background: var(--primary); color: #fff; border-color: var(--primary); }
.hdr-btn--active:hover { opacity: 0.88; color: #fff; }
.hdr-btn--danger:hover { background: #FFF1F2; border-color: #FECDD3; color: #BE123C; }

/* ── Title ── */
.drawer-title-wrap {
  padding: 22px 22px 0;
}

.drawer-title {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
  line-height: 1.3;
}

.title-textarea {
  width: 100%;
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.6px;
  line-height: 1.3;
  background: var(--bg);
  border: 1.5px solid var(--primary);
  border-radius: 10px;
  padding: 10px 13px;
  font-family: inherit;
  resize: none;
  box-shadow: 0 0 0 3px var(--primary-muted);
}
.title-textarea:focus { outline: none; }

/* ── Status pills row ── */
.status-row {
  display: flex;
  gap: 5px;
  padding: 16px 22px 0;
  flex-wrap: wrap;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 11px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  border: 1.5px solid transparent;
  font-family: inherit;
  transition: opacity 0.12s, box-shadow 0.12s, transform 0.1s;
}
.status-pill:hover:not(.sp-dimmed) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.sp-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.sp-todo        { background: #F1F5F9; color: #64748B; border-color: #CBD5E1; }
.sp-in_progress { background: #EFF6FF; color: #1D4ED8; border-color: #BFDBFE; }
.sp-review      { background: #FFFBEB; color: #92400E; border-color: #FDE68A; }
.sp-blocked     { background: #FFF1F2; color: #B91C1C; border-color: #FECDD3; }
.sp-completed   { background: #ECFDF5; color: #065F46; border-color: #A7F3D0; }

.sp-todo        .sp-dot { background: #94A3B8; }
.sp-in_progress .sp-dot { background: #3B82F6; }
.sp-review      .sp-dot { background: #F59E0B; }
.sp-blocked     .sp-dot { background: #EF4444; }
.sp-completed   .sp-dot { background: #10B981; }

.sp-active { box-shadow: 0 0 0 2px currentColor; }
.sp-dimmed { opacity: 0.35; cursor: not-allowed; }

/* ── Divider ── */
.drawer-divider {
  height: 1px;
  background: var(--border);
  margin: 20px 0 0;
}

/* ── Properties table ── */
.props-table {
  padding: 6px 0;
}

.prop-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  align-items: center;
  gap: 12px;
  padding: 9px 22px;
  transition: background 0.1s;
}
.prop-row:hover { background: rgba(0,0,0,0.02); }

.prop-label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  flex-shrink: 0;
}
.prop-label svg { flex-shrink: 0; opacity: 0.7; }

.prop-val {
  display: flex;
  align-items: center;
  min-width: 0;
}

.prop-text {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13.5px;
  color: var(--text);
  font-weight: 500;
}

.prop-empty {
  font-size: 13px;
  color: var(--text-light);
}

.prop-input {
  padding: 5px 9px;
  border: 1.5px solid var(--border);
  border-radius: 7px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.prop-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-muted); }
.prop-input--sm { width: 90px; }

.prop-select {
  padding: 5px 9px;
  border: 1.5px solid var(--border);
  border-radius: 7px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  cursor: pointer;
}
.prop-select:focus { outline: none; border-color: var(--primary); }

/* Status value pill */
.status-val-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  border: 1.5px solid transparent;
}
.svp-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.svp-todo        { background: #F1F5F9; color: #64748B; border-color: #CBD5E1; }
.svp-in_progress { background: #EFF6FF; color: #1D4ED8; border-color: #BFDBFE; }
.svp-review      { background: #FFFBEB; color: #92400E; border-color: #FDE68A; }
.svp-blocked     { background: #FFF1F2; color: #B91C1C; border-color: #FECDD3; }
.svp-completed   { background: #ECFDF5; color: #065F46; border-color: #A7F3D0; }
.svp-todo        .svp-dot { background: #94A3B8; }
.svp-in_progress .svp-dot { background: #3B82F6; }
.svp-review      .svp-dot { background: #F59E0B; }
.svp-blocked     .svp-dot { background: #EF4444; }
.svp-completed   .svp-dot { background: #10B981; }

/* Priority pills */
.priority-pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1.5px solid transparent;
}
.pp-1 { background: #ECFDF5; color: #065F46; border-color: #6EE7B7; }
.pp-2 { background: #FFFBEB; color: #78350F; border-color: #FCD34D; }
.pp-3 { background: #FFF7ED; color: #9A3412; border-color: #FDBA74; }
.pp-4 { background: #FFF1F2; color: #9F1239; border-color: #FCA5A5; }

/* Assignee picker */
.assignee-picker { position: relative; width: 100%; }
.picker-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 9px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  color: var(--text);
  text-align: left;
  transition: border-color 0.12s;
}
.picker-trigger:hover { border-color: var(--border-strong); }
.picker-open .picker-trigger { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-muted); }
.picker-backdrop { position: fixed; inset: 0; z-index: 50; }
.picker-dropdown {
  position: absolute;
  top: calc(100% + 5px);
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.14);
  z-index: 51;
  overflow: hidden;
  max-height: 240px;
  overflow-y: auto;
}
.picker-option {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 12px;
  cursor: pointer;
  transition: background 0.1s;
}
.picker-option:hover { background: var(--bg); }
.picker-unassigned { border-bottom: 1px solid var(--border); }
.po-info { flex: 1; display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.po-name { font-size: 13px; font-weight: 600; color: var(--text); }
.po-email { font-size: 11px; color: var(--text-light); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.po-check { flex-shrink: 0; color: var(--primary); margin-left: auto; }

.av-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 800;
  flex-shrink: 0;
}
.av-circle--sm { width: 28px; height: 28px; font-size: 11px; }

.av-empty {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bg);
  border: 1.5px dashed var(--border-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-light);
  flex-shrink: 0;
}
.av-name { flex: 1; font-size: 13px; font-weight: 600; color: var(--text); }
.av-empty-label { flex: 1; font-size: 13px; color: var(--text-light); }
.av-chevron { margin-left: auto; color: var(--text-light); flex-shrink: 0; }

.av-read {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

/* ── Save row ── */
.save-row {
  display: flex;
  gap: 8px;
  padding: 14px 22px;
  border-top: 1px solid var(--border);
}

.btn-save {
  display: inline-flex;
  align-items: center;
  padding: 7px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  font-family: inherit;
  background: var(--primary);
  color: #fff;
  border: none;
  cursor: pointer;
  transition: opacity 0.12s;
}
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-save:not(:disabled):hover { opacity: 0.88; }

.btn-cancel {
  display: inline-flex;
  align-items: center;
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  background: var(--bg);
  color: var(--text-muted);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.12s;
}
.btn-cancel:hover { background: var(--surface); color: var(--text); }

/* ── Tabs ── */
.drawer-tabs {
  display: flex;
  gap: 0;
  padding: 0 22px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  margin-top: 4px;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 11px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-family: inherit;
  transition: color 0.12s, border-color 0.12s;
  margin-bottom: -1px;
}
.tab-btn:hover { color: var(--text); }
.tab-active { color: var(--primary); border-bottom-color: var(--primary); }

.tab-badge {
  background: var(--primary-light);
  color: var(--primary);
  font-size: 10px;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 999px;
}

/* ── Tab content ── */
.tab-content {
  padding: 18px 22px 32px;
  flex: 1;
}

.desc-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  font-size: 13.5px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  line-height: 1.7;
  resize: vertical;
  min-height: 100px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.desc-textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-muted); }

.desc-text {
  font-size: 13.5px;
  line-height: 1.75;
  color: var(--text);
  white-space: pre-wrap;
}

.desc-empty {
  font-size: 13px;
  color: var(--text-light);
  font-style: italic;
}

/* ── Comment compose ── */
.comment-compose {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.compose-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  flex-shrink: 0;
  margin-top: 2px;
}

.compose-field {
  flex: 1;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.compose-field--focused {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.compose-textarea {
  width: 100%;
  padding: 10px 12px 6px;
  border: none;
  background: transparent;
  font-size: 13.5px;
  font-family: inherit;
  color: var(--text);
  resize: none;
  display: block;
  line-height: 1.6;
}
.compose-textarea:focus { outline: none; }
.compose-textarea::placeholder { color: var(--text-light); }

.compose-actions {
  padding: 7px 10px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border);
  background: var(--surface);
}

.btn-post {
  display: inline-flex;
  align-items: center;
  padding: 5px 14px;
  border-radius: 7px;
  font-size: 12.5px;
  font-weight: 700;
  font-family: inherit;
  background: var(--primary);
  color: #fff;
  border: none;
  cursor: pointer;
  transition: opacity 0.12s;
}
.btn-post:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-post:not(:disabled):hover { opacity: 0.88; }

/* ── Comments feed ── */
.feed-empty {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  padding: 20px 0;
}

.comments-feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feed-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.feed-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  flex-shrink: 0;
}

.feed-body { flex: 1; min-width: 0; }

.feed-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.feed-author {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

.feed-time {
  font-size: 11.5px;
  color: var(--text-light);
  flex: 1;
}

.feed-delete {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-light);
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.12s, color 0.12s;
}
.feed-item:hover .feed-delete { opacity: 1; }
.feed-delete:hover { color: var(--danger, #EF4444); }

.feed-text {
  font-size: 13.5px;
  line-height: 1.6;
  color: var(--text);
  word-break: break-word;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
}

/* ── Dark mode ── */
:global([data-theme="dark"]) .drawer {
  background: #1E2732;
  border-left-color: #38444D;
  box-shadow: -12px 0 50px rgba(0,0,0,0.5);
}
:global([data-theme="dark"]) .drawer-header {
  background: #1E2732;
  border-bottom-color: #38444D;
}
:global([data-theme="dark"]) .drawer-close {
  background: #253341;
  border-color: #38444D;
}
:global([data-theme="dark"]) .drawer-close:hover {
  background: rgba(190,18,60,0.2);
  border-color: rgba(190,18,60,0.4);
  color: #FF6B78;
}
:global([data-theme="dark"]) .hdr-btn {
  background: #253341;
  border-color: #38444D;
  color: var(--text-muted);
}
:global([data-theme="dark"]) .hdr-btn:hover { background: #2E3D4D; color: var(--text); }
:global([data-theme="dark"]) .hdr-btn--active { background: var(--primary); border-color: var(--primary); color: #fff; }
:global([data-theme="dark"]) .drawer-divider { background: #38444D; }
:global([data-theme="dark"]) .prop-row:hover { background: rgba(255,255,255,0.03); }
:global([data-theme="dark"]) .prop-input,
:global([data-theme="dark"]) .prop-select { background: #253341; border-color: #38444D; color: var(--text); }
:global([data-theme="dark"]) .title-textarea { background: #253341; border-color: var(--primary); color: var(--text); }
:global([data-theme="dark"]) .desc-textarea { background: #253341; border-color: #38444D; color: var(--text); }
:global([data-theme="dark"]) .compose-field { background: #1E2732; border-color: #38444D; }
:global([data-theme="dark"]) .compose-actions { background: #15202B; border-top-color: #38444D; }
:global([data-theme="dark"]) .feed-text { background: #15202B; border-color: #38444D; }
:global([data-theme="dark"]) .picker-dropdown { background: #1E2732; border-color: #38444D; }
:global([data-theme="dark"]) .picker-option:hover { background: #253341; }
:global([data-theme="dark"]) .picker-trigger { background: #253341; border-color: #38444D; }
:global([data-theme="dark"]) .av-empty { background: #253341; border-color: #536471; }
:global([data-theme="dark"]) .save-row { border-top-color: #38444D; }
:global([data-theme="dark"]) .btn-cancel { background: #253341; border-color: #38444D; color: var(--text-muted); }

:global([data-theme="dark"]) .sp-todo        { background: rgba(255,255,255,0.07); color: #8B98A5; border-color: #38444D; }
:global([data-theme="dark"]) .sp-in_progress { background: rgba(91,155,255,0.18); color: #5B9BFF; border-color: rgba(91,155,255,0.35); }
:global([data-theme="dark"]) .sp-review      { background: rgba(255,179,0,0.18); color: #FFB300; border-color: rgba(255,179,0,0.35); }
:global([data-theme="dark"]) .sp-blocked     { background: rgba(255,107,120,0.18); color: #FF6B78; border-color: rgba(255,107,120,0.35); }
:global([data-theme="dark"]) .sp-completed   { background: rgba(0,186,124,0.18); color: #00BA7C; border-color: rgba(0,186,124,0.35); }

:global([data-theme="dark"]) .svp-todo        { background: rgba(255,255,255,0.07); color: #8B98A5; border-color: #38444D; }
:global([data-theme="dark"]) .svp-in_progress { background: rgba(91,155,255,0.15); color: #5B9BFF; border-color: rgba(91,155,255,0.3); }
:global([data-theme="dark"]) .svp-review      { background: rgba(255,179,0,0.15); color: #FFB300; border-color: rgba(255,179,0,0.3); }
:global([data-theme="dark"]) .svp-blocked     { background: rgba(255,107,120,0.15); color: #FF6B78; border-color: rgba(255,107,120,0.3); }
:global([data-theme="dark"]) .svp-completed   { background: rgba(0,186,124,0.15); color: #00BA7C; border-color: rgba(0,186,124,0.3); }

:global([data-theme="dark"]) .pp-1 { background: rgba(0,186,124,0.15); color: #00BA7C; border-color: rgba(0,186,124,0.3); }
:global([data-theme="dark"]) .pp-2 { background: rgba(255,179,0,0.15); color: #FFB300; border-color: rgba(255,179,0,0.3); }
:global([data-theme="dark"]) .pp-3 { background: rgba(249,115,22,0.15); color: #FB923C; border-color: rgba(249,115,22,0.3); }
:global([data-theme="dark"]) .pp-4 { background: rgba(255,107,120,0.15); color: #FF6B78; border-color: rgba(255,107,120,0.3); }

/* ── Review Links tab ── */
.tab-btn--review {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.rv-links-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.rv-link-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1.5px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  transition: border-color 0.12s;
}
.rv-link-row:hover { border-color: var(--border-strong); }

.rv-link-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}
.rvli-repo   { background: #F0FDF4; color: #16A34A; }
.rvli-doc    { background: #EFF6FF; color: #2563EB; }
.rvli-design { background: #FDF4FF; color: #9333EA; }
.rvli-link   { background: #F8FAFC; color: #475569; }
:global([data-theme="dark"]) .rvli-repo   { background: rgba(22,163,74,0.18); color: #4ADE80; }
:global([data-theme="dark"]) .rvli-doc    { background: rgba(37,99,235,0.18); color: #60A5FA; }
:global([data-theme="dark"]) .rvli-design { background: rgba(147,51,234,0.18); color: #C084FC; }
:global([data-theme="dark"]) .rvli-link   { background: rgba(255,255,255,0.07); color: #8B98A5; }

.rv-link-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rv-link-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  text-decoration: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rv-link-label:hover { text-decoration: underline; }

.rv-link-url {
  font-size: 11px;
  color: var(--text-light);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rv-link-del {
  width: 26px;
  height: 26px;
  border: none;
  background: none;
  color: var(--text-light);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background 0.12s, color 0.12s;
  flex-shrink: 0;
}
.rv-link-del:hover { background: #FEE2E2; color: #DC2626; }
:global([data-theme="dark"]) .rv-link-del:hover { background: rgba(220,38,38,0.18); color: #F87171; }

.rv-add-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  border-radius: 12px;
}

.rv-add-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin: 0;
}

.rv-type-select {
  padding: 8px 10px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  outline: none;
}
.rv-type-select:focus { border-color: var(--primary); }

.rv-input {
  padding: 8px 12px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  background: var(--surface);
  color: var(--text);
  outline: none;
  transition: border-color 0.14s;
}
.rv-input:focus { border-color: var(--primary); }
.rv-input::placeholder { color: var(--text-light); }
:global([data-theme="dark"]) .rv-input { background: #253341; border-color: #38444D; }
:global([data-theme="dark"]) .rv-type-select { background: #253341; border-color: #38444D; }

.rv-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 16px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: opacity 0.14s;
  align-self: flex-start;
}
.rv-add-btn:hover { opacity: 0.82; }
.rv-add-btn:disabled { opacity: 0.4; cursor: not-allowed; }
:global([data-theme="dark"]) .rv-add-btn { background: #F7F9F9; color: #15202B; }
</style>
