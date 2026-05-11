<template>
  <div class="dashboard-layout">
    <AppSidebar />
    <div class="dashboard-main">
      <AppHeader />
      <main class="dashboard-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppHeader from '../components/layout/AppHeader.vue'

const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  if (!auth.user) {
    try {
      await auth.fetchUser()
    } catch {
      auth.logout()
      router.push('/login')
    }
  }
})
</script>
