<template>
  <div class="auth-page">
    <div class="auth-brand-panel">
      <div class="brand-inner">
        <div class="brand-logo-row">
          <span class="brand-wordmark">mogul<span class="brand-dot">.</span></span>
          <span class="brand-submark">manager</span>
        </div>
        <h2 class="brand-headline">Your workspace,<br />supercharged by AI</h2>
        <p class="brand-sub">Track projects, manage tasks, and get AI-driven insights — for free.</p>
      </div>
    </div>

    <div class="auth-form-panel">
      <div class="auth-form-inner">
        <div class="auth-form-header">
          <h1>Create your account</h1>
          <p class="auth-subtitle">Get started with Mogul Manager for free</p>
        </div>
        <form @submit.prevent="handleRegister" novalidate>
          <div class="form-group">
            <label for="username">Username</label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              minlength="2"
              placeholder="Choose a username"
              autocomplete="username"
            />
          </div>
          <div class="form-group">
            <label for="email">Email address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              placeholder="name@example.com"
              autocomplete="email"
            />
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              minlength="8"
              placeholder="Min. 8 characters"
              autocomplete="new-password"
            />
            <p class="field-hint">At least 8 characters with a mix of letters and numbers.</p>
          </div>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
            <span v-if="loading" class="btn-loader"></span>
            {{ loading ? 'Creating account…' : 'Create account' }}
          </button>
          <div class="divider"><span>or</span></div>
          <a href="/api/auth/google" class="btn btn-google">
            <svg viewBox="0 0 24 24" width="18" height="18" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </a>
        </form>
        <div class="auth-footer">
          <p class="auth-link">
            Already have an account?
            <router-link to="/login">Sign in →</router-link>
          </p>
        </div>
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
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

onMounted(() => {
  if (route.query.error === 'oauth_failed') {
    error.value = 'Google sign-in failed. Please try again.'
  }
})

async function handleRegister() {
  error.value = null
  loading.value = true
  try {
    await auth.register({ username: username.value, email: email.value, password: password.value })
    await auth.login(email.value, password.value)
    const next = route.query.next as string | undefined
    if (next && next.startsWith('/')) {
      router.push(next)
    } else {
      router.push('/')
    }
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  min-height: 100vh;
}

/* ── Left brand panel ── */
.auth-brand-panel {
  flex: 0 0 46%;
  background: linear-gradient(150deg, #1c1c1e 0%, #2d2d30 50%, #3a3a3d 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 60px;
  position: relative;
  overflow: hidden;
}

.auth-brand-panel::before {
  content: '';
  position: absolute;
  width: 480px;
  height: 480px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  top: -180px;
  right: -160px;
  pointer-events: none;
}

.auth-brand-panel::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(0,0,0,0.08);
  bottom: -120px;
  left: -80px;
  pointer-events: none;
}

.brand-inner {
  position: relative;
  z-index: 1;
  color: #fff;
  max-width: 360px;
}

.brand-logo-row {
  display: flex;
  align-items: baseline;
  gap: 3px;
  margin-bottom: 56px;
}

.brand-wordmark {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -1px;
  line-height: 1;
}

.brand-dot { color: rgba(255,255,255,0.65); }

.brand-submark {
  font-size: 11px;
  font-weight: 500;
  color: rgba(255,255,255,0.55);
  letter-spacing: 0.3px;
}

.brand-headline {
  font-size: 36px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -1px;
  margin-bottom: 16px;
}

.brand-sub {
  font-size: 15px;
  line-height: 1.6;
  color: rgba(255,255,255,0.65);
}

.brand-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.brand-features li {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255,255,255,0.9);
}

.feature-icon {
  width: 28px;
  height: 28px;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 12px;
  height: 12px;
  color: #fff;
}

/* ── Right form panel ── */
.auth-form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  padding: 48px 32px;
}

.auth-form-inner {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(10,11,13,0.09), 0 1px 6px rgba(10,11,13,0.06);
}

.auth-form-header {
  margin-bottom: 36px;
}

h1 {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.8px;
  color: var(--text);
  margin-bottom: 8px;
  line-height: 1.2;
}

.auth-subtitle {
  color: var(--text-muted);
  font-size: 14.5px;
  line-height: 1.5;
}

.field-hint {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 7px;
  line-height: 1.5;
}

.submit-btn {
  width: 100%;
  padding: 13px;
  font-size: 14.5px;
  margin-top: 8px;
  border-radius: 11px;
  letter-spacing: -0.1px;
}

.btn-loader {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}

@keyframes spin { to { transform: rotate(360deg); } }

.auth-footer {
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
}

.auth-link {
  text-align: center;
  font-size: 13.5px;
  color: var(--text-muted);
}

.auth-link a {
  color: var(--primary);
  font-weight: 600;
}

.divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  color: var(--text-light);
  font-size: 12.5px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.btn-google {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 11px 16px;
  border: 1.5px solid var(--border);
  border-radius: 11px;
  background: var(--surface);
  color: var(--text);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.12s, border-color 0.12s, box-shadow 0.12s;
  cursor: pointer;
}

.btn-google:hover {
  background: var(--bg);
  border-color: var(--border-strong);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

@media (max-width: 768px) {
  .auth-brand-panel { display: none; }
  .auth-form-panel { padding: 24px 16px; }
}
</style>
