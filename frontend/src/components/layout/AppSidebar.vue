<template>
  <aside class="sidebar">
    <nav class="sidebar-nav">
      <router-link to="/" exact-active-class="active" class="nav-item" title="Home">
        <span class="icon-wrap">
          <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
            <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
          </svg>
        </span>
        <span class="nav-label">Home</span>
      </router-link>

      <router-link to="/chat" active-class="active" class="nav-item" title="AI Chat">
        <span class="icon-wrap">
          <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
            <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd"/>
          </svg>
        </span>
        <span class="nav-label">Chat</span>
      </router-link>

      <router-link to="/documents" active-class="active" class="nav-item" title="Documents">
        <span class="icon-wrap">
          <svg viewBox="0 0 20 20" fill="none" width="20" height="20">
            <path d="M13 2H5a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7l-4-5z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
            <path d="M13 2v5h5M7 9h6M7 12h6M7 15h4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
        </span>
        <span class="nav-label">Docs</span>
      </router-link>

      <router-link to="/settings" active-class="active" class="nav-item" title="Settings">
        <span class="icon-wrap">
          <svg viewBox="0 0 20 20" fill="currentColor" width="20" height="20">
            <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
          </svg>
        </span>
        <span class="nav-label">Settings</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <button class="nav-item logout-btn" @click="handleLogout" title="Sign out">
        <span class="icon-wrap">
          <svg viewBox="0 0 20 20" fill="none" width="20" height="20">
            <path d="M13 3.5L17 7m0 0l-4 4M17 7H7m4-4H5a1 1 0 00-1 1v10a1 1 0 001 1h6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
        <span class="nav-label">Sign Out</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 88px;
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-right: 1px solid rgba(180, 180, 185, 0.4);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  padding: 16px 0 12px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 0 10px;
  flex: 1;
}

.sidebar-footer {
  padding: 10px 10px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 10px 8px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  width: 100%;
  transition: color 0.14s;
  cursor: pointer;
  background: none;
  border: none;
}

.nav-item:hover { color: var(--text); text-decoration: none; }
.nav-item:hover .icon-wrap { box-shadow: 0 2px 8px rgba(10,11,13,0.12); }

.nav-item.active { color: var(--text); }
.nav-item.active .icon-wrap {
  background: #1C1C1E;
  color: #ffffff;
}

.logout-btn:hover .icon-wrap {
  background: #FEE2E2;
  color: #EF4444;
}

.icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.75);
  box-shadow: 0 2px 8px rgba(10,11,13,0.09), 0 1px 3px rgba(10,11,13,0.05);
  transition: background 0.14s, color 0.14s, box-shadow 0.14s;
  color: inherit;
  flex-shrink: 0;
}

.nav-label {
  font-size: 12px;
  font-weight: 400;
  letter-spacing: 0.1px;
  line-height: 1;
  text-align: center;
  color: inherit;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 68px;
}

@media (max-width: 640px) {
  .sidebar { width: 68px; padding: 12px 0 8px; }
  .sidebar-nav { padding: 0 6px; }
  .sidebar-footer { padding: 8px 6px 0; }
  .icon-wrap { width: 36px; height: 36px; border-radius: 10px; }
  .nav-label { font-size: 9.5px; }
}
</style>
