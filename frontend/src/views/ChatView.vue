<template>
  <div class="chat-view">
    <div class="chat-layout">
      <!-- Conversations sidebar -->
      <aside class="chat-sidebar">
        <div class="chat-sidebar-header">
          <h2>Conversations</h2>
          <button class="btn btn-sm btn-primary new-chat-btn" @click="handleNewConversation" :disabled="chatStore.streaming">
            <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
              <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            New
          </button>
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
            <div class="conv-icon">
              <svg viewBox="0 0 14 14" fill="none" width="12" height="12">
                <path fill-rule="evenodd" d="M1 7c0 3.31 2.69 6 6 6a5.94 5.94 0 003-.81L13 13l-1.19-3A5.99 5.99 0 0013 7c0-3.31-2.69-6-6-6S1 3.69 1 7z" fill="currentColor"/>
              </svg>
            </div>
            <div class="conv-info">
              <div class="conv-title">{{ conv.title || 'New conversation' }}</div>
              <div class="conv-date">{{ formatDate(conv.updated_at) }}</div>
            </div>
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
            </div>
            <MessageBubble
              v-for="msg in chatStore.current.messages"
              :key="msg.id || msg.content"
              :role="msg.role"
              :content="msg.content"
              :created-at="msg.created_at"
            />
            <MessageBubble
              v-if="chatStore.streaming"
              role="assistant"
              :content="chatStore.streamContent"
              :streaming="true"
            />
          </div>

          <div class="chat-input-bar">
            <div class="chat-input-wrap" :class="{ focused: inputFocused, disabled: chatStore.streaming }">
              <textarea
                v-model="input"
                placeholder="Message Mogul Manager AI…"
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
import { ref, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import MessageBubble from '../components/chat/MessageBubble.vue'

const chatStore = useChatStore()
const input = ref('')
const inputFocused = ref(false)
const messagesRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

onMounted(() => chatStore.fetchConversations())

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

async function selectConversation(id: number) {
  try { await chatStore.fetchConversation(id) } catch {}
}

async function handleNewConversation() {
  try {
    const conv = await chatStore.createConversation()
    await chatStore.fetchConversation(conv.id)
  } catch {}
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
  padding: 16px;
  border-bottom: 1px solid var(--border);
}

.chat-sidebar-header h2 {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
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
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.1s;
  margin-bottom: 1px;
}

.chat-conv-item:hover { background: var(--bg); }
.chat-conv-item.active { background: var(--primary-light); }

.conv-icon {
  width: 24px;
  height: 24px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--text-muted);
  margin-top: 1px;
}

.chat-conv-item.active .conv-icon {
  background: var(--primary-muted);
  border-color: var(--primary-border);
  color: var(--primary);
}

.conv-info { flex: 1; min-width: 0; }

.conv-title {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
}

.chat-conv-item.active .conv-title { color: var(--primary); font-weight: 600; }
.conv-date { font-size: 11px; color: var(--text-light); margin-top: 2px; }

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
  padding: 32px;
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
  padding: 48px 20px;
  gap: 12px;
  text-align: center;
}

.chat-welcome-icon {
  width: 56px;
  height: 56px;
  background: var(--primary);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 4px;
}

.chat-welcome h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.3px;
}

.chat-welcome p {
  color: var(--text-muted);
  font-size: 14px;
  max-width: 400px;
  line-height: 1.6;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 8px;
}

.quick-prompt {
  padding: 8px 16px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  cursor: pointer;
  font-family: inherit;
  transition: border-color 0.15s, background 0.15s;
}

.quick-prompt:hover {
  border-color: var(--primary-border);
  background: var(--primary-light);
  color: var(--primary);
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
  padding: 16px 32px 20px;
  background: var(--bg);
  max-width: 820px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chat-input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 0;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
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
  width: 44px;
  height: 44px;
  margin: 8px;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.1s;
  align-self: flex-end;
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
