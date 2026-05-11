<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2>MDA</h2>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" exact-active-class="active">
        <span>Workspaces</span>
      </router-link>
      <div v-if="workspaceStore.workspaces.length" class="nav-section">
        <p class="nav-section-title">My Workspaces</p>
        <router-link
          v-for="ws in workspaceStore.workspaces"
          :key="ws.id"
          :to="`/workspaces/${ws.id}`"
          class="nav-item nav-item-sub"
          active-class="active"
        >
          <span>{{ ws.title }}</span>
        </router-link>
      </div>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useWorkspaceStore } from '../../stores/workspaces'

const workspaceStore = useWorkspaceStore()

onMounted(() => {
  workspaceStore.fetchAll()
})
</script>
