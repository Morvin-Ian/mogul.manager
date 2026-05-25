<template>
  <div class="chat-view">
    <div class="chat-layout">
      <!-- Conversations sidebar -->
      <aside class="chat-sidebar">
        <div class="chat-sidebar-header">
          <h2>Conversations</h2>
          <div class="sidebar-header-actions">
            <button
              v-if="chatStore.conversations.length > 0"
              class="btn btn-sm btn-ghost icon-btn"
              @click="handleClearAll"
              :disabled="chatStore.streaming"
              title="Clear all conversations"
            >
              <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
                <path d="M2 3.5h10M5.5 3.5V2.5a1 1 0 011-1h1a1 1 0 011 1v1M5.5 6v4M8.5 6v4M3 3.5l.7 7a1 1 0 001 .9h4.6a1 1 0 001-.9l.7-7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="btn btn-sm btn-primary new-chat-btn" @click="handleNewConversation" :disabled="chatStore.streaming">
              <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
              New
            </button>
          </div>
        </div>

        <div v-if="chatStore.loading" class="sk-convs">
          <div v-for="n in 5" :key="n" class="sk-conv-item">
            <div class="sk-line sk-conv-title"></div>
            <div class="sk-line sk-conv-date"></div>
          </div>
        </div>

        <div v-else class="chat-conversations">
          <div v-if="chatStore.conversations.length === 0" class="conv-empty">
            No conversations yet
          </div>
          <div
            v-for="conv in chatStore.conversations"
            :key="conv.id"
            class="chat-conv-item"
            :class="{ active: chatStore.current?.id === conv.id }"
            @click="selectConversation(conv.id)"
          >
            <div class="conv-info">
              <div class="conv-title">{{ cleanTitle(conv.title) }}</div>
              <div class="conv-date">{{ formatDate(conv.updated_at) }}</div>
            </div>
            <button
              class="conv-delete-btn"
              @click.stop="handleDeleteConv(conv.id)"
              title="Delete conversation"
            >
              <svg viewBox="0 0 12 12" fill="none" width="12" height="12">
                <path d="M1.5 3h9M4.5 3V2a.5.5 0 01.5-.5h1a.5.5 0 01.5.5v1M3 3l.5 6.5a.5.5 0 00.5.5h4a.5.5 0 00.5-.5L9 3" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </aside>

      <!-- Main chat area -->
      <main class="chat-main">
        <template v-if="chatStore.current">
          <div class="chat-messages" ref="messagesRef">
            <div v-if="chatStore.current.messages.length === 0" class="chat-welcome">
              <div class="chat-welcome-icon">
                <svg viewBox="0 0 24 24" fill="none" width="28" height="28">
                  <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12a9.956 9.956 0 004.226 8.147L4 21l3.015-1.5A9.992 9.992 0 0012 22c5.523 0 10-4.477 10-10S17.523 2 12 2zM8 11h8v2H8v-2zm0-4h5v2H8V7z" fill="currentColor"/>
                </svg>
              </div>
              <h3>{{ chatStore.current.title || 'New conversation' }}</h3>
              <p>Ask me anything about your workspaces, projects, or tasks. I can help you analyze progress, suggest priorities, and provide insights.</p>
              <div class="quick-prompts">
                <button class="quick-prompt" @click="quickSend('What projects need my attention?')">What projects need attention?</button>
                <button class="quick-prompt" @click="quickSend('Summarize my overdue tasks')">Summarize overdue tasks</button>
                <button class="quick-prompt" @click="quickSend('What should I work on next?')">What should I work on next?</button>
              </div>

              <div class="personalize-section">
                <div class="personalize-header">
                  <p class="personalize-label">
                    <svg viewBox="0 0 14 14" fill="none" width="13" height="13"><path d="M7 1.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM7 4v3.5l2 1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    The more context you share, the smarter I get
                  </p>
                  <span class="personalize-hint">Select one or more</span>
                </div>
                <div class="personalize-tips">
                  <button
                    v-for="tip in personalizeTips"
                    :key="tip.text"
                    class="personalize-tip"
                    :class="{ selected: selectedTips.has(tip.text) }"
                    @click="toggleTip(tip.text)"
                  >
                    <span class="tip-tag" :class="`tip-tag--${tip.kind}`">{{ tip.label }}</span>
                    <span class="tip-text">{{ tip.text }}</span>
                    <span class="tip-check">
                      <svg viewBox="0 0 12 12" fill="none" width="11" height="11">
                        <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </span>
                  </button>
                </div>
                <div v-if="selectedTips.size > 0" class="personalize-actions">
                  <span class="selection-count">{{ selectedTips.size }} selected</span>
                  <button class="btn btn-ghost btn-sm" @click="selectedTips.clear()">Clear</button>
                  <button class="btn btn-primary btn-sm" @click="sendSelectedTips">
                    <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                      <path d="M2 7l10-5-5 10V8L2 7z" fill="currentColor"/>
                    </svg>
                    Send {{ selectedTips.size > 1 ? `${selectedTips.size} preferences` : 'preference' }}
                  </button>
                </div>
              </div>
            </div>
            <MessageBubble
              v-for="msg in chatStore.current.messages"
              :key="msg.id || msg.content"
              :role="msg.role"
              :content="msg.content"
              :created-at="msg.created_at"
            />
            <div v-if="chatStore.streaming && chatStore.toolActivity" class="tool-activity">
              <span class="tool-activity-dot"></span>
              Running {{ formatToolName(chatStore.toolActivity) }}…
            </div>
            <MessageBubble
              v-if="chatStore.streaming && (chatStore.streamContent || !chatStore.toolActivity)"
              role="assistant"
              :content="chatStore.streamContent"
              :streaming="true"
            />
          </div>

          <div class="chat-input-bar">
            <div class="chat-input-wrap" :class="{ focused: inputFocused, disabled: chatStore.streaming }">
              <textarea
                v-model="input"
                :placeholder="currentPlaceholder"
                rows="1"
                @keydown.enter.exact.prevent="handleSend"
                @focus="inputFocused = true"
                @blur="inputFocused = false"
                @input="autoResize"
                ref="textareaRef"
                :disabled="chatStore.streaming"
              ></textarea>
              <button
                class="send-btn"
                @click="handleSend"
                :disabled="chatStore.streaming || !input.trim()"
              >
                <svg v-if="!chatStore.streaming" viewBox="0 0 16 16" fill="none" width="16" height="16">
                  <path d="M2 8l12-6-6 12V9L2 8z" fill="currentColor"/>
                </svg>
                <span v-else class="streaming-dot"></span>
              </button>
            </div>
            <p class="input-hint">Press Enter to send · Shift+Enter for new line</p>
          </div>
        </template>

        <div v-else class="chat-empty-state">
          <div class="empty-inner">
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" width="32" height="32">
                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.477 2 12a9.956 9.956 0 004.226 8.147L4 21l3.015-1.5A9.992 9.992 0 0012 22c5.523 0 10-4.477 10-10S17.523 2 12 2z" fill="currentColor"/>
              </svg>
            </div>
            <h2>Mogul Manager AI</h2>
            <p>Your intelligent project assistant. Select a conversation or start a new one.</p>
            <button class="btn btn-primary" @click="handleNewConversation">
              <svg viewBox="0 0 14 14" fill="none" width="13" height="13">
                <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
              Start new chat
            </button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import MessageBubble from '../components/chat/MessageBubble.vue'

const chatStore = useChatStore()
const input = ref('')
const inputFocused = ref(false)
const messagesRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

// ── Personalize tips ────────────────────────────────────────────
const personalizeTips = [
  { kind: 'style', label: 'Style',    text: "I prefer my task descriptions to be short and action-focused" },
  { kind: 'goal',  label: 'Goal',     text: "My main goal this month is to ship the v2 release" },
  { kind: 'style', label: 'Style',    text: "Always show me the highest priority tasks first" },
  { kind: 'work',  label: 'Workflow', text: "I work in two-week sprints and review goals every Friday" },
  { kind: 'goal',  label: 'Goal',     text: "I want to clear my backlog before taking on new projects" },
  { kind: 'work',  label: 'Workflow', text: "I've decided to keep all design work in one dedicated project" },
]

const selectedTips = ref(new Set<string>())

function toggleTip(text: string) {
  if (selectedTips.value.has(text)) {
    selectedTips.value.delete(text)
  } else {
    selectedTips.value.add(text)
  }
  // Trigger reactivity on Set mutation
  selectedTips.value = new Set(selectedTips.value)
}

async function sendSelectedTips() {
  if (!selectedTips.value.size || chatStore.streaming || !chatStore.current) return
  const combined = [...selectedTips.value].join('\n')
  selectedTips.value = new Set()
  await chatStore.sendMessage(chatStore.current.id, combined)
}

// ── Rotating input placeholder ─────────────────────────────────
const placeholders = [
  "Message Mogul Manager AI…",
  "Try: \"I prefer tasks grouped by deadline\"",
  "Try: \"My goal this week is…\"",
  "Try: \"Always remind me about blocked tasks first\"",
  "Try: \"I've decided to pause the mobile project\"",
  "Try: \"Show me everything due this week\"",
]
const placeholderIndex = ref(0)
const currentPlaceholder = computed(() => placeholders[placeholderIndex.value])
let placeholderTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  chatStore.fetchConversations()
  placeholderTimer = setInterval(() => {
    if (!inputFocused.value && !input.value) {
      placeholderIndex.value = (placeholderIndex.value + 1) % placeholders.length
    }
  }, 3500)
})

onUnmounted(() => {
  if (placeholderTimer) clearInterval(placeholderTimer)
})

watch(() => chatStore.current?.messages.length, async () => { await nextTick(); scrollToBottom() })
watch(() => chatStore.streamContent, async () => { await nextTick(); scrollToBottom() })

function scrollToBottom() {
  if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
}

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

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

async function selectConversation(id: number) {
  try { await chatStore.fetchConversation(id) } catch {}
}

async function handleNewConversation() {
  try {
    const conv = await chatStore.createConversation()
    await chatStore.fetchConversation(conv.id)
  } catch {}
}

async function handleDeleteConv(id: number) {
  try { await chatStore.removeConversation(id) } catch {}
}

async function handleClearAll() {
  if (!confirm('Delete all conversations? This cannot be undone.')) return
  const ids = chatStore.conversations.map(c => c.id)
  for (const id of ids) {
    try { await chatStore.removeConversation(id) } catch {}
  }
}

async function handleSend() {
  const text = input.value.trim()
  if (!text || chatStore.streaming || !chatStore.current) return
  input.value = ''
  if (textareaRef.value) textareaRef.value.style.height = 'auto'
  await chatStore.sendMessage(chatStore.current.id, text)
}

async function quickSend(text: string) {
  if (chatStore.streaming || !chatStore.current) return
  await chatStore.sendMessage(chatStore.current.id, text)
}

function formatToolName(name: string) {
  return name.replace(/_/g, ' ')
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
.chat-view {
  height: calc(100vh - 58px);
  display: flex;
  flex-direction: column;
  padding: 0;
}

.chat-layout {
  display: flex;
  height: 100%;
  overflow: hidden;
}

/* Sidebar */
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
.chat-conv-item.active { background: var(--primary-light); }

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

.chat-conv-item.active .conv-title { color: var(--primary); font-weight: 600; }
.conv-date { font-size: 11px; color: var(--text-light); margin-top: 2px; }

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

/* Main */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 820px;
  width: 100%;
  margin: 0 auto;
}

/* Welcome state */
.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 56px 20px 40px;
  gap: 14px;
  text-align: center;
}

.chat-welcome-icon {
  width: 58px;
  height: 58px;
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 4px;
  box-shadow: 0 8px 24px rgba(0, 82, 255, 0.3);
}

.chat-welcome h3 {
  font-size: 20px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
}

.chat-welcome p {
  color: var(--text-muted);
  font-size: 14px;
  max-width: 380px;
  line-height: 1.65;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 6px;
}

.quick-prompt {
  padding: 8px 16px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s;
  letter-spacing: -0.1px;
}

.quick-prompt:hover {
  border-color: var(--primary-border);
  background: var(--primary-light);
  color: var(--primary);
}

/* ── Personalize section ── */
.personalize-section {
  margin-top: 28px;
  width: 100%;
  max-width: 560px;
  border-top: 1px solid var(--border);
  padding-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.personalize-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.personalize-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.personalize-hint {
  font-size: 11.5px;
  color: var(--text-light);
  font-style: italic;
  flex-shrink: 0;
}

.personalize-tips {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.personalize-tip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: border-color 0.14s, background 0.14s, box-shadow 0.14s;
  position: relative;
}

.personalize-tip:hover {
  border-color: var(--primary-border);
  background: var(--primary-light);
  box-shadow: 0 2px 8px rgba(0, 82, 255, 0.08);
}

.personalize-tip.selected {
  border-color: var(--primary);
  background: var(--primary-light);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.tip-tag {
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  border: 1px solid;
  white-space: nowrap;
}

.tip-tag--style {
  background: #EBF0FF;
  color: #0039B3;
  border-color: var(--primary-border);
}

.tip-tag--goal {
  background: #ECFDF5;
  color: #047857;
  border-color: #A7F3D0;
}

.tip-tag--work {
  background: #FFFBEB;
  color: #92400E;
  border-color: #FDE68A;
}

.tip-text {
  flex: 1;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.4;
  letter-spacing: -0.1px;
}

.personalize-tip:hover .tip-text,
.personalize-tip.selected .tip-text {
  color: var(--primary);
}

.tip-check {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1.5px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: transparent;
  background: var(--surface);
  transition: all 0.14s;
}

.personalize-tip.selected .tip-check {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

.personalize-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 4px;
  animation: fade-up 0.18s ease;
}

.selection-count {
  flex: 1;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--primary);
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Empty state */
.chat-empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.empty-inner {
  text-align: center;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  width: 64px;
  height: 64px;
  background: var(--primary);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.empty-inner h2 {
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.4px;
}

.empty-inner p {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.6;
}

/* Input bar */
.chat-input-bar {
  padding: 16px 32px 24px;
  background: var(--bg);
  max-width: 820px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 0;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.chat-input-wrap.disabled {
  background: var(--bg);
}

.chat-input-wrap.focused {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}

.chat-input-wrap textarea {
  flex: 1;
  padding: 13px 16px;
  border: none;
  background: transparent;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  color: var(--text);
  line-height: 1.5;
  max-height: 140px;
  overflow-y: auto;
}

.chat-input-wrap textarea:focus { outline: none; }
.chat-input-wrap textarea::placeholder { color: var(--text-light); }
.chat-input-wrap textarea:disabled { opacity: 0.6; }

.send-btn {
  width: 40px;
  height: 40px;
  margin: 10px 10px 10px 4px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary) 0%, #003CBF 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;
  align-self: flex-end;
  box-shadow: 0 2px 8px rgba(0, 82, 255, 0.3);
}

.send-btn:hover:not(:disabled) { background: var(--primary-hover); }
.send-btn:active:not(:disabled) { transform: scale(0.96); }
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.streaming-dot {
  width: 8px;
  height: 8px;
  background: #fff;
  border-radius: 50%;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(0.75); }
}

.input-hint {
  font-size: 11.5px;
  color: var(--text-light);
  text-align: center;
}

.tool-activity {
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  color: var(--text-muted);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 7px 12px;
}

.tool-activity-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--primary);
  animation: pulse 1s ease-in-out infinite;
  flex-shrink: 0;
}

/* Sidebar skeleton */
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
