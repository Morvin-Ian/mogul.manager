<template>
  <div class="auth-page">
    <div class="auth-brand-panel">
      <div class="brand-inner">
        <div class="brand-logo-row">
          <span class="brand-wordmark">mogul<span class="brand-dot">.</span></span>
          <span class="brand-submark">manager</span>
        </div>
        <h2 class="brand-headline">Reset your<br />password</h2>
        <p class="brand-sub">Enter your email and we'll send you a link to get back into your account.</p>
      </div>
    </div>

    <div class="auth-form-panel">
      <div class="auth-form-inner">
        <div v-if="!sent">
          <div class="auth-form-header">
            <h1>Forgot password?</h1>
            <p class="auth-subtitle">We'll email you a reset link.</p>
          </div>
          <form @submit.prevent="handleSubmit" novalidate>
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
            <p v-if="error" class="form-error">{{ error }}</p>
            <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
              <span v-if="loading" class="btn-loader"></span>
              {{ loading ? 'Sending…' : 'Send reset link' }}
            </button>
          </form>
        </div>

        <div v-else class="success-state">
          <div class="success-icon">
            <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
              <path d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0l-8 5-8-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1>Check your email</h1>
          <p class="auth-subtitle">We sent a reset link to <strong>{{ email }}</strong>. It expires in 60 minutes.</p>
          <button class="btn btn-primary submit-btn" style="margin-top: 24px" @click="sent = false">
            Try a different email
          </button>
        </div>

        <div class="auth-footer">
          <p class="auth-link">
            <router-link to="/login">← Back to sign in</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const email = ref('')
const error = ref<string | null>(null)
const loading = ref(false)
const sent = ref(false)

async function handleSubmit() {
  error.value = null
  loading.value = true
  try {
    await auth.forgotPassword(email.value)
    sent.value = true
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
  flex: 0 0 46%;
  background: linear-gradient(150deg, #1c1c1e 0%, #2d2d30 50%, #3a3a3d 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
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
  line-height: 1.75;
  color: rgba(255,255,255,0.72);
}

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

.success-state {
  text-align: center;
  padding: 16px 0;
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: var(--primary-light);
  border: 1px solid var(--primary-border);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: var(--primary);
}

.success-state h1 { text-align: center; }
.success-state .auth-subtitle { text-align: center; margin-top: 8px; }

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
  .auth-form-panel { padding: 24px 16px; }
}
</style>
