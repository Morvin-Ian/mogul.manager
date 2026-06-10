<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-body">
      <AppSidebar />
      <main class="app-content">
        <router-view v-slot="{ Component }">
          <Transition name="route-fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </main>
    </div>
    <ConfirmDialog />
    <AiFloatingButton />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppHeader from '../components/layout/AppHeader.vue'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'
import AiFloatingButton from '../components/common/AiFloatingButton.vue'

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

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--layout-bg);
  background-attachment: fixed;
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  background: transparent;
  min-width: 0;
}
</style>
