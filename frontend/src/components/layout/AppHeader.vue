<template>
  <header class="app-header">
    <div class="header-left">
      <h1>{{ pageTitle }}</h1>
    </div>
    <div class="header-right">
      <span class="user-info">{{ auth.user?.username }}</span>
      <button class="btn btn-sm" @click="handleLogout">Logout</button>
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
  return 'Dashboard'
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
