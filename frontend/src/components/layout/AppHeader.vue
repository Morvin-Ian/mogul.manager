<template>
  <header class="app-header">
    <!-- Logo -->
    <div class="header-logo">
      <span class="logo-wordmark">mogul<span class="logo-dot">.</span></span>
      <span class="logo-sub">manager</span>
    </div>

    <!-- Center nav -->
    <nav class="nav-pills">
      <router-link
        v-for="item in navItems"
        :key="item.label"
        :to="item.to"
        class="nav-pill"
        :class="{ active: isActive(item) }"
      >
        <font-awesome-icon :icon="item.icon" class="nav-pill-icon" />
        {{ item.label }}
      </router-link>
    </nav>

    <!-- Right: actions + user -->
    <div class="header-right">
      <button
        class="hdr-icon"
        :class="{ 'hdr-icon--badge': notifStore.hasUnread }"
        title="Notifications"
        :aria-label="notifStore.hasUnread ? 'Notifications (unread)' : 'Notifications'"
        :aria-expanded="showNotifs"
        @click.stop="toggleNotifs"
      >
        <font-awesome-icon :icon="['far', 'bell']" style="font-size: 15px;" />
      </button>
      <NotificationDropdown :open="showNotifs" @close="showNotifs = false" />

      <router-link to="/settings" class="user-section" :title="auth.user?.username">
        <div class="user-avatar">
          <img v-if="auth.user?.profile_path" :src="auth.user.profile_path" class="avatar-img" :alt="auth.user?.username" />
          <font-awesome-icon v-else :icon="['fas', 'user']" style="font-size: 14px;" />
        </div>
        <div class="user-text">
          <span class="user-name">{{ auth.user?.username ?? 'User' }}</span>
          <span class="user-role">Member</span>
        </div>
      </router-link>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useNotificationStore } from '../../stores/notifications'
import NotificationDropdown from '../common/NotificationDropdown.vue'

const auth = useAuthStore()
const route = useRoute()
const notifStore = useNotificationStore()

const showNotifs = ref(false)

function toggleNotifs() {
  showNotifs.value = !showNotifs.value
  if (showNotifs.value) {
    notifStore.fetchNotifications()
  }
}

const navItems = computed(() => [
  { label: 'Home',       to: '/',           icon: ['fas', 'house'],              activeOn: ['/']           },
  { label: 'Workspaces', to: '/workspaces', icon: ['fas', 'layer-group'],        activeOn: ['/workspaces'] },
  { label: 'Settings',   to: '/settings',   icon: ['fas', 'gear'],               activeOn: ['/settings']   },
])

function isActive(item: { to: string; activeOn: string[] }) {
  if (item.to === '/') return route.path === '/'
  return item.activeOn.some(p => route.path.startsWith(p))
}

onMounted(() => {
  notifStore.connectSSE()
  notifStore.fetchUnreadCount()
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  height: 64px;
  background: rgba(255, 255, 255, 0.50);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: none;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 20;
  gap: 24px;
}

/* ── Logo ───────────────────────── */
.header-logo {
  display: flex;
  align-items: baseline;
  gap: 3px;
  flex-shrink: 0;
}

.logo-wordmark {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -1px;
  line-height: 1;
}

.logo-dot { color: var(--primary); }

.logo-sub {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  letter-spacing: 0.3px;
}

/* ── Nav pills ──────────────────── */
.nav-pills {
  display: flex;
  align-items: center;
  gap: 4px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.nav-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 20px;
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
  text-decoration: none;
}

.nav-pill-icon {
  font-size: 13px;
  opacity: 0.75;
}

.nav-pill:hover {
  background: rgba(0,0,0,0.05);
  color: var(--text);
  text-decoration: none;
}

.nav-pill.active {
  background: #1C1C1E;
  color: #ffffff;
  font-weight: 600;
}

.nav-pill.active .nav-pill-icon {
  opacity: 1;
}

.nav-pill-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #EF4444;
  flex-shrink: 0;
}

/* ── Right ──────────────────────── */
.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.hdr-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: 1.5px solid rgba(200, 200, 206, 0.8);
  background: rgba(255,255,255,0.75);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.12s, color 0.12s, border-color 0.12s, box-shadow 0.12s;
  position: relative;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(10,11,13,0.07);
}

.hdr-icon:hover {
  background: var(--bg);
  color: var(--text);
  border-color: var(--border-strong);
}

.hdr-icon--badge::after {
  content: '';
  position: absolute;
  top: 6px;
  right: 7px;
  width: 7px;
  height: 7px;
  background: #EF4444;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--bg);
}

/* ── User section ───────────────── */
.user-section {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px 4px 4px;
  border-radius: var(--radius-full);
  border: 1.5px solid rgba(200, 200, 206, 0.8);
  background: rgba(255,255,255,0.75);
  text-decoration: none;
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  margin-left: 4px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(10,11,13,0.07);
}

.user-section:hover {
  border-color: var(--border-strong);
  background: var(--bg);
  text-decoration: none;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.user-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.2;
  max-width: 110px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.2;
}

@media (max-width: 900px) {
  .user-text { display: none; }
  .user-section { padding: 4px; }
  .logo-sub { display: none; }
}

/* ── Dark mode header ── */
:global([data-theme="dark"]) .app-header {
  background: rgba(21, 32, 43, 0.88);
  border-bottom: 1px solid rgba(56, 68, 77, 0.5);
}

:global([data-theme="dark"]) .hdr-icon {
  background: rgba(255, 255, 255, 0.06);
  border-color: #38444D;
  color: #8B98A5;
  box-shadow: none;
}
:global([data-theme="dark"]) .hdr-icon:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: #536471;
  color: #F7F9F9;
}

:global([data-theme="dark"]) .user-section {
  background: rgba(255, 255, 255, 0.05);
  border-color: #38444D;
  box-shadow: none;
}
:global([data-theme="dark"]) .user-section:hover {
  background: rgba(255, 255, 255, 0.10);
  border-color: #536471;
}

:global([data-theme="dark"]) .user-avatar {
  background: #253341;
  color: #8B98A5;
}

:global([data-theme="dark"]) .nav-pill:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #F7F9F9;
}
:global([data-theme="dark"]) .nav-pill.active {
  background: #F7F9F9;
  color: #15202B;
}
</style>
