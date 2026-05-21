<template>
  <header class="app-header">
    <div class="header-left">
      <h1>{{ pageTitle }}</h1>
    </div>
    <div class="header-right">
      <div class="user-avatar" :title="auth.user?.username">{{ initials }}</div>
      <span class="user-info">{{ auth.user?.username }}</span>
      <button class="btn btn-ghost btn-sm" @click="handleLogout">Sign out</button>
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
  return 'mogul'
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

.app-header h1 {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.2px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--primary-light);
  border: 1.5px solid var(--primary-border);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}

.user-info {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
}
</style>
