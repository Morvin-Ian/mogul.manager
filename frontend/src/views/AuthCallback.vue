<template>
  <div class="callback-page">
    <div class="callback-card">
      <div v-if="state === 'loading'" class="callback-content">
        <div class="spinner"></div>
        <p class="callback-msg">Completing sign-in…</p>
      </div>
      <div v-else-if="state === 'error'" class="callback-content">
        <div class="error-icon">
          <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
            <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>Sign-in failed</h2>
        <p class="callback-msg">{{ errorMessage }}</p>
        <router-link to="/login" class="btn btn-primary back-btn">Back to Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const state = ref<'loading' | 'error'>('loading')
const errorMessage = ref('Google sign-in failed. Please try again.')

function isValidRedirect(path: string): boolean {
  try {
    const url = new URL(path, window.location.origin)
    return url.origin === window.location.origin && path.startsWith('/')
  } catch {
    return false
  }
}

onMounted(async () => {
  // Read token and next from URL hash fragment, not query string
  const hashParams = new URLSearchParams(route.hash.replace(/^#/, ''))
  const token = hashParams.get('token') || (route.query.token as string | undefined)
  const error = route.query.error as string | undefined
  const next = hashParams.get('next') || (route.query.next as string | undefined)

  if (error) {
    errorMessage.value = 'Google sign-in failed. Please try again.'
    state.value = 'error'
    return
  }

  if (!token) {
    errorMessage.value = 'No token received. Please try again.'
    state.value = 'error'
    return
  }

  localStorage.setItem('token', token)
  // Sync token into the store
  ;(auth as any).token = token
  // Re-initialise — fetchUser reads from the store token ref
  try {
    await auth.fetchUser()
    router.replace(next && isValidRedirect(next) ? next : '/')
  } catch {
    errorMessage.value = 'Failed to load user data. Please try again.'
    state.value = 'error'
  }
})
</script>

<style scoped>
.callback-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
}

.callback-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 48px 40px;
  text-align: center;
  width: 100%;
  max-width: 380px;
  box-shadow: var(--shadow);
}

.callback-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
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

.error-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #FEF2F2;
  border: 1px solid #FECACA;
  color: var(--danger);
  display: flex;
  align-items: center;
  justify-content: center;
}

h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.4px;
}

.callback-msg {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.55;
}

.back-btn {
  margin-top: 8px;
  padding: 10px 24px;
  font-size: 14px;
  border-radius: 10px;
}
</style>
