<template>
  <aside class="conv-panel">
    <!-- Header -->
    <div class="panel-head">
      <span class="panel-title">Conversations</span>
      <div class="panel-head-actions">
        <button
          v-if="conversations.length > 0"
          class="head-btn"
          @click="$emit('clear')"
          :disabled="streaming"
          title="Clear all"
        >
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M2 3.5h10M5.5 3.5V2.5a1 1 0 011-1h1a1 1 0 011 1v1M3 3.5l.7 7a1 1 0 001 .9h4.6a1 1 0 001-.9l.7-7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="new-btn" @click="$emit('new')" :disabled="streaming" title="New conversation">
          <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          New
        </button>
      </div>
    </div>

    <!-- Search -->
    <div class="search-wrap">
      <svg class="search-icon" viewBox="0 0 14 14" fill="none" width="13" height="13">
        <circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.3"/>
        <path d="M10 10l2.5 2.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
      </svg>
      <input
        v-model="search"
        class="search-input"
        placeholder="Search conversations…"
        type="text"
      />
      <button v-if="search" class="search-clear" @click="search = ''">×</button>
    </div>

    <!-- Skeleton loading -->
    <div v-if="loading" class="conv-list">
      <div v-for="n in 6" :key="n" class="sk-item">
        <div class="sk-line sk-title"></div>
        <div class="sk-line sk-sub"></div>
      </div>
    </div>

    <!-- Conversation list -->
    <div v-else class="conv-list">
      <div v-if="conversations.length === 0" class="conv-empty">
        <svg viewBox="0 0 40 40" fill="none" width="32" height="32">
          <path d="M34 8H6a2 2 0 00-2 2v18a2 2 0 002 2h6l4 5 4-5h14a2 2 0 002-2V10a2 2 0 00-2-2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
          <path d="M13 18h14M13 23h8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p>No conversations yet</p>
      </div>

      <div v-else-if="filtered.length === 0" class="conv-empty">
        <p>No results for "{{ search }}"</p>
      </div>

      <div
        v-else
        v-for="conv in filtered"
        :key="conv.id"
        class="conv-item"
        :class="{ active: currentId === conv.id }"
        @click="$emit('select', conv.id)"
      >
        <div class="conv-body">
          <p class="conv-title">{{ cleanTitle(conv.title) }}</p>
          <p class="conv-sub">{{ formatDate(conv.updated_at) }}</p>
        </div>
        <button class="conv-del" @click.stop="$emit('delete', conv.id)" title="Delete">
          <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
            <path d="M1.5 3h9M4.5 3V2a.5.5 0 01.5-.5h1a.5.5 0 01.5.5v1M3 3l.5 6.5a.5.5 0 00.5.5h4a.5.5 0 00.5-.5L9 3" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Conversation } from '../../types'

const props = defineProps<{
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

const search = ref('')

const filtered = computed(() => {
  if (!search.value.trim()) return props.conversations
  const q = search.value.toLowerCase()
  return props.conversations.filter(c =>
    (c.title || 'New conversation').toLowerCase().includes(q)
  )
})

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
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.conv-panel {
  width: 256px;
  flex-shrink: 0;
  border-right: 1px solid var(--border);
  background: var(--surface);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Header ── */
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 14px 12px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  gap: 8px;
}
.panel-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
  flex: 1;
}
.panel-head-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.head-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-light);
  padding: 4px 5px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  transition: background 0.12s, color 0.12s;
}
.head-btn:hover { background: var(--bg); color: var(--text-muted); }

.new-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}
.new-btn:hover { opacity: 0.82; }
.new-btn:disabled { opacity: 0.4; cursor: not-allowed; }
:global([data-theme="dark"]) .new-btn { background: #F7F9F9; color: #15202B; }

/* ── Search ── */
.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  padding: 10px 10px 8px;
  flex-shrink: 0;
}
.search-icon {
  position: absolute;
  left: 20px;
  color: var(--text-light);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 8px 28px 8px 32px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-full);
  font-size: 12.5px;
  font-family: inherit;
  background: var(--bg);
  color: var(--text);
  transition: border-color 0.15s;
}
.search-input:focus { outline: none; border-color: var(--border-strong); }
.search-input::placeholder { color: var(--text-light); }
.search-clear {
  position: absolute;
  right: 18px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 15px;
  color: var(--text-light);
  line-height: 1;
  padding: 2px 3px;
}
.search-clear:hover { color: var(--text-muted); }

/* ── Conversation list ── */
.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 6px 8px;
}
.conv-list::-webkit-scrollbar { width: 4px; }
.conv-list::-webkit-scrollbar-track { background: transparent; }
.conv-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

.conv-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 16px;
  text-align: center;
  color: var(--text-light);
}
.conv-empty p { font-size: 13px; color: var(--text-muted); margin: 0; }

.conv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  border-radius: 9px;
  cursor: pointer;
  transition: background 0.1s;
  margin-bottom: 1px;
}
.conv-item:hover { background: var(--bg); }
.conv-item.active { background: var(--bg); border: 1px solid var(--border-strong); }

.conv-body { flex: 1; min-width: 0; }
.conv-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
  letter-spacing: -0.1px;
}
.conv-item.active .conv-title { color: var(--text); }
.conv-sub { font-size: 11px; color: var(--text-light); }

.conv-del {
  flex-shrink: 0;
  width: 24px; height: 24px;
  background: none; border: none;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-light);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.1s, background 0.1s, color 0.1s;
}
.conv-item:hover .conv-del { opacity: 1; }
.conv-del:hover { background: var(--danger-bg); color: var(--danger); }

/* ── Skeleton ── */
.sk-item {
  padding: 9px 10px;
  border-radius: 9px;
  display: flex; flex-direction: column; gap: 6px;
  margin-bottom: 2px;
}
@keyframes shimmer {
  0%   { background-position: -300px 0; }
  100% { background-position:  300px 0; }
}
.sk-line {
  background: linear-gradient(90deg, var(--bg) 25%, var(--border) 50%, var(--bg) 75%);
  background-size: 300px 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: 4px;
}
.sk-title { height: 12px; width: 78%; }
.sk-sub   { height: 10px; width: 42%; }
</style>
