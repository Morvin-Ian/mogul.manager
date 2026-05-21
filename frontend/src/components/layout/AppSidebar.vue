<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-logo">M</div>
      <span class="brand-name">mogul</span>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" exact-active-class="active">
        <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
          <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM13 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2h-2z" />
        </svg>
        <span>Workspaces</span>
      </router-link>
      <router-link to="/chat" class="nav-item" active-class="active">
        <svg class="nav-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
        </svg>
        <span>AI Chat</span>
      </router-link>
      <div v-if="workspaceStore.workspaces.length" class="nav-section">
        <p class="nav-section-title">Workspaces</p>
        <router-link
          v-for="ws in workspaceStore.workspaces"
          :key="ws.id"
          :to="`/workspaces/${ws.id}`"
          class="nav-item nav-item-sub"
          active-class="active"
        >
          <svg class="nav-icon nav-icon-sm" viewBox="0 0 20 20" fill="currentColor">
            <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
          </svg>
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
onMounted(() => workspaceStore.fetchAll())
</script>

<style scoped>
.sidebar {
  width: 220px;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-right: 1px solid var(--sidebar-border);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 14px;
  border-bottom: 1px solid var(--sidebar-border);
}

.brand-logo {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 800;
  color: #fff;
  flex-shrink: 0;
  letter-spacing: -1px;
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: #fafafa;
  letter-spacing: -0.4px;
}

.sidebar-nav {
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 1px;
  flex: 1;
}

.nav-section { margin-top: 18px; }

.nav-section-title {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #52525b;
  padding: 4px 12px;
  margin-bottom: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  transition: all 0.12s ease;
  border-left: 2px solid transparent;
}

.nav-item:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text-hover);
  text-decoration: none;
}

.nav-item.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-text-active);
  border-left-color: var(--sidebar-active-bar);
  font-weight: 600;
}

.nav-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  opacity: 0.55;
  transition: opacity 0.12s;
}

.nav-item:hover .nav-icon,
.nav-item.active .nav-icon { opacity: 1; }

.nav-icon-sm { width: 14px; height: 14px; }

.nav-item-sub {
  padding-left: 12px;
  font-size: 13px;
  color: #52525b;
}
.nav-item-sub:hover { color: var(--sidebar-text-hover); }
.nav-item-sub.active { color: var(--sidebar-text-active); }

@media (max-width: 640px) {
  .sidebar { width: 52px; }
  .brand-name, .nav-item span, .nav-section { display: none; }
  .nav-item { justify-content: center; padding: 10px; border-left: none; }
  .sidebar-brand { justify-content: center; padding: 16px 0; }
  .nav-icon { width: 18px; height: 18px; opacity: 1; }
}
</style>
