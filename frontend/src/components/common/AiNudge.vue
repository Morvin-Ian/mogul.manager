<template>
  <Transition name="nudge-slide">
    <div v-if="visible" class="ai-nudge">
      <div class="nudge-left">
        <span class="nudge-icon">
          <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" />
        </span>
        <div class="nudge-body">
          <p class="nudge-label">{{ label }}</p>
          <div class="nudge-chips">
            <button
              v-for="p in prompts"
              :key="p"
              class="nudge-chip"
              @click="fire(p)"
            >{{ p }}</button>
          </div>
        </div>
      </div>
      <button class="nudge-close" title="Dismiss" @click="dismiss">
        <font-awesome-icon :icon="['fas', 'xmark']" />
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '../../stores/chat'

const props = defineProps<{
  storageKey: string          // unique key so each page remembers dismissal
  label: string               // "AI can help here" headline
  prompts: string[]           // 2-4 clickable prompt chips
}>()

const router = useRouter()
const chatStore = useChatStore()
const visible = ref(false)

onMounted(() => {
  visible.value = localStorage.getItem(`nudge_dismissed_${props.storageKey}`) !== '1'
})

function dismiss() {
  visible.value = false
  localStorage.setItem(`nudge_dismissed_${props.storageKey}`, '1')
}

async function fire(prompt: string) {
  dismiss()
  chatStore.pendingMessage = prompt  // set before push
  await router.push('/chat')
}
</script>

<style scoped>
.ai-nudge {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  background: var(--primary-light);
  border: 1.5px solid var(--primary-border);
  border-radius: var(--radius-lg);
  padding: 13px 16px;
  margin-bottom: 24px;
}

.nudge-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.nudge-icon {
  width: 30px;
  height: 30px;
  background: var(--primary);
  color: #fff;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
  margin-top: 1px;
}

.nudge-body {
  flex: 1;
  min-width: 0;
}

.nudge-label {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 8px;
  letter-spacing: -0.1px;
}

.nudge-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.nudge-chip {
  background: #fff;
  border: 1.5px solid var(--primary-border);
  border-radius: var(--radius-full);
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--primary);
  cursor: pointer;
  font-family: inherit;
  transition: background 0.13s, color 0.13s, border-color 0.13s;
  white-space: nowrap;
}
.nudge-chip:hover {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}

.nudge-close {
  background: none;
  border: none;
  color: var(--primary);
  opacity: 0.55;
  cursor: pointer;
  font-size: 13px;
  padding: 2px 4px;
  flex-shrink: 0;
  transition: opacity 0.13s;
  line-height: 1;
}
.nudge-close:hover { opacity: 1; }

/* Dark mode */
:global([data-theme="dark"]) .ai-nudge {
  background: rgba(91,155,255,0.1) !important;
  border-color: rgba(91,155,255,0.3) !important;
}
:global([data-theme="dark"]) .nudge-chip {
  background: rgba(91,155,255,0.12) !important;
  border-color: rgba(91,155,255,0.3) !important;
  color: #5B9BFF !important;
}
:global([data-theme="dark"]) .nudge-chip:hover {
  background: #5B9BFF !important;
  color: #fff !important;
}

/* Transition */
.nudge-slide-enter-active { transition: opacity 0.25s, transform 0.25s; }
.nudge-slide-leave-active  { transition: opacity 0.18s, transform 0.18s; }
.nudge-slide-enter-from    { opacity: 0; transform: translateY(-8px); }
.nudge-slide-leave-to      { opacity: 0; transform: translateY(-6px); }
</style>
