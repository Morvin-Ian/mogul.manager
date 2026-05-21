<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <div class="auth-logo">M</div>
        <span class="auth-app-name">mogul</span>
      </div>
      <h1>Welcome back</h1>
      <p class="auth-subtitle">Sign in to continue to your workspace</p>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" required placeholder="you@example.com" />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" v-model="password" type="password" required placeholder="••••••••" />
        </div>
        <p v-if="error" class="form-error">{{ error }}</p>
        <button type="submit" class="btn btn-primary submit-btn" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
      <p class="auth-link">No account? <router-link to="/register">Create one free</router-link></p>
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
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #09090b;
  background-image:
    radial-gradient(ellipse at 20% 60%, rgba(5,150,105,0.18) 0%, transparent 55%),
    radial-gradient(ellipse at 85% 15%, rgba(14,165,233,0.09) 0%, transparent 50%);
}

.auth-card {
  background: var(--surface);
  padding: 44px;
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 400px;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.06), var(--shadow-lg);
}

.auth-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 32px;
}

.auth-logo {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
  color: #fff;
  letter-spacing: -1px;
}

.auth-app-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.6px;
}

h1 {
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 6px;
  letter-spacing: -0.4px;
}

.auth-subtitle {
  text-align: center;
  color: var(--text-muted);
  font-size: 13.5px;
  margin-bottom: 28px;
}

.submit-btn {
  width: 100%;
  margin-top: 6px;
}

.auth-link {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: var(--text-muted);
}
</style>
