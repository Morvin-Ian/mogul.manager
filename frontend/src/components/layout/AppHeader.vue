<template>
  <header class="app-header">
    <div class="header-left">
      <h1>{{ pageTitle }}</h1>
    </div>
    <div class="header-right">
      <div class="user-pill">
        <div class="user-avatar" :title="auth.user?.username">{{ initials }}</div>
        <span class="user-name">{{ auth.user?.username }}</span>
      </div>
      <button class="btn btn-sm sign-out-btn" @click="handleLogout">
        <svg viewBox="0 0 16 16" fill="none" width="14" height="14">
          <path d="M11 3.5L14 7m0 0l-3 3.5M14 7H5m3-4H4a1 1 0 00-1 1v8a1 1 0 001 1h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Sign out
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const pageTitle = computed(() => {
  const name = route.name
  if (name === 'Dashboard') return 'Workspaces'
  if (name === 'WorkspaceDetail') return 'Workspace'
  if (name === 'ProjectDetail') return 'Project'
  if (name === 'TaskDetail') return 'Task'
  if (name === 'Chat') return 'AI Chat'
  return 'Mogul Manager'
})

const initials = computed(() =>
  (auth.user?.username ?? '').slice(0, 2).toUpperCase()
)

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  height: 56px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

h1 {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--text);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 4px 12px 4px 4px;
  border-radius: var(--radius-full);
  background: var(--bg);
  border: 1.5px solid var(--border);
  transition: border-color 0.15s;
  cursor: default;
}

.user-pill:hover {
  border-color: var(--border-strong);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.1px;
}

.sign-out-btn {
  color: var(--text-muted);
  border-color: var(--border);
  background: transparent;
  font-size: 12.5px;
  gap: 5px;
}

.sign-out-btn:hover:not(:disabled) {
  background: var(--danger-bg);
  color: var(--danger);
  border-color: var(--danger-border);
}
</style>
