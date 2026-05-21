<template>
  <div class="auth-page">
    <div class="auth-brand-panel">
      <div class="brand-inner">
        <div class="brand-logo-row">
          <span class="brand-name">Mogul Manager</span>
        </div>
        <h2 class="brand-headline">Your workspace,<br />supercharged by AI</h2>
        <p class="brand-sub">Join teams who track projects, manage tasks, and get insights from an intelligent assistant.</p>
        <ul class="brand-features">
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            Unlimited workspaces &amp; projects
          </li>
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            AI-assisted task prioritization
          </li>
          <li>
            <span class="feature-icon">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </span>
            Free to get started
          </li>
        </ul>
      </div>
    </div>

    <div class="auth-form-panel">
      <div class="auth-form-inner">
        <div class="auth-form-header">
          <h1>Create account</h1>
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
            <p class="field-hint">Use at least 8 characters with a mix of letters and numbers.</p>
          </div>
          <p v-if="error" class="form-error">{{ error }}</p>
          <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
            <span v-if="loading" class="btn-loader"></span>
            {{ loading ? 'Creating account…' : 'Create account' }}
          </button>
        </form>
        <p class="auth-link">
          Already have an account?
          <router-link to="/login">Sign in</router-link>
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

.field-hint {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 5px;
}

.submit-btn {
  width: 100%;
  padding: 13px;
  font-size: 14.5px;
  margin-top: 4px;
  border-radius: var(--radius-sm);
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
