<template>
  <div class="chat-view">
    <div class="chat-layout">
      <aside class="chat-sidebar">
        <div class="chat-sidebar-header">
          <h2>Chat</h2>
          <button class="btn btn-sm btn-primary" @click="handleNewConversation" :disabled="chatStore.streaming">
            + New
          </button>
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
              placeholder="Type a message..."
              rows="2"
              @keydown.enter.prevent="handleSend"
              :disabled="chatStore.streaming"
            ></textarea>
            <button
              class="btn btn-primary"
              @click="handleSend"
              :disabled="chatStore.streaming || !input.trim()"
            >
              {{ chatStore.streaming ? 'Sending...' : 'Send' }}
            </button>
          </div>
        </template>

        <div v-else class="chat-empty-state">
          <div class="chat-empty-inner">
            <h2>AI Chat</h2>
            <p>Select a conversation or start a new one.</p>
            <button class="btn btn-primary" @click="handleNewConversation">Start New Chat</button>
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

onMounted(() => {
  chatStore.fetchConversations()
})

watch(
  () => chatStore.current?.messages.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

watch(
  () => chatStore.streamContent,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

async function selectConversation(id: number) {
  try {
    await chatStore.fetchConversation(id)
  } catch {
    // handled by store
  }
}

async function handleNewConversation() {
  try {
    const conv = await chatStore.createConversation()
    await chatStore.fetchConversation(conv.id)
  } catch {
    // handled by store
  }
}

async function handleSend() {
  const text = input.value.trim()
  if (!text || chatStore.streaming || !chatStore.current) return
  input.value = ''
  await chatStore.sendMessage(chatStore.current.id, text)
}

function formatDate(d: string) {
  const date = new Date(d)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}
</script>
