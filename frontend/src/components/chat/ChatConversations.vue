<template>
  <aside class="chat-sidebar">
    <div class="chat-sidebar-header">
      <h2>Conversations</h2>
      <div class="sidebar-header-actions">
        <button
          v-if="conversations.length > 0"
          class="btn btn-sm btn-ghost icon-btn"
          @click="$emit('clear')"
          :disabled="streaming"
          title="Clear all conversations"
        >
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M2 3.5h10M5.5 3.5V2.5a1 1 0 011-1h1a1 1 0 011 1v1M5.5 6v4M8.5 6v4M3 3.5l.7 7a1 1 0 001 .9h4.6a1 1 0 001-.9l.7-7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="btn btn-sm btn-primary new-chat-btn" @click="$emit('new')" :disabled="streaming">
          <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          New
        </button>
      </div>
    </div>

    <div v-if="loading" class="sk-convs">
      <div v-for="n in 5" :key="n" class="sk-conv-item">
        <div class="sk-line sk-conv-title"></div>
        <div class="sk-line sk-conv-date"></div>
      </div>
    </div>

    <div v-else class="chat-conversations">
      <div v-if="conversations.length === 0" class="conv-empty">
        No conversations yet
      </div>
      <div
        v-for="conv in conversations"
        :key="conv.id"
        class="chat-conv-item"
        :class="{ active: currentId === conv.id }"
        @click="$emit('select', conv.id)"
      >
        <div class="conv-info">
          <div class="conv-title">{{ cleanTitle(conv.title) }}</div>
          <div class="conv-date">{{ formatDate(conv.updated_at) }}</div>
        </div>
        <button
          class="conv-delete-btn"
          @click.stop="$emit('delete', conv.id)"
          title="Delete conversation"
        >
          <svg viewBox="0 0 12 12" fill="none" width="12" height="12">
            <path d="M1.5 3h9M4.5 3V2a.5.5 0 01.5-.5h1a.5.5 0 01.5.5v1M3 3l.5 6.5a.5.5 0 00.5.5h4a.5.5 0 00.5-.5L9 3" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { Conversation } from '../../types'

defineProps<{
  conversations: Conversation[]
  loading: boolean
  streaming: boolean
  currentId: number | null
}>()

defineEmits<{
  select: [id: number]
  new: []
  delete: [id: number]
  clear: []
}>()

function cleanTitle(title: string | null): string {
  if (!title) return 'New conversation'
  const cleaned = title
    .replace(/[\u{1F000}-\u{1FFFF}]/gu, '')
    .replace(/[\u{2600}-\u{27BF}]/gu, '')
    .replace(/[︀-﻿]/g, '')
    .replace(/️/g, '')
    .trim()
  return cleaned || 'New conversation'
}

function formatDate(d: string) {
  const date = new Date(d)
  const diff = Date.now() - date.getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.chat-sidebar {
  width: 256px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  background: var(--surface);
}

.chat-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  gap: 8px;
}

.chat-sidebar-header h2 {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
  flex: 1;
}

.sidebar-header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.icon-btn {
  padding: 5px 7px;
  color: var(--text-muted);
}

.new-chat-btn { gap: 5px; }

.chat-conversations {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conv-empty {
  font-size: 13px;
  color: var(--text-light);
  text-align: center;
  padding: 32px 16px;
}

.chat-conv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.12s;
  margin-bottom: 2px;
  position: relative;
}

.chat-conv-item:hover { background: var(--bg); }
.chat-conv-item.active { background: #1c1c1e; }

.conv-info { flex: 1; min-width: 0; }

.conv-title {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
  letter-spacing: -0.1px;
}

.chat-conv-item.active .conv-title { color: #fff; font-weight: 600; }
.conv-date { font-size: 11px; color: var(--text-light); margin-top: 2px; }
.chat-conv-item.active .conv-date { color: rgba(255, 255, 255, 0.5); }

.conv-delete-btn {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  background: none;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-light);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.1s, background 0.1s, color 0.1s;
  padding: 0;
}

.chat-conv-item:hover .conv-delete-btn { opacity: 1; }
.conv-delete-btn:hover { background: var(--danger-bg); color: var(--danger); }

@keyframes shimmer {
  0%   { background-position: -300px 0; }
  100% { background-position:  300px 0; }
}

.sk-convs {
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sk-conv-item {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sk-line {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 300px 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: 4px;
}

.sk-conv-title { height: 11px; width: 75%; }
.sk-conv-date  { height: 9px;  width: 40%; }
</style>
