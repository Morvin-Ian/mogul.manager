<template>
  <div class="invite-page">
    <Loading v-if="loading" label="Loading invitation…" />

    <div v-else-if="error" class="invite-card error-card">
      <div class="invite-icon error-icon">
        <svg viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
          <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
      </div>
      <h2>Invitation not found</h2>
      <p>This invitation link is invalid or has expired.</p>
      <router-link to="/" class="btn btn-primary">Go home</router-link>
    </div>

    <div v-else-if="invite" class="invite-card">
      <div class="invite-icon">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M3 9l9 6 9-6v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M3 9l9 6 9-6V7a2 2 0 00-2-2H5a2 2 0 00-2 2v2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
        </svg>
      </div>
      <h2>You're invited!</h2>
      <p class="invite-desc">
        <strong>{{ invite.workspace.title }}</strong>
      </p>
      <p class="invite-role">Role: <span class="role-badge">{{ invite.role }}</span></p>
      <p class="invite-email">To: {{ invite.email }}</p>

      <div v-if="invite.status !== 'pending'" class="status-msg">
        This invitation has been {{ invite.status }}.
      </div>

      <template v-else-if="isLoggedIn">
        <button class="btn btn-primary btn-lg" @click="handleAccept" :disabled="accepting">
          {{ accepting ? 'Joining…' : 'Join workspace' }}
        </button>
      </template>

      <template v-else>
        <p class="signin-hint">Sign in or create an account to join.</p>
        <div class="invite-actions">
          <router-link :to="`/login?next=${encodedPath}`" class="btn btn-primary btn-lg">Sign in</router-link>
          <router-link :to="`/register?next=${encodedPath}`" class="btn btn-lg">Create account</router-link>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMembersStore } from '../stores/members'
import { useAuthStore } from '../stores/auth'
import type { InvitationInfo } from '../types'
import Loading from '../components/common/Loading.vue'

const route = useRoute()
const router = useRouter()
const membersStore = useMembersStore()
const auth = useAuthStore()

const invite = ref<InvitationInfo | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const accepting = ref(false)

const isLoggedIn = computed(() => !!auth.token)

const token = computed(() => route.params.token as string)
const encodedPath = computed(() => encodeURIComponent(`/invitations/${token.value}`))

onMounted(async () => {
  try {
    invite.value = await membersStore.getInviteInfo(token.value)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
})

async function handleAccept() {
  if (!token.value) return
  accepting.value = true
  try {
    const res = await membersStore.acceptInvite(token.value)
    router.push(`/workspaces/${res.workspace_id}`)
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    accepting.value = false
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
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 48px 40px;
  max-width: 420px;
  width: 100%;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.06);
}

.error-card { border-color: #FECDD3; }

.invite-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}
.invite-icon svg { width: 24px; height: 24px; }

.error-icon { background: #FFF1F2; color: #BE123C; }

h2 { font-size: 24px; font-weight: 800; color: var(--text); }
.invite-desc { font-size: 15px; color: var(--text-muted); margin-bottom: 4px; }
.invite-role { font-size: 13px; color: var(--text-muted); }
.role-badge {
  display: inline-block;
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 600;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  font-size: 12px;
  text-transform: capitalize;
}
.invite-email { font-size: 12px; color: var(--text-light); }

.status-msg {
  color: #BE123C;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  background: #FFF1F2;
  border-radius: var(--radius);
  width: 100%;
}

.signin-hint { font-size: 13px; color: var(--text-muted); margin-top: 12px; }

.invite-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  margin-top: 4px;
}

.btn-lg {
  width: 100%;
  padding: 12px;
  font-size: 14.5px;
  text-align: center;
  border-radius: 11px;
}
</style>
