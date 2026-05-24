<template>
  <div class="auth-page">
    <div class="auth-brand-panel">
      <div class="brand-inner">
        <div class="brand-logo-row">
          <div class="brand-mark">
            <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
              <path d="M3 16V7l4 5 3-7 3 7 4-5v9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="brand-name">Mogul Manager</span>
        </div>
        <h2 class="brand-headline">Your workspace,<br />supercharged by AI</h2>
        <p class="brand-sub">Join teams who track projects, manage tasks, and get insights from an intelligent assistant.</p>
        <ul class="brand-features">
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            Unlimited workspaces &amp; projects
          </li>
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            AI-assisted task prioritization
          </li>
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            Free to get started
          </li>
        </ul>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

async function handleRegister() {
  error.value = null
  loading.value = true
  try {
    await auth.register({ username: username.value, email: email.value, password: password.value })
    router.push('/login')
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
  background: linear-gradient(150deg, #0052FF 0%, #003CBF 50%, #0028A0 100%);
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
  align-items: center;
  gap: 12px;
  margin-bottom: 56px;
}

.brand-mark {
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.15);
  border: 1.5px solid rgba(255,255,255,0.25);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: rgba(255,255,255,0.95);
  letter-spacing: -0.3px;
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
  line-height: 1.75;
  color: rgba(255,255,255,0.72);
  margin-bottom: 44px;
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
  width: 13px;
  height: 13px;
  color: #fff;
}

/* ── Right form panel ── */
.auth-form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface);
  padding: 48px 40px;
}

.auth-form-inner {
  width: 100%;
  max-width: 400px;
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

@media (max-width: 768px) {
  .auth-brand-panel { display: none; }
  .auth-form-panel { padding: 40px 24px; }
}
</style>
