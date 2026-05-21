<template>
  <div class="auth-page">
    <div class="auth-brand-panel">
      <div class="brand-inner">
        <div class="brand-logo-row">
          <span class="brand-name">Mogul Manager</span>
        </div>
        <h2 class="brand-headline">Work smarter with<br />AI-driven projects</h2>
        <p class="brand-sub">Manage workspaces, track tasks, and collaborate with your AI assistant — all in one place.</p>
        <ul class="brand-features">
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            Kanban boards &amp; task tracking
          </li>
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            AI-powered project intelligence
          </li>
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            Real-time AI chat assistant
          </li>
        </ul>
      </div>
    </div>

    <div class="auth-form-panel">
      <div class="auth-form-inner">
        <div class="auth-form-header">
          <h1>Sign in</h1>
          <p class="auth-subtitle">Welcome back to Mogul Manager</p>
        </div>
        <form @submit.prevent="handleLogin" novalidate>
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
              placeholder="Enter your password"
              autocomplete="current-password"
            />
          </div>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
            <span v-if="loading" class="btn-loader"></span>
            {{ loading ? 'Signing in…' : 'Sign in' }}
          </button>
        </form>
        <p class="auth-link">
          New to Mogul Manager?
          <router-link to="/register">Create a free account</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

async function handleLogin() {
  error.value = null
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
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

/* Left brand panel */
.auth-brand-panel {
  flex: 0 0 44%;
  background: linear-gradient(145deg, #0052FF 0%, #003CBF 55%, #0028A0 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 56px;
  position: relative;
  overflow: hidden;
}

.auth-brand-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 60% 50% at 20% 20%, rgba(255,255,255,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 50% 60% at 80% 80%, rgba(0,0,0,0.12) 0%, transparent 70%);
}

.brand-inner {
  position: relative;
  z-index: 1;
  color: #fff;
  max-width: 380px;
}

.brand-logo-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 52px;
}

.brand-name {
  font-size: 22px;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.4px;
}

.brand-headline {
  font-size: 30px;
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: -0.8px;
  margin-bottom: 16px;
}

.brand-sub {
  font-size: 15px;
  line-height: 1.65;
  color: rgba(255,255,255,0.75);
  margin-bottom: 40px;
}

.brand-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.brand-features li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255,255,255,0.9);
}

.feature-icon {
  width: 24px;
  height: 24px;
  background: rgba(255,255,255,0.15);
  border-radius: 50%;
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

/* Right form panel */
.auth-form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  padding: 40px 32px;
}

.auth-form-inner {
  width: 100%;
  max-width: 380px;
}

.auth-form-header {
  margin-bottom: 32px;
}

h1 {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.6px;
  color: var(--text);
  margin-bottom: 6px;
}

.auth-subtitle {
  color: var(--text-muted);
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 13px;
  font-size: 14.5px;
  margin-top: 4px;
  border-radius: var(--radius-sm);
  position: relative;
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

.auth-link {
  margin-top: 24px;
  text-align: center;
  font-size: 13.5px;
  color: var(--text-muted);
}

.auth-link a {
  color: var(--primary);
  font-weight: 600;
}

@media (max-width: 768px) {
  .auth-brand-panel { display: none; }
  .auth-form-panel { padding: 40px 24px; }
}
</style>
