<template>
  <div class="chat-view">
    <div class="chat-layout">
      <ChatConversations
        :conversations="chatStore.conversations"
        :loading="chatStore.loading"
        :streaming="chatStore.streaming"
        :current-id="chatStore.current?.id ?? null"
        @select="selectConversation"
        @new="handleNewConversation"
        @delete="handleDeleteConv"
        @clear="handleClearAll"
      />

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
            <Transition name="thinking-fade">
              <div
                v-if="chatStore.streaming && !chatStore.streamContent && !chatStore.toolActivity"
                class="thinking-status"
                :key="chatStore.thinkingStatus"
              >
                <span class="thinking-dot"></span>
                <span class="thinking-text">{{ chatStore.thinkingStatus }}</span>
              </div>
            </Transition>
            <Transition name="thinking-fade">
              <div v-if="chatStore.streaming && chatStore.toolActivity" class="tool-activity">
                <span class="tool-activity-dot"></span>
                Running {{ formatToolName(chatStore.toolActivity) }}…
              </div>
            </Transition>
            <MessageBubble
              v-if="chatStore.streaming && chatStore.streamContent"
              role="assistant"
              :content="chatStore.streamContent"
              :streaming="true"
            />
          </div>

          <ChatInput
            v-model="input"
            :streaming="chatStore.streaming"
            :placeholder="currentPlaceholder"
            @send="handleSend"
          />
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
import { useConfirm } from '../composables/useConfirm'
import MessageBubble from '../components/chat/MessageBubble.vue'
import ChatConversations from '../components/chat/ChatConversations.vue'
import ChatInput from '../components/chat/ChatInput.vue'

const chatStore = useChatStore()
const { confirm } = useConfirm()
const input = ref('')
const messagesRef = ref<HTMLElement | null>(null)

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
    if (!input.value) {
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
  const count = chatStore.conversations.length
  const ok = await confirm({
    title: 'Clear all conversations?',
    message: `All ${count} conversation${count !== 1 ? 's' : ''} will be permanently deleted.`,
    consequences: ['Chat history cannot be recovered after deletion'],
    confirmLabel: 'Yes, clear all',
    cancelLabel: 'Cancel',
    danger: true,
  })
  if (!ok) return
  const ids = chatStore.conversations.map(c => c.id)
  for (const id of ids) {
    try { await chatStore.removeConversation(id) } catch {}
  }
}

async function handleSend(text: string) {
  if (!text.trim() || chatStore.streaming || !chatStore.current) return
  input.value = ''
  await chatStore.sendMessage(chatStore.current.id, text.trim())
}

async function quickSend(text: string) {
  if (chatStore.streaming || !chatStore.current) return
  await chatStore.sendMessage(chatStore.current.id, text)
}

function formatToolName(name: string) {
  return name.replace(/_/g, ' ')
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
  background: #1c1c1e;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 4px;
  box-shadow: 0 8px 24px rgba(10, 11, 13, 0.25);
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
  border-color: #B0A8E8;
  background: #E5E2FF;
  color: #3830A0;
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
  border-color: #B0A8E8;
  background: #E5E2FF;
  box-shadow: 0 2px 8px rgba(56, 48, 160, 0.08);
}

.personalize-tip.selected {
  border-color: #3830A0;
  background: #E5E2FF;
  box-shadow: 0 0 0 3px rgba(56, 48, 160, 0.10);
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
  background: #E5E2FF;
  color: #3830A0;
  border-color: #B0A8E8;
}

.tip-tag--goal {
  background: #D8F0DC;
  color: #1A5820;
  border-color: #70C878;
}

.tip-tag--work {
  background: #F2E0CC;
  color: #7A3410;
  border-color: #CFA070;
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
  color: #3830A0;
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
  background: #1c1c1e;
  border-color: #1c1c1e;
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
  color: #3830A0;
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
  background: #1c1c1e;
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
  background: #3830A0;
  animation: pulse 1s ease-in-out infinite;
  flex-shrink: 0;
}

.thinking-status {
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

.thinking-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: thinking-bounce 1.4s ease-in-out infinite;
  flex-shrink: 0;
}

.thinking-text {
  animation: thinking-breathe 1.8s ease-in-out infinite;
}

@keyframes thinking-bounce {
  0%, 100% { transform: translateY(0);   opacity: 1; }
  50%       { transform: translateY(-3px); opacity: 0.5; }
}

@keyframes thinking-breathe {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.55; }
}

.thinking-fade-enter-active,
.thinking-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.thinking-fade-enter-from,
.thinking-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

</style>
