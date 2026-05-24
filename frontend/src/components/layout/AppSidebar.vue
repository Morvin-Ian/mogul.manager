<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-icon">
        <svg viewBox="0 0 20 20" fill="none" width="14" height="14">
          <path d="M3 16V7l4 5 3-7 3 7 4-5v9" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <span class="brand-name">Mogul Manager</span>
    </div>

    <nav class="sidebar-nav">
      <div class="nav-group">
        <router-link to="/" class="nav-item" exact-active-class="active">
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM13 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2h-2z" />
            </svg>
          </span>
          <span class="nav-label">Workspaces</span>
        </router-link>
        <router-link to="/chat" class="nav-item" active-class="active">
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
            </svg>
          </span>
          <span class="nav-label">AI Chat</span>
        </router-link>
      </div>

      <div v-if="workspaceStore.workspaces.length" class="nav-group nav-group-workspaces">
        <p class="nav-section-title">My Workspaces</p>
        <router-link
          v-for="ws in workspaceStore.workspaces"
          :key="ws.id"
          :to="`/workspaces/${ws.id}`"
          class="nav-item nav-item-sub"
          active-class="active"
        >
          <span class="nav-icon">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
              </svg>
            </span>
          <span class="nav-label">{{ ws.title }}</span>
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
  width: 240px;
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
  padding: 18px 16px;
  border-bottom: 1px solid var(--sidebar-border);
}

.brand-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.sidebar-nav {
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 0;
  flex: 1;
  overflow-y: auto;
}

.nav-group {
  margin-bottom: 2px;
}

.nav-group-workspaces {
  margin-top: 18px;
  border-top: 1px solid var(--sidebar-border);
  padding-top: 14px;
}

.nav-section-title {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.9px;
  color: var(--text-light);
  padding: 0 12px 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  transition: background 0.12s ease, color 0.12s ease;
  margin-bottom: 2px;
  position: relative;
}

.nav-item:hover {
  background: var(--sidebar-hover);
  color: var(--sidebar-text-hover);
  text-decoration: none;
}

.nav-item.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-text-active);
  font-weight: 600;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background: var(--primary);
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity 0.12s;
}

.nav-icon svg {
  width: 16px;
  height: 16px;
}

.nav-item:hover .nav-icon { opacity: 0.75; }
.nav-item.active .nav-icon { opacity: 1; }

.nav-item-sub {
  padding-left: 10px;
  font-size: 13px;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 640px) {
  .sidebar { width: 56px; }
  .brand-name, .nav-label, .nav-group-workspaces { display: none; }
  .nav-item { justify-content: center; padding: 10px; }
  .sidebar-brand { justify-content: center; padding: 14px 0; }
  .nav-icon { opacity: 0.65; width: 20px; height: 20px; }
  .nav-icon svg { width: 18px; height: 18px; }
}
</style>
