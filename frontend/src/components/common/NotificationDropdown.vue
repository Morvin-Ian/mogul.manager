<template>
  <Teleport to="body">
    <Transition name="nd-pop">
    <div v-if="open" class="nd-backdrop" @click="close" @keydown.esc="close">
      <div class="nd-dropdown" @click.stop>
        <div class="nd-header">
          <span class="nd-title">Notifications</span>
          <button v-if="store.unreadCount" class="nd-mark-btn" @click="store.markAllAsRead()">Mark all as read</button>
        </div>

        <div v-if="store.loading" class="nd-center"><div class="nd-spinner" /></div>

        <div v-else-if="store.notifications.length === 0" class="empty-state">
          <div class="empty-state-glyph">
            <font-awesome-icon :icon="['far', 'bell']" />
          </div>
          <div class="empty-state-title">You're all caught up</div>
          <div class="empty-state-hint">Mentions, assignments, and team activity will show up here.</div>
        </div>

        <div v-else class="nd-list">
          <div
            v-for="n in store.notifications"
            :key="n.id"
            class="nd-item"
            :class="{ 'nd-item--unread': !n.is_read }"
            @click="handleClick(n)"
          >
            <span class="nd-item-dot" :class="{ 'nd-item-dot--visible': !n.is_read }" />
            <div class="nd-item-body">
              <div class="nd-item-title">{{ n.title }}</div>
              <div v-if="n.message" class="nd-item-msg">{{ n.message }}</div>
              <div class="nd-item-time">{{ timeAgo(n.created_at) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '../../stores/notifications'
import { timeAgo } from '../../utils/time'
import type { Notification } from '../../types'

defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const store = useNotificationStore()

function close() {
  emit('close')
}

function handleClick(n: Notification) {
  if (!n.is_read) store.markAsRead(n.id)
  if (n.link) {
    close()
    window.location.href = n.link
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.nd-backdrop {
  position: fixed;
  inset: 0;
  z-index: var(--z-dropdown);
  display: flex;
  justify-content: flex-end;
  padding: 72px 32px 0 0;
}

.nd-dropdown {
  width: 380px;
  max-height: min(480px, 80vh);
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--border, #D8D9DE);
  border-radius: var(--radius-lg, 16px);
  box-shadow: var(--shadow-lg, 0 20px 60px rgba(10,11,13,0.14), 0 4px 16px rgba(10,11,13,0.08));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: nd-in 0.12s ease-out;
}

@keyframes nd-in {
  from { opacity: 0; transform: translateY(-6px) scale(0.97); }
}

.nd-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px 12px;
  border-bottom: 1px solid var(--border, #D8D9DE);
  flex-shrink: 0;
}

.nd-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text, #0A0B0D);
}

.nd-mark-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary, #0052FF);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm, 8px);
  transition: background 0.12s;
}

.nd-mark-btn:hover {
  background: var(--primary-light, rgba(0,82,255,0.08));
}

.nd-list {
  overflow-y: auto;
  flex: 1;
}

.nd-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 18px;
  cursor: pointer;
  transition: background 0.1s;
  border-bottom: 1px solid var(--border, #D8D9DE);
}

.nd-item:last-child {
  border-bottom: none;
}

.nd-item:hover {
  background: var(--bg, #F4F4F6);
}

.nd-item--unread {
  background: var(--primary-light, rgba(0,82,255,0.04));
}

.nd-item--unread:hover {
  background: var(--primary-light, rgba(0,82,255,0.08));
}

.nd-item-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary, #0052FF);
  flex-shrink: 0;
  margin-top: 6px;
  visibility: hidden;
}

.nd-item-dot--visible {
  visibility: visible;
}

.nd-item-body {
  flex: 1;
  min-width: 0;
}

.nd-item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text, #0A0B0D);
  line-height: 1.3;
  margin-bottom: 2px;
}

.nd-item-msg {
  font-size: 13px;
  color: var(--text-muted, #5B616E);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 4px;
}

.nd-item-time {
  font-size: 11px;
  color: var(--text-light, #8A919E);
}

.nd-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  gap: 12px;
}

.nd-empty {
  color: var(--text-muted, #5B616E);
  font-size: 14px;
}

.nd-empty-icon {
  font-size: 32px;
  opacity: 0.4;
}

.nd-spinner {
  width: 24px;
  height: 24px;
  border: 2.5px solid var(--border, #D8D9DE);
  border-top-color: var(--primary, #0052FF);
  border-radius: 50%;
  animation: nd-spin 0.6s linear infinite;
}

@keyframes nd-spin {
  to { transform: rotate(360deg); }
}

/* Dark mode overrides */
:global([data-theme="dark"]) .nd-dropdown {
  background: #1E2732;
  border-color: #38444D;
}

:global([data-theme="dark"]) .nd-item:hover {
  background: rgba(255,255,255,0.05);
}

:global([data-theme="dark"]) .nd-item--unread {
  background: rgba(91, 155, 255, 0.1);
}

:global([data-theme="dark"]) .nd-item--unread:hover {
  background: rgba(91, 155, 255, 0.15);
}

:global([data-theme="dark"]) .nd-mark-btn:hover {
  background: rgba(91, 155, 255, 0.15);
}

/* Transition */
.nd-pop-enter-active {
  animation: nd-in 0.12s ease-out;
}

.nd-pop-leave-active {
  animation: nd-in 0.1s ease-in reverse;
}
</style>
