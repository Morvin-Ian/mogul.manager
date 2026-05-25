<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>Invite a member</h3>
        <button class="modal-close" @click="$emit('close')" aria-label="Close">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
            <path d="M1 1l12 12M13 1L1 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <div v-if="successMsg" class="success-banner">
        <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
          <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.4"/>
          <path d="M5 8l2.5 2.5L11 5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ successMsg }}
      </div>

      <form v-else @submit.prevent="handleInvite" novalidate>
        <div class="form-group">
          <label for="invite-email">Email address</label>
          <input
            id="invite-email"
            v-model="email"
            type="email"
            required
            placeholder="colleague@example.com"
            autocomplete="off"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="invite-role">Role</label>
          <select id="invite-role" v-model="role" :disabled="loading">
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>
          <p class="field-hint">
            <span v-if="role === 'admin'">Admins can invite/remove members and manage projects.</span>
            <span v-else>Members can view and work on projects and tasks.</span>
          </p>
        </div>

        <p v-if="errorMsg" class="form-error">{{ errorMsg }}</p>

        <div class="modal-actions">
          <button type="button" class="btn" @click="$emit('close')" :disabled="loading">Cancel</button>
          <button type="submit" class="btn btn-primary" :disabled="loading || !email.trim()">
            <span v-if="loading" class="btn-spinner"></span>
            {{ loading ? 'Sending…' : 'Send Invite' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useMembersStore } from '../../stores/members'
import type { MemberRole } from '../../types'

const props = defineProps<{ workspaceId: number }>()
const emit = defineEmits<{ (e: 'close'): void }>()

const membersStore = useMembersStore()

const email = ref('')
const role = ref<MemberRole>('member')
const loading = ref(false)
const errorMsg = ref<string | null>(null)
const successMsg = ref<string | null>(null)

async function handleInvite() {
  if (!email.value.trim()) return
  errorMsg.value = null
  loading.value = true
  try {
    await membersStore.invite(props.workspaceId, email.value.trim(), role.value)
    successMsg.value = `Invite sent to ${email.value.trim()}`
    setTimeout(() => emit('close'), 2000)
  } catch (e) {
    errorMsg.value = (e as Error).message || 'Failed to send invitation.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal {
  width: 100%;
  max-width: 440px;
}

h3 {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #F0FDF4;
  border: 1px solid #BBF7D0;
  color: #16A34A;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.field-hint {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 6px;
  line-height: 1.5;
}

.form-error {
  font-size: 13px;
  color: var(--danger);
  margin-top: 2px;
}

.btn-spinner {
  width: 13px;
  height: 13px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

@keyframes spin { to { transform: rotate(360deg); } }

select {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius, 8px);
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  outline: none;
  cursor: pointer;
  appearance: auto;
}

select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 82, 255, 0.08);
}
</style>
