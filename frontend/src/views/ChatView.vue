<template>
  <div class="chat-view">
    <div class="chat-layout">
      <aside class="chat-sidebar">
        <div class="chat-sidebar-header">
          <h2>Conversations</h2>
          <button class="btn btn-sm btn-primary" @click="handleNewConversation" :disabled="chatStore.streaming">+ New</button>
        </div>
        <div v-if="chatStore.loading" class="loading">Loading...</div>
        <div v-else class="chat-conversations">
          <div
            v-for="conv in chatStore.conversations"
            :key="conv.id"
            class="chat-conv-item"
            :class="{ active: chatStore.current?.id === conv.id }"
            @click="selectConversation(conv.id)"
          >
            <div class="conv-title">{{ conv.title || 'Untitled' }}</div>
            <div class="conv-date">{{ formatDate(conv.updated_at) }}</div>
          </div>
          <div v-if="chatStore.conversations.length === 0" class="empty">No conversations yet.</div>
        </div>
      </aside>

      <main class="chat-main">
        <template v-if="chatStore.current">
          <div class="chat-messages" ref="messagesRef">
            <div v-if="chatStore.current.messages.length === 0" class="chat-welcome">
              <h3>{{ chatStore.current.title }}</h3>
              <p>Ask me anything about your workspaces, projects, or tasks.</p>
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
            <textarea
              v-model="input"
              placeholder="Message mogul AI…"
              rows="2"
              @keydown.enter.exact.prevent="handleSend"
              :disabled="chatStore.streaming"
            ></textarea>
            <button class="btn btn-primary" @click="handleSend" :disabled="chatStore.streaming || !input.trim()">
              {{ chatStore.streaming ? '…' : 'Send' }}
            </button>
          </div>
        </template>

        <div v-else class="chat-empty-state">
          <div class="chat-empty-inner">
            <h2>AI Chat</h2>
            <p>Select a conversation or start a new one.</p>
            <button class="btn btn-primary" @click="handleNewConversation">Start new chat</button>
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
const messagesRef = ref<HTMLElement | null>(null)

onMounted(() => chatStore.fetchConversations())

watch(() => chatStore.current?.messages.length, async () => { await nextTick(); scrollToBottom() })
watch(() => chatStore.streamContent, async () => { await nextTick(); scrollToBottom() })

function scrollToBottom() {
  if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
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
  height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
}

.chat-layout {
  display: flex;
  height: 100%;
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.chat-sidebar {
  width: 248px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  background: #fafafa;
}

.chat-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
}

.chat-sidebar-header h2 {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.7px;
}

.chat-conversations {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-conv-item {
  padding: 9px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-bottom: 1px;
  transition: background 0.1s;
}

.chat-conv-item:hover { background: #ececec; }
.chat-conv-item.active { background: var(--primary-light); }

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

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 28px 40px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 20px;
  gap: 8px;
}

.chat-welcome h3 { font-size: 16px; font-weight: 600; color: var(--text); }
.chat-welcome p  { color: var(--text-muted); font-size: 14px; }

.chat-empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-empty-inner { text-align: center; }

.chat-empty-inner h2 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 10px;
  letter-spacing: -0.4px;
}

.chat-empty-inner p { color: var(--text-muted); margin-bottom: 20px; }

.chat-input-bar {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 14px 24px;
  border-top: 1px solid var(--border);
  background: #fafafa;
}

.chat-input-bar textarea {
  flex: 1;
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius);
  font-size: 14px;
  font-family: inherit;
  resize: none;
  background: var(--surface);
  transition: border-color 0.15s, box-shadow 0.15s;
  line-height: 1.5;
}

.chat-input-bar textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-muted);
}
</style>
