<template>
  <div class="milestone-panel">
    <div class="mp-head">
      <div class="mp-head-left">
        <h3 class="mp-title">
          <font-awesome-icon :icon="['fas', 'flag-checkered']" />
          Milestones
        </h3>
        <p class="mp-sub">Track key dates and achievements for this project.</p>
      </div>
      <button v-if="isAdmin" class="btn btn-sm" @click="showForm = true">
        <font-awesome-icon :icon="['fas', 'plus']" />
        Add milestone
      </button>
    </div>

    <div v-if="showForm" class="mp-form">
      <input v-model="form.name" class="mp-input" placeholder="Milestone name" maxlength="255" />
      <input v-model="form.description" class="mp-input" placeholder="Description (optional)" />
      <input v-model="form.due_date" type="date" class="mp-input mp-input--sm" />
      <div class="mp-form-actions">
        <button class="btn btn-sm btn-primary" :disabled="!form.name.trim() || saving" @click="handleCreate">
          {{ saving ? 'Creating…' : 'Create' }}
        </button>
        <button class="btn btn-sm btn-ghost" @click="closeForm">Cancel</button>
      </div>
    </div>

    <div v-if="store.loading" class="mp-loading">Loading milestones…</div>

    <div v-else-if="store.milestones.length === 0" class="mp-empty">
      <div class="mp-empty-icon">
        <font-awesome-icon :icon="['fas', 'flag']" />
      </div>
      <p class="mp-empty-title">No milestones yet</p>
      <p class="mp-empty-sub">Add milestones to mark important dates and project phases.</p>
    </div>

    <div v-else class="mp-list">
      <div
        v-for="m in store.milestones"
        :key="m.id"
        class="mp-item"
        :class="{ 'mp-item--achieved': m.status === 'achieved', 'mp-item--cancelled': m.status === 'cancelled' }"
      >
        <div class="mp-item-left">
          <div class="mp-status-icon" :class="`msi-${m.status}`">
            <font-awesome-icon v-if="m.status === 'achieved'" :icon="['fas', 'check']" />
            <font-awesome-icon v-else-if="m.status === 'cancelled'" :icon="['fas', 'xmark']" />
            <font-awesome-icon v-else :icon="['fas', 'flag']" />
          </div>
          <div class="mp-item-body">
            <div class="mp-item-title-row">
              <span class="mp-item-name">{{ m.name }}</span>
              <span v-if="m.due_date" class="mp-item-date">
                <font-awesome-icon :icon="['far', 'calendar']" />
                {{ formatDate(m.due_date) }}
              </span>
            </div>
            <p v-if="m.description" class="mp-item-desc">{{ m.description }}</p>
            <div class="mp-item-meta">
              <span class="mp-status-badge" :class="`msb-${m.status}`">{{ statusLabel(m.status) }}</span>
              <span v-if="m.achieved_at" class="mp-achieved-date">Achieved {{ formatDate(m.achieved_at) }}</span>
            </div>
          </div>
        </div>
        <div class="mp-item-actions">
          <select
            v-if="isAdmin"
            class="mp-status-select"
            :value="m.status"
            @change="handleStatusChange(m, ($event.target as HTMLSelectElement).value)"
          >
            <option value="pending">Pending</option>
            <option value="achieved">Achieved</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <button
            v-if="isAdmin"
            class="mp-delete-btn"
            title="Delete milestone"
            @click="handleDelete(m)"
          >
            <font-awesome-icon :icon="['fas', 'trash-can']" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMilestoneStore } from '../../stores/milestones'
import { useMembersStore } from '../../stores/members'
import { useConfirm } from '../../composables/useConfirm'
import { useToast } from '../../composables/useToast'
import type { Milestone, MilestoneStatus } from '../../types'

const props = defineProps<{ projectId: number }>()

const store = useMilestoneStore()
const membersStore = useMembersStore()
const { confirm } = useConfirm()
const toast = useToast()

const showForm = ref(false)
const saving = ref(false)

const form = reactive({ name: '', description: '', due_date: '' })

const isAdmin = ref(false)

onMounted(async () => {
  await store.fetchByProject(props.projectId)
  const role = membersStore.myMembership?.role
  isAdmin.value = role === 'admin' || role === 'owner'
})

function closeForm() {
  showForm.value = false
  form.name = ''
  form.description = ''
  form.due_date = ''
}

async function handleCreate() {
  if (!form.name.trim()) return
  saving.value = true
  try {
    await store.create(props.projectId, {
      name: form.name.trim(),
      description: form.description || null,
      due_date: form.due_date || null,
    })
    closeForm()
    toast.success('Milestone created')
  } catch (e: any) {
    toast.error(e?.message || 'Failed to create milestone')
  } finally {
    saving.value = false
  }
}

async function handleStatusChange(m: Milestone, status: string) {
  try {
    await store.update(props.projectId, m.id, { status: status as MilestoneStatus })
    toast.success(`Milestone ${status === 'achieved' ? 'achieved' : status}`)
  } catch (e: any) {
    toast.error(e?.message || 'Failed to update milestone')
  }
}

async function handleDelete(m: Milestone) {
  const ok = await confirm({
    title: 'Delete milestone?',
    message: `"${m.name}" will be permanently removed.`,
    confirmLabel: 'Delete',
    cancelLabel: 'Keep',
    danger: true,
  })
  if (!ok) return
  try {
    await store.remove(props.projectId, m.id)
    toast.success('Milestone deleted')
  } catch (e: any) {
    toast.error(e?.message || 'Failed to delete milestone')
  }
}

const STATUS_LABELS: Record<string, string> = { pending: 'Pending', achieved: 'Achieved', cancelled: 'Cancelled' }
function statusLabel(s: string) { return STATUS_LABELS[s] || s }

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<style scoped>
.milestone-panel {
  padding-top: 24px;
}

.mp-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.mp-head-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mp-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.mp-sub {
  font-size: 13px;
  color: var(--text-muted);
}

.mp-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  margin-bottom: 20px;
}

.mp-input {
  padding: 8px 11px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  transition: border-color 0.15s;
}

.mp-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.mp-input--sm {
  width: 180px;
}

.mp-form-actions {
  display: flex;
  gap: 8px;
}

.mp-loading {
  text-align: center;
  padding: 40px;
  color: var(--text-light);
  font-size: 13px;
}

.mp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 50px 20px;
  text-align: center;
}

.mp-empty-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--bg);
  border: 1.5px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--text-light);
}

.mp-empty-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.mp-empty-sub {
  font-size: 13px;
  color: var(--text-muted);
  max-width: 300px;
  line-height: 1.5;
}

.mp-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mp-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  transition: border-color 0.12s, opacity 0.2s;
}

.mp-item:hover {
  border-color: var(--border-strong);
}

.mp-item--achieved {
  opacity: 0.7;
  border-left: 3px solid #10B981;
}

.mp-item--cancelled {
  opacity: 0.5;
  border-left: 3px solid #EF4444;
}

.mp-item-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.mp-status-icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
  margin-top: 1px;
}

.msi-pending {
  background: #F1F5F9;
  color: #64748B;
  border: 1px solid #CBD5E1;
}

.msi-achieved {
  background: #ECFDF5;
  color: #065F46;
  border: 1px solid #A7F3D0;
}

.msi-cancelled {
  background: #FFF1F2;
  color: #B91C1C;
  border: 1px solid #FECDD3;
}

.mp-item-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.mp-item-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.mp-item-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.mp-item-date {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--text-light);
}

.mp-item-date svg {
  font-size: 10px;
}

.mp-item-desc {
  font-size: 12.5px;
  color: var(--text-muted);
  line-height: 1.5;
}

.mp-item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
}

.mp-status-badge {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}

.msb-pending   { background: #F1F5F9; color: #64748B; }
.msb-achieved  { background: #ECFDF5; color: #065F46; }
.msb-cancelled { background: #FFF1F2; color: #B91C1C; }

.mp-achieved-date {
  font-size: 11px;
  color: var(--text-light);
}

.mp-item-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.mp-status-select {
  padding: 4px 8px;
  border: 1.5px solid var(--border);
  border-radius: 7px;
  font-size: 12px;
  font-family: inherit;
  color: var(--text);
  background: var(--bg);
  cursor: pointer;
}

.mp-status-select:focus {
  outline: none;
  border-color: var(--primary);
}

.mp-delete-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: var(--text-light);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.12s;
}

.mp-delete-btn:hover {
  background: #FFF1F2;
  color: #BE123C;
}

:global([data-theme="dark"]) .mp-item {
  background: #1A2D42;
  border-color: rgba(91, 155, 255, 0.20);
}

:global([data-theme="dark"]) .mp-item:hover {
  border-color: rgba(91, 155, 255, 0.35);
}

:global([data-theme="dark"]) .mp-form {
  background: #1E2732;
  border-color: #38444D;
}

:global([data-theme="dark"]) .mp-input {
  background: #253341;
  border-color: #38444D;
  color: var(--text);
}

:global([data-theme="dark"]) .msi-pending {
  background: rgba(255, 255, 255, 0.07);
  color: #8B98A5;
  border-color: #38444D;
}

:global([data-theme="dark"]) .msi-achieved {
  background: rgba(0, 186, 124, 0.15);
  color: #00BA7C;
  border-color: rgba(0, 186, 124, 0.3);
}

:global([data-theme="dark"]) .msi-cancelled {
  background: rgba(255, 107, 120, 0.15);
  color: #FF6B78;
  border-color: rgba(255, 107, 120, 0.3);
}

:global([data-theme="dark"]) .mp-status-select {
  background: #253341;
  border-color: #38444D;
  color: var(--text);
}

:global([data-theme="dark"]) .mp-delete-btn:hover {
  background: rgba(190, 18, 60, 0.2);
  color: #FF6B78;
}

:global([data-theme="dark"]) .mp-empty-icon {
  background: #253341;
  border-color: #38444D;
}
</style>
