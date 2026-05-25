<template>
  <div class="invite-page">
    <div class="invite-card">
      <!-- Logo -->
      <div class="invite-brand">
        <div class="brand-mark">
          <svg viewBox="0 0 20 20" fill="none" width="16" height="16">
            <path d="M3 16V7l4 5 3-7 3 7 4-5v9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="brand-name">Mogul Manager</span>
      </div>

      <!-- Loading -->
      <div v-if="state === 'loading'" class="invite-content">
        <div class="spinner"></div>
        <p class="invite-sub">Loading invitation…</p>
      </div>

      <!-- Error states -->
      <div v-else-if="state === 'invalid'" class="invite-content">
        <div class="state-icon state-icon--error">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
            <path d="M15 9l-6 6M9 9l6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>Invalid invitation</h2>
        <p class="invite-sub">This invite link is invalid or does not exist.</p>
        <router-link to="/login" class="btn btn-primary action-btn">Go to Login</router-link>
      </div>

      <div v-else-if="state === 'expired'" class="invite-content">
        <div class="state-icon state-icon--warn">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
            <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>Invitation expired</h2>
        <p class="invite-sub">This invite link has expired. Ask the workspace owner to send a new one.</p>
      </div>

      <div v-else-if="state === 'accepted'" class="invite-content">
        <div class="state-icon state-icon--success">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
            <path d="M8 12l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h2>Already accepted</h2>
        <p class="invite-sub">You have already joined this workspace.</p>
        <router-link v-if="invitation" :to="`/workspaces/${invitation.workspace_id}`" class="btn btn-primary action-btn">
          Open Workspace
        </router-link>
      </div>

      <div v-else-if="state === 'revoked'" class="invite-content">
        <div class="state-icon state-icon--error">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
            <path d="M15 9l-6 6M9 9l6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>Invitation revoked</h2>
        <p class="invite-sub">This invitation has been revoked. Contact the workspace owner for a new invite.</p>
      </div>

      <!-- Ready: logged in -->
      <div v-else-if="state === 'ready' && isLoggedIn && invitation" class="invite-content">
        <div class="state-icon state-icon--info">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="1.8"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>You're invited!</h2>
        <p class="invite-sub">
          You've been invited to join
          <strong>{{ invitation.workspace_title || 'a workspace' }}</strong>
          as <span class="role-chip" :class="`role-chip--${invitation.role}`">{{ invitation.role }}</span>.
        </p>
        <p v-if="joinError" class="form-error">{{ joinError }}</p>
        <button
          class="btn btn-primary action-btn"
          :disabled="joining"
          @click="handleAccept"
        >
          <span v-if="joining" class="btn-spinner"></span>
          {{ joining ? 'Joining…' : `Join workspace` }}
        </button>
      </div>

      <!-- Ready: not logged in -->
      <div v-else-if="state === 'ready' && !isLoggedIn && invitation" class="invite-content">
        <div class="state-icon state-icon--info">
          <svg viewBox="0 0 24 24" fill="none" width="26" height="26">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="1.8"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>You're invited!</h2>
        <p class="invite-sub">
          You've been invited to join
          <strong>{{ invitation.workspace_title || 'a workspace' }}</strong>
          as <span class="role-chip" :class="`role-chip--${invitation.role}`">{{ invitation.role }}</span>.
        </p>
        <p class="invite-sub muted">Sign in or create an account to accept this invitation.</p>
        <div class="invite-actions">
          <router-link
            :to="`/register?next=/invite/${token}`"
            class="btn btn-primary action-btn"
          >
            Create account to join
          </router-link>
          <router-link
            :to="`/login?next=/invite/${token}`"
            class="btn action-btn"
          >
            Sign in to join
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useMembersStore } from '../stores/members'
import type { Invitation } from '../types'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const membersStore = useMembersStore()

const token = route.params.token as string
const invitation = ref<Invitation | null>(null)
const state = ref<'loading' | 'ready' | 'invalid' | 'expired' | 'accepted' | 'revoked'>('loading')
const joining = ref(false)
const joinError = ref<string | null>(null)

const isLoggedIn = computed(() => !!auth.token)

onMounted(async () => {
  try {
    const info = await membersStore.getInviteInfo(token)
    invitation.value = info

    if (info.status === 'expired') {
      state.value = 'expired'
    } else if (info.status === 'accepted') {
      state.value = 'accepted'
    } else if (info.status === 'revoked') {
      state.value = 'revoked'
    } else {
      state.value = 'ready'
    }
  } catch {
    state.value = 'invalid'
  }
})

async function handleAccept() {
  if (!invitation.value) return
  joinError.value = null
  joining.value = true
  try {
    await membersStore.acceptInvite(token)
    router.push(`/workspaces/${invitation.value.workspace_id}`)
  } catch (e) {
    joinError.value = (e as Error).message
  } finally {
    joining.value = false
  }
}
</script>

<style scoped>
.invite-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  padding: 24px;
}

.invite-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 48px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow);
}

.invite-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 36px;
}

.brand-mark {
  width: 32px;
  height: 32px;
  background: var(--primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.invite-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  text-align: center;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.state-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.state-icon--error   { background: #FEF2F2; border: 1px solid #FECACA; color: var(--danger); }
.state-icon--warn    { background: #FFFBEB; border: 1px solid #FDE68A; color: #D97706; }
.state-icon--success { background: #F0FDF4; border: 1px solid #BBF7D0; color: #16A34A; }
.state-icon--info    { background: #EFF6FF; border: 1px solid #BFDBFE; color: #2563EB; }

h2 {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
}

.invite-sub {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  max-width: 320px;
}

.invite-sub.muted {
  font-size: 13px;
  color: var(--text-light);
}

.role-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.role-chip--owner  { background: #F3E8FF; color: #7C3AED; }
.role-chip--admin  { background: #EFF6FF; color: #2563EB; }
.role-chip--member { background: var(--bg); color: var(--text-muted); border: 1px solid var(--border); }

.invite-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  margin-top: 4px;
}

.action-btn {
  width: 100%;
  padding: 11px 20px;
  font-size: 14px;
  border-radius: 10px;
  justify-content: center;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

.form-error {
  font-size: 13px;
  color: var(--danger);
}
</style>
