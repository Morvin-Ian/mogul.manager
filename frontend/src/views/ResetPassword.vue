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
        <h2 class="brand-headline">Choose a new<br />password</h2>
        <p class="brand-sub">Pick something strong that you don't use elsewhere.</p>
      </div>
    </div>

    <div class="auth-form-panel">
      <div class="auth-form-inner">

        <div v-if="!tokenPresent" class="invalid-state">
          <h1>Invalid link</h1>
          <p class="auth-subtitle">This reset link is missing or malformed. Please request a new one.</p>
          <router-link to="/forgot-password" class="btn btn-primary submit-btn" style="margin-top: 24px; display: flex;">
            Request new link
          </router-link>
        </div>

        <div v-else-if="!done">
          <div class="auth-form-header">
            <h1>Set new password</h1>
            <p class="auth-subtitle">Must be at least 8 characters.</p>
          </div>
          <form @submit.prevent="handleSubmit" novalidate>
            <div class="form-group">
              <label for="password">New password</label>
              <input
                id="password"
                v-model="password"
                type="password"
                required
                placeholder="At least 8 characters"
                autocomplete="new-password"
                minlength="8"
              />
            </div>
            <div class="form-group">
              <label for="confirm">Confirm password</label>
              <input
                id="confirm"
                v-model="confirm"
                type="password"
                required
                placeholder="Repeat your new password"
                autocomplete="new-password"
              />
            </div>
            <p v-if="error" class="form-error">{{ error }}</p>
            <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
              <span v-if="loading" class="btn-loader"></span>
              {{ loading ? 'Saving…' : 'Reset password' }}
            </button>
          </form>
        </div>

        <div v-else class="success-state">
          <div class="success-icon">
            <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1>Password updated</h1>
          <p class="auth-subtitle">Your password has been changed. Sign in with your new credentials.</p>
          <router-link to="/login" class="btn btn-primary submit-btn" style="margin-top: 24px; display: flex;">
            Sign in
          </router-link>
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
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()

const resetToken = computed(() => route.query.token as string | undefined)
const tokenPresent = computed(() => !!resetToken.value)

const password = ref('')
const confirm = ref('')
const error = ref<string | null>(null)
const loading = ref(false)
const done = ref(false)

async function handleSubmit() {
  error.value = null
  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }
  if (password.value !== confirm.value) {
    error.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await auth.resetPassword(resetToken.value!, password.value)
    done.value = true
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
  background: linear-gradient(150deg, #0052FF 0%, #003CBF 50%, #0028A0 100%);
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
}

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

.submit-btn {
  width: 100%;
  padding: 13px;
  font-size: 14.5px;
  margin-top: 8px;
  border-radius: 11px;
  letter-spacing: -0.1px;
  text-align: center;
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

.success-state, .invalid-state {
  text-align: center;
  padding: 16px 0;
}

.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: #ECFDF5;
  border: 1px solid #A7F3D0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  color: #047857;
}

.success-state h1, .invalid-state h1 { text-align: center; }
.success-state .auth-subtitle, .invalid-state .auth-subtitle { text-align: center; margin-top: 8px; }

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
