<template>
  <Teleport to="body">
    <Transition name="fab-slide">
      <div v-if="!isOnChat" class="ai-fab-wrap">
        <!-- Mini overlay -->
        <Transition name="fab-pop">
          <div v-if="open" class="ai-fab-overlay" @click.self="open = false">
            <div class="ai-fab-panel">
              <div class="fab-panel-header">
                <span class="fab-logo">mogul<span class="fab-dot">.</span>manager</span>
                <button class="fab-close" @click="open = false">
                  <font-awesome-icon :icon="['fas', 'xmark']" />
                </button>
              </div>
              <p class="fab-hint">What do you need?</p>
              <div class="fab-input-row">
                <input
                  ref="fabInputRef"
                  v-model="fabQuery"
                  class="fab-input"
                  placeholder="Ask anything about your work…"
                  @keydown.enter="sendQuery"
                  @keydown.esc="open = false"
                />
                <button class="fab-send" :disabled="!fabQuery.trim()" @click="sendQuery">
                  <font-awesome-icon :icon="['fas', 'arrow-right']" />
                </button>
              </div>
              <div class="fab-prompts">
                <button
                  v-for="p in contextPrompts"
                  :key="p"
                  class="fab-prompt-chip"
                  @click="usePrompt(p)"
                >{{ p }}</button>
              </div>
              <button class="fab-open-chat" @click="goToChat">
                <font-awesome-icon :icon="['fas', 'comments']" />
                Open full chat
              </button>
            </div>
          </div>
        </Transition>

        <!-- The button itself -->
        <button class="ai-fab" :class="{ 'ai-fab--open': open }" @click="toggle" :title="open ? 'Close' : 'Ask AI'">
          <font-awesome-icon v-if="open" :icon="['fas', 'xmark']" />
          <template v-else>
            <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" class="fab-icon" />
            <span class="fab-label">Ask AI</span>
          </template>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '../../stores/chat'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

const open = ref(false)
const fabQuery = ref('')
const fabInputRef = ref<HTMLInputElement | null>(null)

const isOnChat = computed(() => route.path.startsWith('/chat'))

const ROUTE_PROMPTS: Record<string, string[]> = {
  '/workspaces': ['Show me all my projects and their status', 'What tasks are overdue?', 'Create a new workspace for me'],
  '/projects': ['List all active projects', 'Which project has the most pending tasks?', 'Create a project and add tasks to it'],
  '/plans': ['Create a plan for my current project', 'Show me all active plans', 'What are the next steps in my plans?'],
  '/documents': ['Summarize my uploaded documents', 'Search my docs for information on', 'What documents do I have ready?'],
  '/review': ['What tasks are in review right now?', 'Approve all my reviewed tasks', 'Who submitted the most tasks for review?'],
}

const DEFAULT_PROMPTS = [
  'What should I work on today?',
  'Create tasks for my project',
  'Summarize what\'s overdue across all workspaces',
  'Make a plan for launching our product',
]

const contextPrompts = computed(() => {
  const base = route.path.replace(/\/[a-f0-9-]{36}.*$/, '') // strip UUID
  return ROUTE_PROMPTS[base] ?? DEFAULT_PROMPTS
})

function toggle() {
  open.value = !open.value
  if (open.value) {
    nextTick(() => fabInputRef.value?.focus())
  }
}

async function sendQuery() {
  if (!fabQuery.value.trim()) return
  const query = fabQuery.value.trim()
  fabQuery.value = ''
  open.value = false
  await navigateToChat(query)
}

async function usePrompt(p: string) {
  open.value = false
  await navigateToChat(p)
}

async function navigateToChat(query: string) {
  // Set BEFORE push — onMounted in ChatView reads it; watch handles already-mounted case
  chatStore.pendingMessage = query
  await router.push('/chat')
}

async function goToChat() {
  open.value = false
  await router.push('/chat')
}
</script>

<style scoped>
.ai-fab-wrap {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 900;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

/* The FAB button */
.ai-fab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #1c1c1e;
  color: #fff;
  border: none;
  border-radius: var(--radius-full);
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  box-shadow: 0 4px 20px rgba(10,11,13,0.28), 0 1px 6px rgba(10,11,13,0.18);
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
  white-space: nowrap;
}
.ai-fab:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(10,11,13,0.35); }
.ai-fab:active { transform: scale(0.97); }
.ai-fab--open { background: #3a3a3c; }
.fab-icon { font-size: 13px; }
.fab-label { letter-spacing: -0.2px; }

/* Dark mode FAB */
:global([data-theme="dark"]) .ai-fab { background: #F7F9F9; color: #15202B; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
:global([data-theme="dark"]) .ai-fab:hover { box-shadow: 0 8px 28px rgba(0,0,0,0.6); }

/* Panel */
.ai-fab-overlay {
  position: fixed;
  inset: 0;
  z-index: 899;
}
.ai-fab-panel {
  position: fixed;
  bottom: 78px;
  right: 28px;
  width: 340px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 20px;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.fab-panel-header { display: flex; align-items: center; justify-content: space-between; }
.fab-logo { font-size: 20px; font-weight: 700; color: var(--text); letter-spacing: -0.8px; line-height: 1; }
.fab-dot { color: var(--primary); }
.fab-close { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 14px; padding: 2px; }
.fab-close:hover { color: var(--text); }
.fab-hint { font-size: 13px; color: var(--text-muted); margin: 0; }

.fab-input-row { display: flex; gap: 6px; }
.fab-input {
  flex: 1; padding: 9px 12px; border: 1.5px solid var(--border);
  border-radius: var(--radius-sm); font-size: 13.5px; font-family: inherit;
  background: var(--bg); color: var(--text); outline: none;
  transition: border-color 0.15s;
}
.fab-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-muted); }
.fab-send {
  width: 36px; height: 36px; border-radius: var(--radius-sm);
  background: #1c1c1e; color: #fff; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: opacity 0.14s; flex-shrink: 0;
}
.fab-send:disabled { opacity: 0.35; cursor: not-allowed; }
.fab-send:not(:disabled):hover { opacity: 0.82; }
:global([data-theme="dark"]) .fab-send { background: #F7F9F9; color: #15202B; }

.fab-prompts { display: flex; flex-direction: column; gap: 5px; }
.fab-prompt-chip {
  text-align: left; background: var(--bg); border: 1.5px solid var(--border);
  border-radius: var(--radius-sm); padding: 7px 11px;
  font-size: 12.5px; color: var(--text-muted); cursor: pointer;
  font-family: inherit; transition: border-color 0.13s, color 0.13s, background 0.13s;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.fab-prompt-chip:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }

.fab-open-chat {
  display: inline-flex; align-items: center; gap: 7px;
  background: none; border: none; color: var(--text-muted);
  font-size: 12.5px; font-weight: 600; cursor: pointer; font-family: inherit;
  padding: 4px 0; align-self: flex-start;
  transition: color 0.13s;
}
.fab-open-chat:hover { color: var(--primary); }

/* Transitions */
.fab-slide-enter-active, .fab-slide-leave-active { transition: opacity 0.2s, transform 0.2s; }
.fab-slide-enter-from, .fab-slide-leave-to { opacity: 0; transform: translateY(12px); }
.fab-pop-enter-active  { transition: opacity 0.18s, transform 0.18s cubic-bezier(0.34,1.2,0.64,1); }
.fab-pop-leave-active  { transition: opacity 0.14s; }
.fab-pop-enter-from    { opacity: 0; transform: scale(0.92) translateY(8px); }
.fab-pop-leave-to      { opacity: 0; }
</style>
